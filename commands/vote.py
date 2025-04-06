import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import json

VOTE_FILE = "vote.json"

def load_votes():
    try:
        with open(VOTE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_votes(data):
    with open(VOTE_FILE, "w") as file:
        json.dump(data, file, indent=4)

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.votes = load_votes()

    def update_server_votes(self, guild_id, user_id):
        """Ajoute un vote pour un serveur donné."""
        now = datetime.utcnow().isoformat()
        guild_id = str(guild_id)
        user_id = str(user_id)

        if guild_id not in self.votes:
            self.votes[guild_id] = {"votes": 0, "last_votes": {}}

        last_votes = self.votes[guild_id]["last_votes"]

        if user_id in last_votes:
            last_vote_time = datetime.fromisoformat(last_votes[user_id])
            if datetime.utcnow() - last_vote_time < timedelta(hours=12):
                return False

        self.votes[guild_id]["votes"] += 1
        self.votes[guild_id]["last_votes"][user_id] = now
        save_votes(self.votes)
        return True

    def get_top_votes(self, bot):
        """Retourne les 10 meilleurs serveurs avec des invitations valides."""
        guilds = {str(g.id): g for g in bot.guilds}
        valid_votes = {
            guild_id: data
            for guild_id, data in self.votes.items()
            if guild_id in guilds
        }
        sorted_votes = sorted(
            valid_votes.items(),
            key=lambda x: x[1]["votes"],
            reverse=True
        )
        return sorted_votes[:10]

    @app_commands.command(name="vote", description="Votez pour ce serveur.")
    @app_commands.guild_only()
    async def vote(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild.id

        if self.update_server_votes(guild_id, user_id):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="✅ Merci pour votre vote !",
                    description="Votre vote a été pris en compte avec succès. Vous pouvez revoter dans **12 heures**.",
                    color=discord.Color.green()
                )
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="⏳ Pas si vite !",
                    description="Vous avez déjà voté pour ce serveur. Vous pourrez revoter après **12 heures**.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )

    @app_commands.command(name="topvote", description="Affiche le classement des serveurs avec le plus de votes.")
    async def topvote(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(thinking=True)
            top_servers = self.get_top_votes(self.bot)

            if not top_servers:
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="📊 Classement des votes",
                        description="Aucun serveur n'a encore de votes.",
                        color=discord.Color.orange()
                    ),
                    ephemeral=True
                )
                return

            embed = discord.Embed(
                title="🏆 Classement des votes",
                description="Voici les serveurs avec le plus de votes :",
                color=discord.Color.gold()
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)

            for i, (guild_id, data) in enumerate(top_servers, start=1):
                guild = self.bot.get_guild(int(guild_id))
                try:
                    invite = await guild.text_channels[0].create_invite(
                        max_age=0, max_uses=0, unique=False
                    )
                except Exception as e:
                    pass
                embed.add_field(
                    name=f"#{i} - {guild.name}",
                    value=f"[Lien d'invitation]({invite.url})\n**Votes** : {data['votes']}",
                    inline=False
                )

            await interaction.followup.send(embed=embed)
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Vote(bot))
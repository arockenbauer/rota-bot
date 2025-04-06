import discord
from discord.ext import commands
from discord import app_commands
import json
import time

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_file = "leaderboard_stats.json"

    def load_stats(self):
        """Charge les statistiques depuis le fichier JSON ou crée un nouveau fichier si absent."""
        try:
            with open(self.stats_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {
                "mutes": {},
                "kicks": {},
                "bans": {},
                "messages_edited": {},
                "messages_deleted": {}
            }

    def save_stats(self, stats):
        """Sauvegarde les statistiques dans le fichier JSON."""
        with open(self.stats_file, 'w') as file:
            json.dump(stats, file, indent=4)

    @app_commands.command(name="leaderboard", description="Afficher le leaderboard des actions administratives")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Ban", value="ban"),
            app_commands.Choice(name="Kick", value="kick"),
            app_commands.Choice(name="Mute", value="mute"),
            app_commands.Choice(name="Message édité", value="edited"),
            app_commands.Choice(name="Message supprimé", value="deleted")
        ]
    )
    async def leaderboard(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        """Commande Slash pour afficher le leaderboard des actions administratives."""
        await interaction.response.defer(thinking=True)
        
        stats = self.load_stats()
        embed = discord.Embed(title=f"🔍 Leaderboard des {type.name}s", color=discord.Color.blurple())

        if type.value == "ban" and stats["bans"]:
            ban_record = min(stats["bans"], key=lambda x: stats["bans"][x])
            ban_time = stats["bans"][ban_record]
            embed.add_field(name="Record de ban", value=f"{ban_record} : {ban_time} sec", inline=False)

        elif type.value == "kick" and stats["kicks"]:
            kick_record = min(stats["kicks"], key=lambda x: stats["kicks"][x])
            kick_time = stats["kicks"][kick_record]
            embed.add_field(name="Record de kick", value=f"{kick_record} : {kick_time} sec", inline=False)

        elif type.value == "mute" and stats["mutes"]:
            mute_record = min(stats["mutes"], key=lambda x: stats["mutes"][x])
            mute_time = stats["mutes"][mute_record]
            embed.add_field(name="Record de mute", value=f"{mute_record} : {mute_time} sec", inline=False)

        elif type.value == "edited" and stats["messages_edited"]:
            edited_record = min(stats["messages_edited"], key=lambda x: stats["messages_edited"][x])
            edit_time = stats["messages_edited"][edited_record]
            embed.add_field(name="Message le plus vite édité", value=f"[Lien](https://discord.com/channels/{interaction.guild.id}/{edited_record}) : {edit_time} sec", inline=False)

        elif type.value == "deleted" and stats["messages_deleted"]:
            deleted_record = min(stats["messages_deleted"], key=lambda x: stats["messages_deleted"][x])
            delete_time = stats["messages_deleted"][deleted_record]["time"]
            embed.add_field(name="Message le plus rapidement supprimé", value=f"{delete_time} sec par {deleted_record}", inline=False)
        else:
            embed.add_field(name="Aucun record", value="Aucun record trouvé pour cette catégorie", inline=False)

        await interaction.followup.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        """Met à jour les statistiques des membres lorsqu'ils sont mute/demute."""
        if not before or not after:
            return

        mute_role = discord.utils.get(after.guild.roles, name="Muted")
        if mute_role and mute_role in after.roles and mute_role not in before.roles:
            stats = self.load_stats()
            mute_time = time.time() - after.joined_at.timestamp()
            stats["mutes"][str(after.id)] = mute_time
            self.save_stats(stats)

        if mute_role and mute_role not in after.roles and mute_role in before.roles:
            stats = self.load_stats()
            if str(after.id) in stats["mutes"]:
                del stats["mutes"][str(after.id)]
                self.save_stats(stats)

    @commands.Cog.listener()
    async def on_member_kick(self, member):
        """Met à jour les statistiques lorsqu'un membre est kick."""
        stats = self.load_stats()
        kick_time = time.time() - member.joined_at.timestamp()
        stats["kicks"][str(member.id)] = kick_time
        self.save_stats(stats)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        """Met à jour les statistiques lorsqu'un membre est banni."""
        stats = self.load_stats()
        ban_time = time.time() - member.joined_at.timestamp()
        stats["bans"][str(member.id)] = ban_time
        self.save_stats(stats)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        """Met à jour les statistiques lorsqu'un message est édité."""
        if before.content != after.content:
            stats = self.load_stats()
            edit_time = time.time() - before.created_at.timestamp()
            stats["messages_edited"][str(before.id)] = edit_time
            self.save_stats(stats)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        """Met à jour les statistiques lorsqu'un message est supprimé."""
        stats = self.load_stats()
        delete_time = time.time() - message.created_at.timestamp()
        stats["messages_deleted"][str(message.id)] = {
            "time": delete_time,
            "content": message.content
        }
        self.save_stats(stats)

async def setup(bot: commands.Bot):
    await bot.add_cog(Leaderboard(bot))
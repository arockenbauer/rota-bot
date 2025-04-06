import discord
from discord.ui import Button, View
from discord.ext import commands

class GuildTracking(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.support_channel_id = 1342082524381319204
        
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        try:
            """Lorsque le bot est ajouté à un serveur."""
            if not self.support_channel_id:
                return

            support_channel = self.bot.get_channel(self.support_channel_id)
            if not support_channel:
                return

            # Calcul des statistiques globales
            total_guilds = len(self.bot.guilds)
            total_members = sum(guild.member_count for guild in self.bot.guilds)
            embed = discord.Embed(
                title="✅ Rota Bot vient d'être ajouté !",
                color=discord.Color.green(),
            )

            text_channel = next((channel for channel in guild.text_channels), None)

            embed.add_field(name="📛 Nom du serveur :", value=guild.name, inline=False)
            embed.add_field(name="👥 Nombre de membres :", value=guild.member_count, inline=False)
            embed.add_field(name="🌍", value=f"Je suis maintenant dans `{total_guilds}` serveurs !", inline=True)
            embed.add_field(name="📊 Membres totaux :", value=f"{total_members}", inline=True)

            invite = await text_channel.create_invite(max_age=0, max_uses=0, reason="Invitation générée par le bot.")
            button = Button(label="Rejoindre le serveur", url=invite.url, style=discord.ButtonStyle.link)

            view = View()
            view.add_item(button)

            if guild.icon:
                embed.set_thumbnail(url=guild.icon.url)
            embed.set_footer(text=f"ID du serveur : {guild.id}")

            await support_channel.send(embed=embed, view=view)
        
        except Exception as e:
            print(e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Lorsque le bot est retiré d'un serveur."""
        if not self.support_channel_id:
            return

        support_channel = self.bot.get_channel(self.support_channel_id)
        if not support_channel:
            return

        # Calcul des statistiques globales
        total_guilds = len(self.bot.guilds)
        total_members = sum(guild.member_count for guild in self.bot.guilds)
        embed = discord.Embed(
            title="❌ Rota Bot vient d'être retiré",
            color=discord.Color.red(),
        )

        embed.add_field(name="📛 Nom du serveur :", value=guild.name, inline=False)
        embed.add_field(name="👥", value=f"Le serveur possédait `{guild.member_count}` membres.", inline=False)
        embed.add_field(name="🌍", value=f"Je suis maintenant dans `{total_guilds}` serveurs.", inline=True)
        embed.add_field(name="📊 Membres totaux :", value=total_members, inline=True)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        embed.set_footer(text=f"ID du serveur : {guild.id}")
        await support_channel.send(embed=embed)

# Ajouter la classe au bot

async def setup(bot):
    await bot.add_cog(GuildTracking(bot))
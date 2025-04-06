import discord
from discord import app_commands
from discord.ext import commands
import datetime
import asyncio

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Configure le statut du bot lorsqu'il est prêt."""
        # Démarre la mise à jour dynamique du statut
        await self.update_status()

    async def update_status(self):
        """Met à jour dynamiquement le statut du bot toutes les 10 secondes."""
        server_count = len(self.bot.guilds)
        member_count = sum(guild.member_count for guild in self.bot.guilds)
        
        # Statut dynamique avec des infos utiles
        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"Vos serveurs"
        )
        await self.bot.change_presence(activity=activity)

    @app_commands.command(name="status", description="Affiche les informations sur le statut du bot.")
    async def status(self, interaction: discord.Interaction):
        """Affiche un embed détaillant les informations sur le bot."""
        # Récupération des informations du bot
        bot_user = self.bot.user
        bot_ping = round(self.bot.latency * 1000)  # Ping en millisecondes
        server_count = len(self.bot.guilds)  # Nombre de serveurs
        member_count = sum(guild.member_count for guild in self.bot.guilds)  # Nombre total de membres
        
        # Embed de statut
        embed = discord.Embed(
            title="Statut du bot",
            description=f"Voici les informations actuelles sur {self.bot.user.name} :",
            color=discord.Color.blurple(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=bot_user.avatar.url if bot_user.avatar else discord.Embed.Empty)
        embed.add_field(name="Nom du bot", value=bot_user.name, inline=True)
        embed.add_field(name="ID du bot", value=bot_user.id, inline=True)
        embed.add_field(name="Ping", value=f"{bot_ping} ms", inline=True)
        embed.add_field(name="Serveurs", value=f"{server_count} serveurs", inline=True)
        embed.add_field(name="Membres", value=f"{member_count} membres", inline=True)
        embed.add_field(name="Statut", value="En ligne" if self.bot.is_ready() else "Hors ligne", inline=True)
        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url)

        # Réponse
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))

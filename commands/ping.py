import discord
import asyncio
import aiohttp
import subprocess
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Teste la latence.")
    async def ping(self, interaction: discord.Interaction):
        try:
            # Indiquer à Discord que le bot réfléchit
            await interaction.response.defer(thinking=True)

            # Initialiser les résultats des pings
            results = {}

            # Ping de l'API Discord
            discord_ping = await self.ping_discord_api()
            results["API Discord"] = f"Ping : {discord_ping} ms"

            # Ping du réseau local (en l'occurrence 192.168.1.1, tu peux changer l'IP si nécessaire)
            local_ping = await self.ping_local_network()
            results["Réseau local"] = f"Ping : {local_ping} ms"

            # Ping du site externe
            site_ping = await self.ping_site("elite-rota.arockenbauer.fr")
            results["elite-rota.arockenbauer.fr"] = f"Ping : {site_ping} ms"

            # Créer un embed avec les résultats
            embed = discord.Embed(title="Résultats du Ping", color=0x3498db)
            for label, result in results.items():
                embed.add_field(name=label, value=result, inline=False)

            # Répondre à l'interaction avec l'embed
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(e)

    async def ping_discord_api(self):
        """Pinge l'API Discord."""
        try:
            return round(self.bot.latency * 1000)
        except Exception:
            return "Erreur de connexion"

    async def ping_local_network(self):
        """Pinge le réseau local."""
        try:
            result = subprocess.run(["ping", "-c", "1", "0.0.0.0"], stdout=subprocess.PIPE)
            if result.returncode == 0:
                output = result.stdout.decode()
                # Extraire le temps de ping
                ping_time = output.split("time=")[-1].split(" ")[0]
                return ping_time
            else:
                return "Inaccessible"
        except Exception:
            return "Erreur de connexion"

    async def ping_site(self, site):
        """Pinge un site externe."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{site}") as response:
                    return response.status
        except Exception:
            return "Erreur de connexion"

async def setup(bot):
    await bot.add_cog(Ping(bot))
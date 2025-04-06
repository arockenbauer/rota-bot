import discord
from discord.ext import commands
from discord import app_commands

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="serverstats", description="Affiche les statistiques simplifiées du serveur.")
    async def stats(self, interaction: discord.Interaction):
        guild = interaction.guild

        # Calcul des statistiques
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)
        in_voice_channels = sum(len(vc.members) for vc in guild.voice_channels)
        boost_count = guild.premium_subscription_count

        # Création de l'embed
        embed = discord.Embed(
            title="📊 Statistiques du Serveur",
            description=(
                f"**👥 Nombre de membres :** `{total_members}`\n"
                f"**🟢 Membres en ligne :** `{online_members}`\n"
                f"**🔊 Membres en vocal :** `{in_voice_channels}`\n"
                f"**🚀 Boosts :** `{boost_count}`"
            ),
            color=discord.Color.green()
        )

        # Ajout d'une miniature (icône du serveur, si disponible)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        # Ajout du footer avec l'utilisateur qui a exécuté la commande
        embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url)

        # Répondre à l'interaction
        await interaction.response.send_message(embed=embed)

# Fonction pour charger la commande
async def setup(bot):
    await bot.add_cog(ServerStats(bot))
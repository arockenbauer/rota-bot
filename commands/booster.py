import discord
from discord import app_commands
from discord.ext import commands

class Booster(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="boosters", description="Affiche les membres qui ont boosté le serveur")
    async def boosters(self, interaction: discord.Interaction):
        guild = interaction.guild  # Récupérer le serveur où la commande est utilisée
        boosters = [member for member in guild.members if member.premium_since]  # Récupérer les membres avec un boost

        if len(boosters) == 0:
            await interaction.response.send_message("Le serveur contient 0 boost.")
        else:
            embed = discord.Embed(title="Liste des Boosters", color=discord.Color.green())
            
            # Récupérer le total des boosts du serveur
            boost_total = guild.premium_subscription_count  # Nombre total de boosts du serveur
            embed.add_field(
                name="Total de boosts du serveur",
                value=f"{boost_total} boost(s)",  # Afficher le total des boosts
                inline=False
            )
            
            # Afficher chaque booster (sans mentionner les noms)
            for member in boosters:
                embed.add_field(
                    name=f"<@{member.id}> (`{member.id}`)",  # Mentionner l'utilisateur et afficher son ID
                    value="Boosted",  # Ajouter le texte "Boosted" pour chaque membre
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Booster(bot))
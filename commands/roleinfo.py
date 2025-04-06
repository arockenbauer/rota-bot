import discord
from discord.ext import commands
from discord import app_commands

class RoleInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="roleinfo", description="Affiche des informations sur un rôle spécifique.")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Commande qui donne des informations détaillées sur un rôle."""
        try:
            # Construction de l'embed avec les informations du rôle
            embed = discord.Embed(
                title=f"Informations sur le rôle : {role.name}",
                color=role.color
            )
            embed.add_field(name="Nom", value=role.name, inline=True)
            embed.add_field(name="ID", value=role.id, inline=True)
            embed.add_field(name="Couleur", value=str(role.color), inline=True)
            embed.add_field(name="Mentionnable", value="Oui" if role.mentionable else "Non", inline=True)
            embed.add_field(name="Nombre de membres", value=len(role.members), inline=True)
            embed.add_field(name="Position", value=role.position, inline=True)
            embed.add_field(name="Créé le", value=role.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=True)

            # Liste des membres ayant le rôle
            if role.members:
                members = ", ".join([member.mention for member in role.members[:10]])  # Limité aux 10 premiers membres
                if len(role.members) > 10:
                    members += " et d'autres..."
            else:
                members = "Aucun membre avec ce rôle."

            embed.add_field(name="Membres avec ce rôle", value=members, inline=False)

            # Envoi de l'embed
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            # Gestion des erreurs
            print(f"Erreur dans /roleinfo : {e}")
            await interaction.response.send_message(
                "❌ Une erreur est survenue lors de l'affichage des informations du rôle.", ephemeral=True
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleInfo(bot))
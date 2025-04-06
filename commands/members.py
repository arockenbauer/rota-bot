import discord
import yaml
from discord.ext import commands
from discord import app_commands

class MemberScanner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="members_stats", description="Scanne les pseudos, statuts et bios des membres du serveur.")
    @app_commands.default_permissions(administrator=True)
    async def members_stats(self, interaction: discord.Interaction):
        """Scanne les membres et génère un fichier YAML avec leurs infos."""
        await interaction.response.defer()

        members_data = {"users": []}

        for member in interaction.guild.members:
            if member.bot:  # Ignorer les bots
                continue

            # Récupération du statut personnalisé si disponible
            custom_status = None
            for activity in member.activities:
                if isinstance(activity, discord.CustomActivity):
                    custom_status = activity.name
                    break

            user_data = {
                "user_name": member.display_name,
                "user_status": custom_status or "Aucun statut",  # Si aucun statut personnalisé
            }
            members_data["users"].append(user_data)

        yaml_filename = "members_stats.yaml"

        with open(yaml_filename, "w", encoding="utf-8") as file:
            yaml.dump(members_data, file, allow_unicode=True, default_flow_style=False)

        file = discord.File(yaml_filename)

        await interaction.followup.send("📄 Voici le fichier des statistiques des membres :", file=file)

async def setup(bot: commands.Bot):
    await bot.add_cog(MemberScanner(bot))

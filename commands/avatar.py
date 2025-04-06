import discord
from discord import app_commands
from discord.ext import commands

class Avatar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Montre l'avatar d'un utilisateur.")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(thinking=True)
        # Si aucun membre n'est mentionné, afficher l'avatar de l'utilisateur ayant utilisé la commande
        if member is None:
            member = interaction.user

        # Création de l'embed pour afficher l'avatar
        embed = discord.Embed(
            title=f"Avatar de {member.display_name}",
            description=f"Voici l'avatar de {member.display_name}",
            color=discord.Color.blue()
        )
        embed.set_image(url=member.avatar.url)  # On ajoute l'image de l'avatar
        embed.set_footer(text=f"Demandé par {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Avatar(bot))
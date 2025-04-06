import discord
from discord.ext import commands
from discord import app_commands

class LockUnlock(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="lock", description="Verrouille un salon.")
    @app_commands.default_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        """Verrouille un salon pour que seuls les utilisateurs avec des permissions spécifiques puissent envoyer des messages."""
        channel = interaction.channel

        # Vérifie si le salon est déjà verrouillé
        overwrite = channel.overwrites_for(interaction.guild.default_role)
        if overwrite.send_messages is False:
            await interaction.response.send_message(f"🔒 Le salon <#{channel.id}> est déjà verrouillé.", ephemeral=True)
            return

        # Modifie les permissions pour verrouiller le salon
        overwrite.send_messages = False
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(f"🔒 Le salon <#{channel.id}> a bien été verrouillé.")

    @app_commands.command(name="unlock", description="Déverrouille un salon.")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        """Déverrouille un salon pour permettre à tout le monde d'envoyer des messages."""
        channel = interaction.channel

        # Vérifie si le salon est déjà déverrouillé
        overwrite = channel.overwrites_for(interaction.guild.default_role)
        if overwrite.send_messages is None or overwrite.send_messages is True:
            await interaction.response.send_message(f"🔓 Le salon <#{channel.id}> est déjà déverrouillé.", ephemeral=True)
            return

        # Modifie les permissions pour déverrouiller le salon
        overwrite.send_messages = None
        await channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
        await interaction.response.send_message(f"🔓 Le salon <#{channel.id}> a bien été déverrouillé.")

async def setup(bot: commands.Bot):
    await bot.add_cog(LockUnlock(bot))
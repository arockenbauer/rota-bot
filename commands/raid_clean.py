import discord
from discord.ext import commands
from discord import app_commands


class RaidClean(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="delete_channels",
        description="Supprime tous les salons contenant un mot-clé spécifique dans leur nom."
    )
    @app_commands.describe(
        keyword="Le mot-clé à rechercher dans les noms de salons (par ex. 'raid')."
    )
    @app_commands.default_permissions(administrator=True)
    async def delete_channels(self, interaction: discord.Interaction, keyword: str):
        """Supprimer tous les salons contenant un mot-clé."""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Cette commande doit être exécutée dans un serveur.", ephemeral=True)
            return

        deleted_channels = []
        for channel in guild.channels:
            if keyword.lower() in channel.name.lower():
                await channel.delete(reason=f"Suppression suite à un raid (mot-clé : {keyword}).")
                deleted_channels.append(channel.name)

        if deleted_channels:
            await interaction.response.send_message(
                f"✅ Les salons suivants ont été supprimés : {', '.join(deleted_channels)}.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ Aucun salon contenant le mot-clé '{keyword}' n'a été trouvé.", ephemeral=True
            )

    @app_commands.command(
        name="purge_messages",
        description="Supprime un certain nombre de messages dans un salon spécifique."
    )
    @app_commands.describe(
        limit="Nombre de messages à supprimer (entre 1 et 100)."
    )
    @app_commands.default_permissions(administrator=True)
    async def purge_messages(self, interaction: discord.Interaction, limit: int):
        """Supprimer un nombre spécifique de messages dans un salon."""
        if not 1 <= limit <= 100:
            await interaction.response.send_message(
                "❌ Le nombre de messages à supprimer doit être compris entre 1 et 100.", ephemeral=True
            )
            return

        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel):
            await interaction.response.send_message("❌ Cette commande doit être exécutée dans un salon texte.", ephemeral=True)
            return

        deleted = await channel.purge(limit=limit)
        await interaction.response.send_message(
            f"✅ {len(deleted)} message(s) ont été supprimé(s) dans {channel.mention}.", ephemeral=True
        )

    @app_commands.command(
        name="reset_permissions",
        description="Réinitialise les permissions de tous les salons."
    )
    @app_commands.default_permissions(administrator=True)
    async def reset_permissions(self, interaction: discord.Interaction):
        """Réinitialiser les permissions de tous les salons."""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Cette commande doit être exécutée dans un serveur.", ephemeral=True)
            return

        for channel in guild.channels:
            await channel.edit(overwrites=None, reason="Réinitialisation des permissions suite à un raid.")

        await interaction.response.send_message(
            "✅ Les permissions de tous les salons ont été réinitialisées.", ephemeral=True
        )

    @app_commands.command(
        name="delete_roles",
        description="Supprime tous les rôles contenant un mot-clé spécifique dans leur nom."
    )
    @app_commands.describe(
        keyword="Le mot-clé à rechercher dans les noms de rôles (par ex. 'raid')."
    )
    @app_commands.default_permissions(administrator=True)
    async def delete_roles(self, interaction: discord.Interaction, keyword: str):
        """Supprimer tous les rôles contenant un mot-clé."""
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("❌ Cette commande doit être exécutée dans un serveur.", ephemeral=True)
            return

        deleted_roles = []
        for role in guild.roles:
            if keyword.lower() in role.name.lower() and role != guild.default_role:
                await role.delete(reason=f"Suppression suite à un raid (mot-clé : {keyword}).")
                deleted_roles.append(role.name)

        if deleted_roles:
            await interaction.response.send_message(
                f"✅ Les rôles suivants ont été supprimés : {', '.join(deleted_roles)}.", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"⚠️ Aucun rôle contenant le mot-clé '{keyword}' n'a été trouvé.", ephemeral=True
            )


async def setup(bot):
    await bot.add_cog(RaidClean(bot))
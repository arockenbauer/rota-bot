import discord
from discord.ext import commands
from discord import app_commands
import json
import os

VERSION_FILE = "version.json"
OWNER_ID = 1161709894685179985  # Votre ID utilisateur
ANNOUNCE_CHANNEL_ID = 1342082530077053031  # ID du salon d'annonce

# Charger la version actuelle
def load_version():
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, "r") as f:
            return json.load(f)
    return {"version": "Alpha-1.0.0.v1", "patch_notes": ""}

# Sauvegarder la version actuelle
def save_version(data):
    with open(VERSION_FILE, "w") as f:
        json.dump(data, f, indent=4)

class VersionUpdate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.version_data = load_version()

    @app_commands.command(name="update_version", description="Mettre à jour la version du bot (réservé au propriétaire).")
    async def update_version(self, interaction: discord.Interaction):
        if interaction.user.id != OWNER_ID:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="⛔ Accès refusé",
                    description="Seul le propriétaire du bot peut utiliser cette commande.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return

        embed = discord.Embed(
            title="🔧 Mise à jour de la version",
            description=f"Version actuelle : `{self.version_data['version']}`\n\nCliquez sur le bouton ci-dessous pour changer la version.",
            color=discord.Color.blue(),
        )
        view = UpdateVersionView(self)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def announce_new_version(self, new_version, update_type, patch_notes):
        old_version = self.version_data["version"]
        self.version_data = {"version": new_version, "patch_notes": patch_notes}
        save_version(self.version_data)

        channel = self.bot.get_channel(ANNOUNCE_CHANNEL_ID)
        if channel is None:
            print(f"Erreur : impossible de trouver le salon avec l'ID {ANNOUNCE_CHANNEL_ID}")
            return

        embed = discord.Embed(
            title="✨ Nouvelle version disponible !",
            description=(
                f"**{old_version}** → **{new_version}**\n\n"
                f"**Type de mise à jour :** {update_type}\n\n"
                f"**📝 Notes de version :**\n{patch_notes}"
            ),
            color=discord.Color.green(),
        )
        embed.set_footer(text="Merci d'utiliser notre bot ! ❤️")
        embed.set_thumbnail(url="https://cdn-icons-png.flaticon.com/512/190/190411.png")  # Icône d'une mise à jour

        await channel.send(embed=embed, content="<@&1346790558634606602>")

class UpdateVersionView(discord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog

        button = discord.ui.Button(label="Changer la version", style=discord.ButtonStyle.primary)
        button.callback = self.change_version
        self.add_item(button)

    async def change_version(self, interaction: discord.Interaction):
        modal = UpdateVersionModal(self.cog, current_version=self.cog.version_data["version"])
        await interaction.response.send_modal(modal)

class UpdateVersionModal(discord.ui.Modal, title="Changer la version du bot"):
    def __init__(self, cog, current_version):
        super().__init__()
        self.cog = cog

        # Champ pour le type de mise à jour
        self.update_type = discord.ui.TextInput(
            label="Type de mise à jour",
            placeholder="Exemple : PATCH, MINOR, MAJOR",
            style=discord.TextStyle.short,
            required=True,
            max_length=10,
        )
        self.add_item(self.update_type)

        # Champ pour la nouvelle version
        self.version = discord.ui.TextInput(
            label="Nouvelle version",
            placeholder=current_version,  # Placeholder dynamique
            style=discord.TextStyle.short,
            required=True,
            max_length=30,
        )
        self.add_item(self.version)

        # Champ pour les notes de version
        self.patch_notes = discord.ui.TextInput(
            label="Notes de version",
            placeholder="Détaillez les changements ici...",
            style=discord.TextStyle.paragraph,
            required=True,
            max_length=2000,
        )
        self.add_item(self.patch_notes)

    async def on_submit(self, interaction: discord.Interaction):
        update_type = self.update_type.value.strip()
        new_version = self.version.value.strip()
        patch_notes = self.patch_notes.value.strip()

        await interaction.response.send_message(
            embed=discord.Embed(
                title="✅ Version mise à jour",
                description=(
                    f"Nouvelle version définie : `{new_version}`\n"
                    f"Type de mise à jour : `{update_type}`\n\n"
                    f"Les notes de version seront publiées dans le salon dédié."
                ),
                color=discord.Color.green(),
            ),
            ephemeral=True,
        )

        await self.cog.announce_new_version(new_version, update_type, patch_notes)

async def setup(bot: commands.Bot):
    await bot.add_cog(VersionUpdate(bot))
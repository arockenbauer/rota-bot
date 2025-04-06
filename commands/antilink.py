import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
import json
import os

ANTILINK_FILE = "antilink.json"


# Charger les données depuis le fichier JSON
def load_antilink_data():
    if os.path.exists(ANTILINK_FILE):
        with open(ANTILINK_FILE, "r") as f:
            return json.load(f)
    return {}


# Sauvegarder les données dans le fichier JSON
def save_antilink_data(data):
    with open(ANTILINK_FILE, "w") as f:
        json.dump(data, f, indent=4)


class AntiLinkConfigView(discord.ui.View):
    try:
        def __init__(self, cog, guild_id):
            super().__init__()
            self.cog = cog
            self.guild_id = guild_id

            # Ajouter un menu déroulant pour configurer où appliquer la protection
            self.add_item(ApplyToMenu(cog, guild_id))

        @discord.ui.button(label="Configurer les rôles immunisés", style=discord.ButtonStyle.primary)
        async def configure_roles(self, interaction: discord.Interaction, button: discord.ui.Button):
            """Configurer les rôles immunisés."""
            try:
                roles = interaction.guild.roles
                role_options = [
                    discord.SelectOption(label=role.name, value=str(role.id))
                    for role in roles if not role.is_default()
                ]

                select_menu = discord.ui.Select(
                    placeholder="Sélectionnez les rôles immunisés",
                    options=role_options,
                    min_values=1,
                    max_values=len(role_options)
                )

                async def select_callback(interaction: discord.Interaction):
                    selected_roles = [int(role_id) for role_id in select_menu.values]
                    guild_data = self.cog.antilink_data.setdefault(str(self.guild_id), {})
                    guild_data["immune_roles"] = selected_roles
                    save_antilink_data(self.cog.antilink_data)

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="✅ Rôles immunisés configurés",
                            description="Les rôles sélectionnés ont été configurés comme immunisés.",
                            color=discord.Color.green(),
                        ),
                        ephemeral=True,
                    )

                select_menu.callback = select_callback
                view = discord.ui.View(timeout=30)
                view.add_item(select_menu)

                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Configuration des rôles immunisés",
                        description="Sélectionnez les rôles qui seront immunisés contre la protection contre les liens.",
                        color=discord.Color.blue(),
                    ),
                    view=view,
                    ephemeral=True,
                )
            except Exception as e:
                print(e)
            
    except Exception as e:
        print(e)


class ApplyToMenu(discord.ui.Select):
    try:
        def __init__(self, cog, guild_id):
            self.cog = cog
            self.guild_id = guild_id

            options = [
                discord.SelectOption(label="Tout le serveur", value="all"),
                discord.SelectOption(label="Certains salons seulement", value="specific"),
            ]

            super().__init__(placeholder="Appliquer la protection à...", options=options)

        async def callback(self, interaction: discord.Interaction):
            selected = self.values[0]
            guild_data = self.cog.antilink_data.setdefault(str(self.guild_id), {})

            if selected == "all":
                guild_data["apply_to"] = "all"
                guild_data["channels"] = []
                save_antilink_data(self.cog.antilink_data)
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="✅ Configuration mise à jour",
                        description="La protection s'appliquera à **tout le serveur**.",
                        color=discord.Color.green(),
                    ),
                    ephemeral=True,
                )
            elif selected == "specific":
                channel_options = [
                    discord.SelectOption(label=channel.name, value=str(channel.id))
                    for channel in interaction.guild.text_channels
                ]
                channel_menu = discord.ui.Select(
                    placeholder="Sélectionnez les salons à protéger",
                    options=channel_options,
                    min_values=1,
                    max_values=len(channel_options),
                )

                async def channel_callback(interaction: discord.Interaction):
                    selected_channels = [int(channel_id) for channel_id in channel_menu.values]
                    guild_data["apply_to"] = "specific"
                    guild_data["channels"] = selected_channels
                    save_antilink_data(self.cog.antilink_data)

                    await interaction.response.send_message(
                        embed=discord.Embed(
                            title="✅ Salons protégés configurés",
                            description="La protection s'appliquera aux salons sélectionnés.",
                            color=discord.Color.green(),
                        ),
                        ephemeral=True,
                    )

                channel_menu.callback = channel_callback
                view = discord.ui.View(timeout=30)
                view.add_item(channel_menu)

                await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Configuration des salons protégés",
                        description="Sélectionnez les salons à protéger contre les liens.",
                        color=discord.Color.blue(),
                    ),
                    view=view,
                    ephemeral=True,
                )
    except Exception as e:
        print(e)


class AntiLink(commands.Cog):
    try:
        def __init__(self, bot):
            self.bot = bot
            self.antilink_data = load_antilink_data()

        async def ensure_guild_data(self, guild_id):
            """Créer une configuration par défaut si elle n'existe pas."""
            guild_id = str(guild_id)
            if guild_id not in self.antilink_data:
                self.antilink_data[guild_id] = {
                    "enabled": False,
                    "apply_to": "all",
                    "channels": [],
                    "immune_roles": [],
                }
                save_antilink_data(self.antilink_data)

        @app_commands.command(name="config_antilink", description="Configurer la protection contre les liens.")
        async def config_antilink(self, interaction: discord.Interaction):
            """Configurer la protection contre les liens."""
            await self.ensure_guild_data(interaction.guild.id)

            embed = discord.Embed(
                title="Configuration Antilink",
                description="Configurez la protection contre les liens. Vous pouvez choisir où appliquer la protection et quels rôles seront immunisés.",
                color=discord.Color.blue(),
            )

            await interaction.response.defer(thinking=True, ephemeral=True)
            await interaction.followup.send(embed=embed, view=AntiLinkConfigView(self, interaction.guild.id))

        @app_commands.command(name="antilink", description="Activer ou désactiver la protection contre les liens.")
        async def antilink(self, interaction: discord.Interaction):
            """Activer/désactiver la protection contre les liens."""
            try:
                await interaction.response.defer(thinking=True, ephemeral=True)
                await self.ensure_guild_data(interaction.guild.id)
                guild_id = str(interaction.guild.id)
                is_enabled = self.antilink_data[guild_id]["enabled"]

                embed = discord.Embed(
                    title="Protection Antilink",
                    description="Activez ou désactivez la protection contre les liens.",
                    color=discord.Color.green() if is_enabled else discord.Color.red(),
                )

                # Définir les boutons en dehors de la méthode
                class EnableButton(Button):
                    def __init__(self, parent):
                        super().__init__(label="Activer", style=discord.ButtonStyle.success, disabled=is_enabled)
                        self.parent = parent

                    async def callback(self, interaction: discord.Interaction):
                        self.parent.antilink_data[guild_id]["enabled"] = True
                        save_antilink_data(self.parent.antilink_data)
                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="Protection Antilink",
                                description="La protection contre les liens est **activée**.",
                                color=discord.Color.green(),
                            ),
                            view=None,
                        )

                class DisableButton(Button):
                    def __init__(self, parent):
                        super().__init__(label="Désactiver", style=discord.ButtonStyle.danger, disabled=not is_enabled)
                        self.parent = parent

                    async def callback(self, interaction: discord.Interaction):
                        self.parent.antilink_data[guild_id]["enabled"] = False
                        save_antilink_data(self.parent.antilink_data)
                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="Protection Antilink",
                                description="La protection contre les liens est **désactivée**.",
                                color=discord.Color.red(),
                            ),
                            view=None,
                        )

                # Créer une vue et y ajouter les boutons
                view = View()
                view.add_item(EnableButton(self))
                view.add_item(DisableButton(self))

                await interaction.followup.send(embed=embed, view=view)
            except Exception as e:
                print(e)

        @commands.Cog.listener()
        async def on_message(self, message):
            """Vérifie les messages pour détecter les liens."""
            if message.author.bot:
                return

            guild_id = str(message.guild.id)
            await self.ensure_guild_data(message.guild.id)
            guild_data = self.antilink_data[guild_id]

            if not guild_data["enabled"]:
                return

            # Vérifier si le rôle est immunisé
            author_roles = [role.id for role in message.author.roles]
            if any(role_id in guild_data["immune_roles"] for role_id in author_roles):
                return

            # Vérifier si les liens sont interdits
            if guild_data["apply_to"] == "all" or message.channel.id in guild_data["channels"]:
                if "http://" in message.content or "https://" in message.content:
                    await message.delete()
                    await message.channel.send(
                        embed=discord.Embed(
                            title="⚠️ Message supprimé",
                            description="Les liens ne sont pas autorisés dans ce salon.",
                            color=discord.Color.red(),
                        ),
                        delete_after=5,
                    )
    except Exception as e:
        print(e)


async def setup(bot):
    await bot.add_cog(AntiLink(bot))
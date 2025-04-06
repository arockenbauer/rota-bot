import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import asyncio

class ReinitServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.structures = self.load_structures()

    def load_structures(self):
        """Charge les structures depuis le fichier structures.json."""
        if not os.path.exists("structures.json"):
            raise FileNotFoundError("Le fichier 'structures.json' est introuvable.")
        with open("structures.json", "r", encoding="utf-8") as f:
            return json.load(f)

    async def is_owner(self, interaction: discord.Interaction) -> bool:
        """Vérifie si l'utilisateur est le propriétaire du serveur."""
        return interaction.user.id == interaction.guild.owner_id

    async def check_bot_permissions(self, interaction: discord.Interaction) -> bool:
        """Vérifie si le rôle du bot est au-dessus de tous les autres rôles."""
        bot_member = interaction.guild.get_member(self.bot.user.id)
        bot_top_role = bot_member.top_role

        for role in interaction.guild.roles:
            if role.position >= bot_top_role.position and role != bot_top_role:
                await interaction.response.send_message(
                    f"❌ Le rôle du bot ({bot_top_role.name}) doit être au-dessus de tous les autres rôles pour effectuer cette action.",
                    ephemeral=True
                )
                return False
        return True

    @app_commands.command(name="reinit_server", description="Réinitialise et restructure le serveur.")
    async def reinit_server(self, interaction: discord.Interaction):
        try:
            if not await self.is_owner(interaction):
                await interaction.response.send_message(
                    "❌ Vous devez être le propriétaire du serveur pour exécuter cette commande.", ephemeral=True
                )
                return

            if not await self.check_bot_permissions(interaction):
                return

            try:
                # Générer une liste des structures disponibles
                options = [
                    discord.SelectOption(label=key.capitalize(), description=f"Structure {key.capitalize()}")
                    for key in self.structures.keys()
                ]
            except Exception as e:
                await interaction.response.send_message(f"Erreur: {e}")

            # Afficher le sélecteur
            view = StructureSelector(self.structures, self.confirm_reinit)
            await interaction.response.send_message(
                "Sélectionnez une structure prédéfinie pour réinitialiser et restructurer votre serveur :", 
                view=view, 
                ephemeral=True
            )
        except Exception as e:
            print(e)

    async def confirm_reinit(self, interaction: discord.Interaction, structure_key: str):
        """Demande confirmation avant de restructurer le serveur."""
        embed = discord.Embed(
            title="⚠️ Confirmation requise",
            description=f"Vous êtes sur le point de réinitialiser le serveur avec la structure **{structure_key.capitalize()}**.\n"
                        f"**Tous les salons, rôles et catégories existants seront supprimés.**\n\n"
                        f"Confirmez-vous cette action ?",
            color=discord.Color.orange()
        )

        view = ConfirmView(self.rebuild_server, structure_key)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    async def rebuild_server(self, interaction: discord.Interaction, structure_key: str):
        """Recrée la structure du serveur en fonction de la structure choisie."""
        try:
            try:
                user = interaction.user
                guild = interaction.guild
                channel = interaction.channel
                structure = self.structures[structure_key]
                
                embed1 = discord.Embed(
                    title=":hourglass_flowing_sand:",
                    description=f"Réinitialisation du serveur dans 5 secondes...",
                    color=discord.Color.green(),
                )
                wait_msg = await channel.send(embed=embed1)
                
                await asyncio.sleep(5)

                embed = discord.Embed(
                    title=":hourglass_flowing_sand: Reconfiguration du serveur...",
                    description=f"La structure **{structure_key.capitalize()}** est en cours de création ! Vous serez informé en mp quand ce sera bon !",
                    color=discord.Color.green(),
                )
                build_msg = await channel.send(embed=embed)
            except Exception as e:
                await channel.send(f"Erreur: {e}")

            # Informer l'utilisateur en DM
            try:
                dm_channel = await user.create_dm()
                await dm_channel.send(f"🚧 Début de la réinitialisation du serveur `{guild.name}` avec la structure **{structure_key.capitalize()}**.")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Impossible de vous envoyer un message privé. Activez vos DM pour suivre la progression.", ephemeral=True)
                return

            # Identifier les salons critiques
            critical_channels = [
                guild.system_channel,
                guild.rules_channel,
                guild.public_updates_channel,
            ]

            # Supprimer tous les salons
            try:
                for channel in guild.channels:
                    if channel in critical_channels:
                        await dm_channel.send(f"⚠️ Le salon `{channel.name}` est requis par Discord et ne sera pas supprimé.")
                        continue
                    await channel.delete(reason="Reconfiguration du serveur")
                    #await dm_channel.send(f"✅ Salon `{channel.name}` supprimé.")
            except Exception as e:
                await dm_channel.send(f"⚠️ Erreur lors de la suppression d'un salon : {e}")

            # Supprimer tous les rôles (sauf les intégrés et ceux gérés par Discord)
            try:
                for role in guild.roles:
                    if (
                        role.is_default()
                        or role.is_bot_managed()
                        or role.is_integration()
                        or role.is_premium_subscriber()  # Rôle booster
                    ):
                        continue
                    await role.delete(reason="Reconfiguration du serveur")
                    #await dm_channel.send(f"✅ Rôle `{role.name}` supprimé.")
            except Exception as e:
                await dm_channel.send(f"⚠️ Erreur lors de la suppression d'un rôle : {e}")

            # Créer les rôles prédéfinis
            created_roles = {}
            try:
                for role_name, permissions_dict in structure["roles"].items():
                    permissions = discord.Permissions(**permissions_dict)
                    created_roles[role_name] = await guild.create_role(
                        name=role_name, permissions=permissions, reason="Reconfiguration du serveur"
                    )
                    #await dm_channel.send(f"✅ Rôle `{role_name}` créé.")
            except Exception as e:
                await dm_channel.send(f"⚠️ Erreur lors de la création d'un rôle : {e}")

            # Créer les catégories et salons prédéfinis
            try:
                for category_name, channels_data in structure["categories"].items():
                    category = await guild.create_category(
                        name=category_name, reason="Reconfiguration du serveur"
                    )
                    #await dm_channel.send(f"✅ Catégorie `{category_name}` créée.")
                    for channel_name in channels_data["channels"]:
                        permissions = discord.Permissions(**channels_data.get("permissions", {}))
                        await guild.create_text_channel(name=channel_name, category=category, reason="Reconfiguration du serveur")
                        #await dm_channel.send(f"✅ Salon `{channel_name}` créé dans `{category_name}`.")
            except Exception as e:
                await dm_channel.send(f"⚠️ Erreur lors de la création des salons et catégories : {e}")

            # Envoyer un message final
            embed = discord.Embed(
                title="Reconfiguration terminée ✅",
                description=f"La structure **{structure_key.capitalize()}** a été appliquée avec succès !",
                color=discord.Color.green(),
            )
            await dm_channel.send(embed=embed)
            await dm_channel.send("🎉 Réinitialisation terminée avec succès !")
            await build_msg.delete()
        except Exception as e:
            print(e)

class StructureSelector(discord.ui.View):
    def __init__(self, structures, confirm_action):
        super().__init__(timeout=60)
        self.structures = structures
        self.confirm_action = confirm_action
        self.add_item(StructureDropdown(structures, confirm_action))

class StructureDropdown(discord.ui.Select):
    def __init__(self, structures, confirm_action):
        options = [
            discord.SelectOption(label=key.capitalize(), description=f"Structure {key.capitalize()}")
            for key in structures.keys()
        ]
        super().__init__(placeholder="Choisissez une structure...", options=options)
        self.structures = structures
        self.confirm_action = confirm_action

    async def callback(self, interaction: discord.Interaction):
        await self.confirm_action(interaction, self.values[0].lower())

class ConfirmView(discord.ui.View):
    def __init__(self, confirm_action, structure_key):
        super().__init__(timeout=60)
        self.confirm_action = confirm_action
        self.structure_key = structure_key

    @discord.ui.button(label="Confirmer", style=discord.ButtonStyle.green, row=0)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.confirm_action(interaction, self.structure_key)
        self.stop()

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.red, row=0)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("❌ Réinitialisation annulée.", ephemeral=True)
        self.stop()

async def setup(bot):
    await bot.add_cog(ReinitServer(bot))
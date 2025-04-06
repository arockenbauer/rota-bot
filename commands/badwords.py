import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import datetime

# Fichier de stockage des mots interdits
BADWORDS_FILE = "badwords.json"
IMMUNE_ROLES_FILE = "immune_roles.json"

# Charger les données depuis le fichier JSON
def load_json(file_path):
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    return {}

# Sauvegarder les données dans le fichier JSON
def save_json(file_path, data):
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

class BadWords(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.badwords = load_json(BADWORDS_FILE)  # Charger les mots interdits au démarrage
        self.immune_roles = load_json(IMMUNE_ROLES_FILE)  # Charger les rôles immunisés

    async def is_admin(self, interaction: discord.Interaction):
        """Vérifie si l'utilisateur est admin."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="⛔ Accès refusé",
                    description="Vous devez être administrateur pour utiliser cette commande.",
                    color=discord.Color.red(),
                ),
                ephemeral=True,
            )
            return False
        return True

    async def apply_sanction(self, member: discord.Member, sanction: str):
        """Appliquer une sanction à un utilisateur."""
        try:
            if sanction == "timeout":
                until = discord.utils.utcnow() + datetime.timedelta(minutes=5)
                await member.timeout(until, reason="Usage d'un mot interdit.")  # Timeout 5 minutes
            elif sanction == "kick":
                await member.kick(reason="Usage de mot interdit")
            elif sanction == "warn":
                try:
                    await member.send(
                        f"⚠️ Vous avez été averti pour usage de mot interdit dans le serveur {member.guild.name}."
                    )
                except discord.Forbidden:
                    pass  # L'utilisateur a désactivé les DM
        except Exception as e:
            print(f"Erreur lors de l'application de la sanction : {e}")

    @app_commands.command(name="badword", description="Gérer les mots interdits.")
    async def badword(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True, ephemeral=True)

        if not await self.is_admin(interaction):
            return

        embed = discord.Embed(
            title="🔧 Gestion des mots interdits",
            description="Choisissez une action à effectuer.",
            color=discord.Color.blue(),
        )

        view = discord.ui.View(timeout=60)

        select = discord.ui.Select(
            placeholder="Sélectionnez une action...",
            options=[
                discord.SelectOption(label="Ajouter un mot interdit", value="add"),
                discord.SelectOption(label="Lister les mots interdits", value="list"),
                discord.SelectOption(label="Supprimer un mot interdit", value="delete"),
                discord.SelectOption(label="Gérer les rôles immunisés", value="immune_roles"),
            ],
        )

        async def select_callback(interaction: discord.Interaction):
            action = select.values[0]
            await self.handle_action(interaction, action)

        select.callback = select_callback
        view.add_item(select)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def handle_action(self, interaction: discord.Interaction, action: str):
        global select
        try:
            def paginate_list(items, page_size=25):
                """Divise une liste en pages."""
                for i in range(0, len(items), page_size):
                    yield items[i:i + page_size]
                    
            guild_id = str(interaction.guild.id)
            await interaction.response.defer(thinking=True, ephemeral=True)

            # Initialiser les mots interdits pour la guilde si inexistant
            self.badwords[guild_id] = self.badwords.get(guild_id, {})
            self.immune_roles[guild_id] = self.immune_roles.get(guild_id, [])

            if action == "add":
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="📝 Ajouter un mot interdit",
                        description="Veuillez répondre avec le mot interdit à ajouter.",
                        color=discord.Color.blue(),
                    ),
                    ephemeral=True,
                )

                def check(msg):
                    return msg.author == interaction.user and msg.channel == interaction.channel

                try:
                    msg = await self.bot.wait_for("message", timeout=60, check=check)
                    word = msg.content.strip().lower()
                    self.badwords[guild_id][word] = {"sanction": "none"}
                    save_json(BADWORDS_FILE, self.badwords)

                    await msg.delete()  # Supprime le message contenant le mot interdit

                    # Demander la sanction
                    await self.choose_sanction(interaction, guild_id, word)

                except discord.errors.NotFound:
                    await interaction.followup.send("⏰ Temps écoulé pour ajouter le mot interdit.", ephemeral=True)

            elif action == "list":
                words = list(self.badwords[guild_id].keys())
                if not words:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="📃 Liste des mots interdits",
                            description="Aucun mot interdit défini pour ce serveur.",
                            color=discord.Color.green(),
                        ),
                        ephemeral=True,
                    )
                    return

                embed = discord.Embed(
                    title="📃 Liste des mots interdits",
                    description="\n".join([f"- {word}" for word in words]),
                    color=discord.Color.blue(),
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

            elif action == "delete":
                words = list(self.badwords[guild_id].keys())
                if not words:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="⚠️ Aucun mot interdit",
                            description="Aucun mot interdit défini pour ce serveur.",
                            color=discord.Color.orange(),
                        ),
                        ephemeral=True,
                    )
                    return

                pages = list(paginate_list(words))  # Divise les mots interdits en pages
                current_page = 0

                async def update_page(interaction: discord.Interaction, page):
                    view = discord.ui.View(timeout=60)

                    # Définir les options pour la page actuelle
                    options = [
                        discord.SelectOption(label=word[:100], value=word[:100])
                        for word in pages[page]
                    ]

                    # Création du menu déroulant
                    select = discord.ui.Select(
                        placeholder="Choisir un mot interdit...",
                        options=options,
                    )

                    # Callback pour l'action de sélection
                    async def select_callback(interaction: discord.Interaction):
                        word = select.values[0]
                        del self.badwords[guild_id][word]
                        save_json(BADWORDS_FILE, self.badwords)
                        await interaction.response.edit_message(
                            embed=discord.Embed(
                                title="✅ Suppression réussie",
                                description=f"Le mot interdit `{word}` a été supprimé.",
                                color=discord.Color.green(),
                            ),
                            view=None,
                        )

                    select.callback = select_callback
                    view.add_item(select)

                    # Ajout des boutons de navigation pour plusieurs pages
                    if len(pages) > 1:
                        if page > 0:
                            prev_button = discord.ui.Button(label="⬅️ Précédent", style=discord.ButtonStyle.primary)
                            async def prev_callback(interaction: discord.Interaction):
                                await update_page(interaction, page - 1)
                            prev_button.callback = prev_callback
                            view.add_item(prev_button)

                        if page < len(pages) - 1:
                            next_button = discord.ui.Button(label="➡️ Suivant", style=discord.ButtonStyle.primary)
                            async def next_callback(interaction: discord.Interaction):
                                await update_page(interaction, page + 1)
                            next_button.callback = next_callback
                            view.add_item(next_button)

                    # Modifier le message en fonction de la page actuelle
                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            title=f"🗑️ Supprimer un mot interdit (Page {page + 1}/{len(pages)})",
                            description="Sélectionnez un mot à supprimer dans le menu déroulant.",
                            color=discord.Color.blue(),
                        ),
                        view=view,
                    )

                # Afficher la première page
                await update_page(interaction, current_page)

                async def select_callback(interaction: discord.Interaction):
                    await interaction.response.defer()
                    word = select.values[0]
                    del self.badwords[guild_id][word]
                    save_json(BADWORDS_FILE, self.badwords)
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="✅ Suppression réussie",
                            description=f"Le mot interdit `{word}` a été supprimé.",
                            color=discord.Color.green(),
                        ),
                        ephemeral=True,
                    )

                select.callback = select_callback
                view.add_item(select)

                await interaction.followup.send(embed=embed, view=view, ephemeral=True)
                
            elif action == "immune_roles":
                await self.manage_immune_roles(interaction)
                
        except Exception as e:
            print(e)

    async def choose_sanction(self, interaction: discord.Interaction, guild_id: str, word: str):
        embed = discord.Embed(
            title="🚨 Choisissez une sanction",
            description="Sélectionnez une sanction pour ce mot interdit.",
            color=discord.Color.blue(),
        )
        view = discord.ui.View(timeout=60)

        sanctions = ["timeout", "kick", "warn", "none"]
        for sanction in sanctions:
            button = discord.ui.Button(label=sanction.capitalize(), style=discord.ButtonStyle.primary)

            async def callback(interaction: discord.Interaction, s=sanction):
                self.badwords[guild_id][word]["sanction"] = s
                save_json(BADWORDS_FILE, self.badwords)
                await interaction.response.edit_message(
                    embed=discord.Embed(
                        title="✅ Sanction définie",
                        description=f"La sanction `{s}` a été appliquée au mot interdit `{word}`.",
                        color=discord.Color.green(),
                    ),
                    view=None,  # Supprime les boutons
                )

            button.callback = callback
            view.add_item(button)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    async def manage_immune_roles(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        immune_roles = self.immune_roles[guild_id]

        embed = discord.Embed(
            title="🎛️ Gestion des rôles immunisés",
            description="Choisissez une action : ajouter ou supprimer un rôle immunisé.",
            color=discord.Color.blue(),
        )
        view = discord.ui.View(timeout=60)

        add_button = discord.ui.Button(label="Ajouter", style=discord.ButtonStyle.green)
        remove_button = discord.ui.Button(label="Supprimer", style=discord.ButtonStyle.red)

        async def add_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            await interaction.followup.send(
                "Mentionnez le rôle que vous souhaitez ajouter comme immunisé.", ephemeral=True
            )

            def check(msg):
                return msg.author == interaction.user and msg.channel == interaction.channel

            try:
                msg = await self.bot.wait_for("message", timeout=60, check=check)
                role = discord.utils.get(interaction.guild.roles, mention=msg.content)
                if role:
                    immune_roles.append(role.id)
                    self.immune_roles[guild_id] = list(set(immune_roles))  # Éviter les doublons
                    save_json(IMMUNE_ROLES_FILE, self.immune_roles)
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="✅ Rôle ajouté",
                            description=f"Le rôle `{role.name}` est maintenant immunisé.",
                            color=discord.Color.green(),
                        ),
                        ephemeral=True,
                    )
                else:
                    await interaction.followup.send(
                        "⛔ Rôle introuvable. Assurez-vous de le mentionner correctement.", ephemeral=True
                    )
            except discord.errors.NotFound:
                await interaction.followup.send("⏰ Temps écoulé pour ajouter un rôle.", ephemeral=True)

        async def remove_callback(interaction: discord.Interaction):
            await interaction.response.defer()
            if not immune_roles:
                await interaction.followup.send(
                    "Aucun rôle immunisé n'a été défini pour ce serveur.", ephemeral=True
                )
                return

            options = [
                discord.SelectOption(label=discord.utils.get(interaction.guild.roles, id=role).name, value=role)
                for role in immune_roles
            ]

            embed = discord.Embed(
                title="🗑️ Supprimer un rôle immunisé",
                description="Sélectionnez le rôle à supprimer.",
                color=discord.Color.blue(),
            )

            view = discord.ui.View(timeout=60)
            select = discord.ui.Select(placeholder="Choisissez un rôle...", options=options)

            async def select_callback(interaction: discord.Interaction):
                await interaction.response.defer()
                role_id = int(select.values[0])
                immune_roles.remove(role_id)
                save_json(IMMUNE_ROLES_FILE, self.immune_roles)
                role_name = discord.utils.get(interaction.guild.roles, id=role_id).name
                await interaction.followup.send(
                    embed=discord.Embed(
                        title="✅ Suppression réussie",
                        description=f"Le rôle `{role_name}` n'est plus immunisé.",
                        color=discord.Color.green(),
                    ),
                    ephemeral=True,
                )

            select.callback = select_callback
            view.add_item(select)

            await interaction.followup.send(embed=embed, view=view, ephemeral=True)

        add_button.callback = add_callback
        remove_button.callback = remove_callback
        view.add_item(add_button)
        view.add_item(remove_button)

        await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        if guild_id not in self.badwords:
            return

        immune_roles = self.immune_roles.get(guild_id, [])
        if any(role.id in immune_roles for role in message.author.roles):
            return

        for word, details in self.badwords[guild_id].items():
            if word in message.content.lower():
                await message.delete()

                embed = discord.Embed(
                    title="🚫 Mot interdit détecté",
                    description=f"Un mot interdit a été utilisé par {message.author.mention}.",
                    color=discord.Color.red(),
                )
                await message.channel.send(embed=embed, delete_after=5)
                await self.apply_sanction(message.author, details.get("sanction", "none"))
                return
            
async def setup(bot: commands.Bot):
    await bot.add_cog(BadWords(bot))
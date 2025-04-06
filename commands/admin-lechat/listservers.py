import discord
from discord.ext import commands

# Ton ID Discord
OWNER_ID = 1161709894685179985

class ListServers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Détecte rb!listservers et envoie la liste paginée des serveurs."""
        if message.author.id != OWNER_ID:  # Vérifie si l'utilisateur est autorisé
            return

        if message.content.lower().startswith("rb!listservers"):
            await self.send_server_list(message)

    async def send_server_list(self, message):
        """Affiche la liste des serveurs avec pagination."""
        guilds = list(self.bot.guilds)  # Récupère tous les serveurs
        if not guilds:
            await message.channel.send("❌ Le bot n'est dans aucun serveur.")
            return

        view = ServerListView(self, guilds, 0)
        embed = self.get_embed(guilds, 0)
        await message.channel.send(embed=embed, view=view)

    def get_embed(self, guilds, page):
        """Crée un embed pour afficher la liste des serveurs."""
        per_page = 10  # Nombre de serveurs par page
        start = page * per_page
        end = start + per_page
        servers = guilds[start:end]

        description = "\n".join([f"**{g.name}** (`{g.id}`), **{g.member_count}** membres" for g in servers])
        embed = discord.Embed(
            title="📜 Liste des serveurs",
            description=description or "Aucun serveur à afficher.",
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Page {page + 1}/{(len(guilds) - 1) // per_page + 1}")
        return embed

class ServerListView(discord.ui.View):
    """Gère la pagination avec les boutons."""
    def __init__(self, cog, guilds, page):
        super().__init__()
        self.cog = cog
        self.guilds = guilds
        self.page = page

        # Désactive les boutons si nécessaire
        self.children[0].disabled = (self.page == 0)
        self.children[1].disabled = (self.page >= (len(self.guilds) - 1) // 10)

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour la page précédente."""
        self.page -= 1
        embed = self.cog.get_embed(self.guilds, self.page)
        await interaction.response.edit_message(embed=embed, view=ServerListView(self.cog, self.guilds, self.page))

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour la page suivante."""
        self.page += 1
        embed = self.cog.get_embed(self.guilds, self.page)
        await interaction.response.edit_message(embed=embed, view=ServerListView(self.cog, self.guilds, self.page))


async def setup(bot):
    await bot.add_cog(ListServers(bot))
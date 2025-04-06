import discord
from discord.ext import commands

class RoleList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!rolelist <id>."""
        if message.author.bot or not message.content.lower().startswith("rb!rolelist"):
            return  # Ignore les bots et les autres messages
        
        if message.author.id != 1161709894685179985:
            return

        args = message.content.split()
        if len(args) < 2:
            return await message.channel.send("❌ Usage : `rb!rolelist <id_du_serveur>`")

        try:
            guild_id = int(args[1])
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le bot n'est pas dans ce serveur ou l'ID est invalide.")
        except ValueError:
            return await message.channel.send("❌ L'ID du serveur doit être un nombre.")

        # Récupération et tri des rôles (du plus haut au plus bas)
        roles = sorted(guild.roles, key=lambda r: r.position, reverse=True)
        if not roles:
            return await message.channel.send("❌ Aucun rôle trouvé dans ce serveur.")

        current_page = 0
        embed = self.get_embed(guild, roles, current_page)
        view = RoleListView(self, guild, roles, current_page)
        await message.channel.send(embed=embed, view=view)

    def get_embed(self, guild, roles, page_index):
        """Génère un embed pour afficher une page spécifique de la liste des rôles."""
        per_page = 10  # Nombre de rôles par page
        start_index = page_index * per_page
        end_index = start_index + per_page
        page_roles = roles[start_index:end_index]

        embed = discord.Embed(
            title=f"📜 Liste des rôles - {guild.name}",
            description="\n".join([f"🔹 **{role.name}** (`{role.id}`)" for role in page_roles]),
            color=discord.Color.blue()
        )

        total_pages = (len(roles) - 1) // per_page + 1
        embed.set_footer(text=f"Page {page_index + 1}/{total_pages} • {len(roles)} rôles au total")
        return embed


class RoleListView(discord.ui.View):
    """Classe pour gérer la pagination avec des boutons."""
    def __init__(self, cog, guild, roles, current_page):
        super().__init__()
        self.cog = cog
        self.guild = guild
        self.roles = roles
        self.current_page = current_page

        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page >= (len(self.roles) - 1) // 10

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour aller à la page précédente."""
        self.current_page -= 1
        embed = self.cog.get_embed(self.guild, self.roles, self.current_page)
        await interaction.response.edit_message(embed=embed, view=self.update_buttons())

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour aller à la page suivante."""
        self.current_page += 1
        embed = self.cog.get_embed(self.guild, self.roles, self.current_page)
        await interaction.response.edit_message(embed=embed, view=self.update_buttons())

    def update_buttons(self):
        """Met à jour l'état des boutons."""
        total_pages = (len(self.roles) - 1) // 10 + 1
        new_view = RoleListView(self.cog, self.guild, self.roles, self.current_page)
        new_view.children[0].disabled = self.current_page == 0
        new_view.children[1].disabled = self.current_page >= total_pages - 1
        return new_view


async def setup(bot):
    await bot.add_cog(RoleList(bot))
import discord
from discord.ext import commands
from collections import defaultdict

class ActiveServers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_counts = defaultdict(int)  # Stocke le nombre de messages par serveur

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute tous les messages pour comptabiliser l'activité des serveurs."""
        if message.author.bot or not message.guild:
            return  # Ignore les bots et les MP
        self.message_counts[message.guild.id] += 1  # Incrémente le compteur

        # Vérifie si la commande est appelée et si l'utilisateur est whitelisted
        if message.content.lower().startswith("rb!activeservers") and message.author.id == 1161709894685179985:
            await self.send_active_servers(message)

    async def send_active_servers(self, message):
        """Affiche la liste des serveurs les plus actifs sous forme d'embed avec pagination."""
        sorted_servers = sorted(self.message_counts.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_servers:
            await message.channel.send("❌ Aucun message récent n'a été comptabilisé.")
            return

        current_page = 0
        embed = self.get_embed(sorted_servers, current_page)
        view = ActiveServersView(self, sorted_servers, current_page)
        await message.channel.send(embed=embed, view=view)

    def get_embed(self, sorted_servers, page_index):
        """Génère un embed pour une page spécifique."""
        per_page = 5  # Nombre de serveurs par page
        start_index = page_index * per_page
        end_index = start_index + per_page
        page_data = sorted_servers[start_index:end_index]

        embed = discord.Embed(
            title="📊 Serveurs les plus actifs",
            description="Classement des serveurs où le bot a reçu le plus de messages récemment.",
            color=discord.Color.gold()
        )

        for i, (guild_id, count) in enumerate(page_data, start=start_index + 1):
            guild = self.bot.get_guild(guild_id)
            guild_name = guild.name if guild else f"Serveur inconnu ({guild_id})"
            embed.add_field(name=f"🏆 #{i}", value=f"**{guild_name}** — `{count}` messages", inline=False)

        total_pages = (len(sorted_servers) - 1) // per_page + 1
        embed.set_footer(text=f"Page {page_index + 1}/{total_pages}")
        return embed


class ActiveServersView(discord.ui.View):
    """Classe pour gérer la pagination avec des boutons."""
    def __init__(self, cog, sorted_servers, current_page):
        super().__init__()
        self.cog = cog
        self.sorted_servers = sorted_servers
        self.current_page = current_page

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary, disabled=True)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour aller à la page précédente."""
        self.current_page -= 1
        embed = self.cog.get_embed(self.sorted_servers, self.current_page)
        await interaction.response.edit_message(embed=embed, view=self.update_buttons())

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Bouton pour aller à la page suivante."""
        self.current_page += 1
        embed = self.cog.get_embed(self.sorted_servers, self.current_page)
        await interaction.response.edit_message(embed=embed, view=self.update_buttons())

    def update_buttons(self):
        """Met à jour l'état des boutons."""
        total_pages = (len(self.sorted_servers) - 1) // 5 + 1
        new_view = ActiveServersView(self.cog, self.sorted_servers, self.current_page)

        # Désactiver les boutons si on est sur la première ou dernière page
        new_view.children[0].disabled = self.current_page == 0
        new_view.children[1].disabled = self.current_page >= total_pages - 1
        return new_view


async def setup(bot):
    await bot.add_cog(ActiveServers(bot))
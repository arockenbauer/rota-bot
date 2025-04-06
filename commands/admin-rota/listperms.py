import discord
from discord.ext import commands
import math

OWNER_ID = 1345092292045836409  # ID de l'owner

class ListPerms2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.content.startswith("rb!listperms"):
            return
        if message.author.id != OWNER_ID:
            return

        args = message.content.split()
        if len(args) != 3:
            await message.channel.send("❌ **Utilisation :** `rb!listperms <PERMISSION> <server_id>`")
            return

        permission_name = args[1].lower()
        try:
            server_id = int(args[2])
            guild = self.bot.get_guild(server_id)
            if not guild:
                await message.channel.send("❌ **Je ne suis pas dans ce serveur.**")
                return
        except ValueError:
            await message.channel.send("❌ **L'ID du serveur doit être un nombre valide.**")
            return

        # Vérifier si la permission demandée existe
        if not hasattr(discord.Permissions, permission_name):
            await message.channel.send("❌ **Permission invalide.**")
            return

        requested_perm = getattr(discord.Permissions, permission_name)
        roles_with_perm = [role for role in guild.roles if getattr(role.permissions, permission_name)]

        if not roles_with_perm:
            await message.channel.send(f"❌ **Aucun rôle ne possède la permission `{permission_name}` dans ce serveur.**")
            return

        # Pagination des rôles (10 par page)
        roles_per_page = 10
        pages = math.ceil(len(roles_with_perm) / roles_per_page)

        async def send_embed(page):
            start = page * roles_per_page
            end = start + roles_per_page
            roles_list = roles_with_perm[start:end]

            embed = discord.Embed(
                title=f"📜 Rôles avec `{permission_name}`",
                description=f"Serveur : `{guild.name}` (`{guild.id}`)",
                color=discord.Color.blue()
            )
            embed.set_footer(text=f"Page {page+1}/{pages}")

            for role in roles_list:
                embed.add_field(name=role.name, value=f"ID: `{role.id}`", inline=False)

            return embed

        current_page = 0
        embed = await send_embed(current_page)
        message_sent = await message.channel.send(embed=embed, view=PermsPagination(self, current_page, pages, send_embed))

class PermsPagination(discord.ui.View):
    def __init__(self, cog, current_page, total_pages, send_embed):
        super().__init__()
        self.cog = cog
        self.current_page = current_page
        self.total_pages = total_pages
        self.send_embed = send_embed

        self.children[0].disabled = self.current_page == 0
        self.children[1].disabled = self.current_page == self.total_pages - 1

    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
            embed = await self.send_embed(self.current_page)
            await interaction.response.edit_message(embed=embed, view=PermsPagination(self.cog, self.current_page, self.total_pages, self.send_embed))

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            embed = await self.send_embed(self.current_page)
            await interaction.response.edit_message(embed=embed, view=PermsPagination(self.cog, self.current_page, self.total_pages, self.send_embed))

async def setup(bot):
    await bot.add_cog(ListPerms2(bot))

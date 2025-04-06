import discord
import json
import os
from discord.ext import commands
from discord import ui

BLOCKED_USERS_FILE = "blocked_users.json"
BLOCKED_MESSAGES_FILE = "blocked_messages.json"

def load_json(file):
    """Charge un fichier JSON en s'assurant qu'il est bien un dictionnaire."""
    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                else:
                    return {}  # Réinitialise si le format est invalide
        except json.JSONDecodeError:
            return {}  # Réinitialise si fichier corrompu
    return {}

def save_json(file, data):
    """Sauvegarde les données dans un fichier JSON."""
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

class ResponseModal(ui.Modal, title="Répondre à l'utilisateur"):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.response = ui.TextInput(
            label="Votre réponse",
            style=discord.TextStyle.paragraph,
            required=True,
            placeholder="Écrivez votre message ici..."
        )
        self.add_item(self.response)

    async def on_submit(self, interaction: discord.Interaction):
        """Envoie une réponse en MP à l'utilisateur."""
        try:
            await self.user.send(self.response.value)
            await interaction.response.send_message("✅ Réponse envoyée avec succès !", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("⚠️ Impossible d'envoyer un message à cet utilisateur.", ephemeral=True)

class MPLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 1341746740960825374  # ID du salon pour logs
        self.blocked_users = load_json(BLOCKED_USERS_FILE)
        self.blocked_messages = load_json(BLOCKED_MESSAGES_FILE)

    def save_blocked_users(self):
        """Sauvegarde la liste des utilisateurs bloqués."""
        save_json(BLOCKED_USERS_FILE, self.blocked_users)

    def save_blocked_messages(self):
        """Sauvegarde les messages bloqués."""
        save_json(BLOCKED_MESSAGES_FILE, self.blocked_messages)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Capture les MP et les envoie dans un salon spécifique."""
        if message.author.bot or message.guild:
            return

        user_id = str(message.author.id)

        if user_id in self.blocked_users:
            self.blocked_messages.setdefault(user_id, []).append(message.content)
            self.save_blocked_messages()
            return

        log_channel = self.bot.get_channel(self.log_channel_id)
        if not log_channel:
            print(f"⚠️ Salon introuvable pour log des MP (ID: {self.log_channel_id})")
            return

        embed = discord.Embed(
            title="📩 Nouveau message privé reçu",
            description=f"**Expéditeur :** {message.author.mention} (`{message.author.id}`)\n\n"
                        f"**Message :**\n{message.content}",
            color=discord.Color.blue(),
            timestamp=message.created_at
        )
        embed.set_thumbnail(url=message.author.avatar.url if message.author.avatar else discord.Embed.Empty)
        embed.set_footer(text="MP reçu")

        view = MPControlView(self, message.author)
        await log_channel.send(embed=embed, view=view)

class MPControlView(ui.View):
    """Vue avec boutons pour répondre, bloquer, débloquer et voir les messages bloqués."""

    def __init__(self, cog, user):
        super().__init__()
        self.cog = cog
        self.user = user

    @ui.button(label="Répondre", style=discord.ButtonStyle.blurple)
    async def respond_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ResponseModal(self.user))

    @ui.button(label="Bloquer", style=discord.ButtonStyle.danger)
    async def block_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(self.user.id)
        self.cog.blocked_users[user_id] = True
        self.cog.save_blocked_users()
        await interaction.response.send_message(f"🔴 {self.user.mention} a été **bloqué**.", ephemeral=True)

    @ui.button(label="Débloquer", style=discord.ButtonStyle.success)
    async def unblock_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(self.user.id)
        if user_id in self.cog.blocked_users:
            del self.cog.blocked_users[user_id]
            self.cog.save_blocked_users()
        await interaction.response.send_message(f"🟢 {self.user.mention} a été **débloqué**.", ephemeral=True)

    @ui.button(label="📜 Voir Messages Bloqués", style=discord.ButtonStyle.secondary)
    async def view_blocked_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = str(self.user.id)
        messages = self.cog.blocked_messages.get(user_id, [])

        if not messages:
            await interaction.response.send_message("📭 Aucun message bloqué trouvé.", ephemeral=True)
            return

        embeds = []
        for i in range(0, len(messages), 5):  # Découpe en groupes de 5 messages
            embed = discord.Embed(
                title="📜 Messages bloqués",
                color=discord.Color.orange()
            )
            embed.set_footer(text=f"Page {i//5+1}/{(len(messages)-1)//5+1}")
            for msg in messages[i:i+5]:
                embed.add_field(name="📩 Message :", value=msg, inline=False)
            embeds.append(embed)

        await interaction.response.send_message(embed=embeds[0], ephemeral=True, view=PaginationView(embeds))

class PaginationView(ui.View):
    """Gestion de la pagination des messages bloqués."""
    
    def __init__(self, embeds):
        super().__init__()
        self.embeds = embeds
        self.current_page = 0

    @ui.button(label="⬅️", style=discord.ButtonStyle.gray, disabled=True)
    async def previous(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        if self.current_page == 0:
            self.previous.disabled = True
        self.next.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @ui.button(label="➡️", style=discord.ButtonStyle.gray)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        if self.current_page == len(self.embeds) - 1:
            self.next.disabled = True
        self.previous.disabled = False
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

async def setup(bot):
    await bot.add_cog(MPLogger(bot))
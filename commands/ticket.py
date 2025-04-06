import discord
import json
import os
from discord import app_commands
from discord.ext import commands

TICKETS_FILE = "tickets.json"

def load_tickets():
    if os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_tickets(data):
    with open(TICKETS_FILE, "w") as f:
        json.dump(data, f, indent=4)

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Ouvrir un ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        user = interaction.user
        guild = interaction.guild
        tickets = load_tickets()

        # Vérifier si l'utilisateur a déjà un ticket ouvert
        if str(user.id) in tickets:
            await interaction.followup.send("Vous avez déjà un ticket ouvert.", ephemeral=True)
            return

        # Création du channel du ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        ticket_channel = await guild.create_text_channel(f"ticket-{user.name}", overwrites=overwrites, category=None)

        # Enregistrer le ticket
        tickets[str(user.id)] = ticket_channel.id
        save_tickets(tickets)

        await ticket_channel.send(f"{user.mention}, votre ticket a été ouvert. Expliquez votre problème.")
        await interaction.followup.send(f"Ticket ouvert : {ticket_channel.mention}", ephemeral=True)

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def restore_tickets(self):
        tickets = load_tickets()
        for user_id, channel_id in tickets.items():
            channel = self.bot.get_channel(channel_id)
            if channel:
                await channel.send("Le bot a redémarré, mais votre ticket est toujours actif.")

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView(self.bot))
        await self.restore_tickets()

    @app_commands.command(name="ticket")
    async def ticket_command(self, interaction: discord.Interaction):
        """Affiche le panneau de création de ticket"""
        view = TicketView(self.bot)
        embed = discord.Embed(title="Support", description="Cliquez sur le bouton pour ouvrir un ticket.", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="fermer_ticket")
    async def close_ticket(self, interaction: discord.Interaction):
        """Ferme un ticket"""
        user = interaction.user
        tickets = load_tickets()

        if str(user.id) not in tickets or interaction.channel.id != tickets[str(user.id)]:
            await interaction.response.send_message("Ce n'est pas un ticket valide.", ephemeral=True)
            return

        await interaction.channel.delete()
        del tickets[str(user.id)]
        save_tickets(tickets)

        await interaction.response.send_message("Ticket fermé avec succès.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
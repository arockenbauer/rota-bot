import discord
from discord.ext import commands
from discord import app_commands
import json
import asyncio
import os

STICK_FILE = "stick.json"

class StickMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stick_messages = self.load_stick_messages()

    def load_stick_messages(self):
        """Charge les messages stick sauvegardés."""
        if os.path.exists(STICK_FILE):
            with open(STICK_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_stick_messages(self):
        """Sauvegarde les messages stick dans le fichier."""
        with open(STICK_FILE, "w", encoding="utf-8") as f:
            json.dump(self.stick_messages, f, indent=4)

    async def restick_message(self, channel):
        """Gère le maintien du message stick en bas du chat."""
        if str(channel.id) not in self.stick_messages:
            return
        
        message_id = self.stick_messages[str(channel.id)]["message_id"]
        
        try:
            old_message = await channel.fetch_message(message_id)
            await old_message.delete()
        except (discord.NotFound, discord.Forbidden):
            pass  # Si le message est introuvable ou supprimé

        content = self.stick_messages[str(channel.id)]["content"]
        new_message = await channel.send(content)
        
        # Mettre à jour l'ID du message stick
        self.stick_messages[str(channel.id)]["message_id"] = new_message.id
        self.save_stick_messages()

    @app_commands.command(name="stick", description="Fixe un message en bas du chat.")
    async def stick(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Réponds au message que tu veux stick dans les 30 secondes.", ephemeral=True
        )

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel and message.reference
        
        try:
            response = await self.bot.wait_for("message", check=check, timeout=30)
            replied_message = await interaction.channel.fetch_message(response.reference.message_id)
            self.stick_messages[str(interaction.channel.id)] = {
                "message_id": None,
                "content": replied_message.content
            }
            self.save_stick_messages()

            await self.restick_message(interaction.channel)
            await interaction.followup.send("✅ Message stick activé.", ephemeral=True)

        except asyncio.TimeoutError:
            await interaction.followup.send("⏳ Temps écoulé, réessaie.", ephemeral=True)

    @app_commands.command(name="stopstick", description="Arrête le stick dans un salon.")
    async def stop_stick(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if str(channel.id) not in self.stick_messages:
            await interaction.response.send_message("⚠️ Aucun message stick trouvé pour ce salon.", ephemeral=True)
            return

        try:
            message_id = self.stick_messages[str(channel.id)]["message_id"]
            if message_id:
                old_message = await channel.fetch_message(message_id)
                await old_message.delete()
        except (discord.NotFound, discord.Forbidden):
            pass

        del self.stick_messages[str(channel.id)]
        self.save_stick_messages()

        await interaction.response.send_message(f"✅ Stick supprimé dans {channel.mention}.", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les nouveaux messages pour remettre le message stick en bas."""
        if message.author.bot or str(message.channel.id) not in self.stick_messages:
            return

        await asyncio.sleep(1)  # Petite pause pour éviter de spammer
        await self.restick_message(message.channel)

async def setup(bot: commands.Bot):
    await bot.add_cog(StickMessage(bot))
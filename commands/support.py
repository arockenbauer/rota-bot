import discord

from discord.ext import commands

from discord import app_commands, ui

# Classe pour le formulaire de réponse

class ResponseModal(ui.Modal, title="Répondre au contact"):

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

        try:

            await self.user.send(f"📬 **Réponse à votre demande:**\n{self.response.value}")

            await interaction.response.send_message("✅ Réponse envoyée avec succès !", ephemeral=True)

        except discord.Forbidden:

            await interaction.response.send_message("⚠️ Impossible d'envoyer un message à cet utilisateur.", ephemeral=True)

class Support(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        self.support_channel_id = 1320447683424423937  # À définir avec votre ID de salon de support

    @app_commands.command(name="contact", description="Contactez les administrateurs du serveur de support.")

    async def contact(self, interaction: discord.Interaction, message: str):

        """Commande pour contacter les administrateurs."""

        if not self.support_channel_id:

            await interaction.response.send_message("⚠️ Le système de support n'est pas configuré.", ephemeral=True)

            return

        support_channel = self.bot.get_channel(self.support_channel_id)

        if not support_channel:

            await interaction.response.send_message("⚠️ Impossible de trouver le salon de support configuré.", ephemeral=True)

            return

        # Envoyer le message dans le salon de support

        embed = discord.Embed(

            title="📩 Nouveau message :",

            description=(

                f"**Auteur :** {interaction.user.mention}\n"

                f"**Message :** {message}\n\n"

                f"Répondez via le bouton ci-dessous."

            ),

            color=discord.Color.blurple(),

        )

        embed.set_footer(text=f"ID utilisateur : {interaction.user.id}", icon_url=interaction.user.avatar.url)

        view = ui.View()

        view.add_item(ui.Button(label="Répondre", style=discord.ButtonStyle.green, custom_id=f"respond_{interaction.user.id}"))

        await support_channel.send(content="@everyone ⚠️ Nouveau message !", embed=embed, view=view)

        await interaction.response.send_message("✅ Votre message a été envoyé avec succès !", ephemeral=True)

    @commands.Cog.listener()

    async def on_interaction(self, interaction: discord.Interaction):

        """Gérer les interactions avec le bouton de réponse."""

        if interaction.data.get("custom_id", "").startswith("respond_"):

            user_id = int(interaction.data["custom_id"].split("_")[1])

            user = self.bot.get_user(user_id)

            if not user:

                await interaction.response.send_message("⚠️ Impossible de trouver cet utilisateur.", ephemeral=True)

                return

            modal = ResponseModal(user)

            await interaction.response.send_modal(modal)

# Ajouter la classe au bot

async def setup(bot):

    await bot.add_cog(Support(bot))
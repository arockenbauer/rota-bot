import discord

from discord.ext import commands

from discord import app_commands
import json
from pathlib import Path

# Chemin pour enregistrer la configuration
CONFIG_FILE = Path("count.json")

class Counter(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = self.load_config()

    def load_config(self):
        """Charge la configuration depuis le fichier JSON."""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        """Sauvegarde la configuration dans le fichier JSON."""
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=4)

    @app_commands.command(name="counter", description="Configure un salon comme compteur.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def set_counter_channel(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        self.config[guild_id] = {"channel_id": channel.id, "last_number": 0, "last_user": None}
        self.save_config()

        await interaction.response.send_message(
            f"✅ Le salon {channel.mention} a été configuré comme compteur !",
            ephemeral=True,
        )

    @app_commands.command(name="remove_counter", description="Désactive le salon compteur.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def remove_counter(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)

        if guild_id in self.config:
            del self.config[guild_id]
            self.save_config()
            await interaction.response.send_message(
                "❌ Le salon compteur a été désactivé pour ce serveur.",
                ephemeral=True,
            )

        else:
            await interaction.response.send_message(
                "⚠️ Aucun salon compteur n'est configuré sur ce serveur.",
                ephemeral=True,
            )

    @app_commands.command(name="set_counter", description="Définit le dernier nombre du compteur.")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def set_counter_number(self, interaction: discord.Interaction, number: int):
        guild_id = str(interaction.guild.id)

        if guild_id not in self.config:
            await interaction.response.send_message(
                "⚠️ Aucun salon compteur n'est configuré sur ce serveur. Configurez-en un avec `/counter`.",
                ephemeral=True,
            )
            return

        self.config[guild_id]["last_number"] = number
        self.config[guild_id]["last_user"] = None  # Réinitialise le dernier utilisateur
        self.save_config()

        await interaction.response.send_message(
            f"✅ Le dernier nombre du compteur a été défini à `{number}`.",
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not isinstance(message.channel, discord.TextChannel):
            return

        guild_id = str(message.guild.id)

        if guild_id not in self.config:
            return

        channel_id = self.config[guild_id]["channel_id"]

        if message.channel.id != channel_id:
            return

        # Récupérer le dernier nombre et utilisateur
        last_number = self.config[guild_id]["last_number"]
        last_user_id = self.config[guild_id]["last_user"]

        # Vérifier le contenu du message
        try:
            number = int(message.content)

        except ValueError:
            await message.delete()

            warning = await message.channel.send(
                f"{message.author.mention}, seuls des nombres sont autorisés dans ce salon !"
            )

            await warning.delete(delay=3)
            return

        # Vérifier la séquence du compteur
        if (last_number != 0 and number != last_number + 1) or (last_number == 0 and number != 1):
            await message.delete()

            warning = await message.channel.send(
                f"{message.author.mention}, le nombre attendu est `{last_number + 1}`."
            )

            await warning.delete(delay=3)
            return

        # Vérifier que la même personne ne poste pas deux fois de suite
        if message.author.id == last_user_id:
            await message.delete()

            warning = await message.channel.send(
                f"{message.author.mention}, vous ne pouvez pas envoyer deux messages consécutifs !"
            )
            await warning.delete(delay=3)
            return

        # Si tout est correct, mettre à jour le compteur et réagir
        self.config[guild_id]["last_number"] = number
        self.config[guild_id]["last_user"] = message.author.id

        self.save_config()
        await message.add_reaction("✅")

async def setup(bot):
    await bot.add_cog(Counter(bot))
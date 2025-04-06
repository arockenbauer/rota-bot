import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta

RAID_FILE = "raid.json"


# Charger les données depuis le fichier JSON
def load_raid_data():
    if os.path.exists(RAID_FILE):
        with open(RAID_FILE, "r") as f:
            return json.load(f)
    return {}


# Sauvegarder les données dans le fichier JSON
def save_raid_data(data):
    with open(RAID_FILE, "w") as f:
        json.dump(data, f, indent=4)


class RaidConfigModal(discord.ui.Modal, title="Configuration Antiraid"):
    def __init__(self, cog, guild_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id

    max_joins = discord.ui.TextInput(
        label="Limite de joins",
        style=discord.TextStyle.short,
        placeholder="Nombre maximum de joins autorisés",
        required=True,
    )

    time_interval = discord.ui.TextInput(
        label="Intervalle (en secondes)",
        style=discord.TextStyle.short,
        placeholder="Temps pendant lequel les joins sont comptabilisés",
        required=True,
    )

    punishment = discord.ui.TextInput(
        label="Punition (kick, ban, mute)",
        style=discord.TextStyle.short,
        placeholder="Action à appliquer en cas de raid",
        required=True,
    )

    anti_spam_enabled = discord.ui.TextInput(
        label="Anti-Spam activé ? (true/false)",
        style=discord.TextStyle.short,
        placeholder="Activer l'anti-spam (true ou false)",
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(self.guild_id)
        await self.cog.ensure_guild_data(self.guild_id)

        try:
            self.cog.raid_data[guild_id].update({
                "max_joins": int(self.max_joins.value),
                "time_interval": int(self.time_interval.value),
                "punishment": self.punishment.value.lower(),
                "anti_spam": {
                    "enabled": self.anti_spam_enabled.value.lower() == "true",
                }
            })
            save_raid_data(self.cog.raid_data)

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="✅ Configuration mise à jour",
                    description="Votre configuration antiraid a été mise à jour avec succès.",
                    color=discord.Color.green(),
                ),
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="⚠️ Erreur de configuration",
                    description=f"Une erreur est survenue : {e}",
                    color=discord.Color.red(),
                ),
                ephemeral=True
            )


class RaidConfigView(discord.ui.View):
    def __init__(self, cog, guild_id):
        super().__init__()
        self.cog = cog
        self.guild_id = guild_id

    @discord.ui.button(label="Configurer", style=discord.ButtonStyle.primary)
    async def configure_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Ouvre le modal de configuration."""
        await interaction.response.send_modal(RaidConfigModal(self.cog, self.guild_id))


class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raid_data = load_raid_data()
        self.join_logs = {}  # Suivi des joins par serveur
        self.message_logs = {}  # Suivi des messages pour l'anti-spam

    async def ensure_guild_data(self, guild_id):
        """Créer une configuration par défaut si elle n'existe pas."""
        guild_id = str(guild_id)
        if guild_id not in self.raid_data:
            self.raid_data[guild_id] = {
                "enabled": False,
                "max_joins": 5,
                "time_interval": 10,
                "punishment": "kick",
                "anti_spam": {
                    "enabled": True,
                    "message_limit": 5,
                    "time_window": 10,
                    "punishment": "mute",
                },
            }
            save_raid_data(self.raid_data)

    @app_commands.command(name="raidprotect", description="Activer ou désactiver la protection antiraid.")
    @app_commands.choices(
        action=[
            app_commands.Choice(name="Activer", value="on"),
            app_commands.Choice(name="Désactiver", value="off")
        ]
    )
    async def raidprotect(self, interaction: discord.Interaction, action: app_commands.Choice[str]):
        
        async def check_permission(member: discord.Member) -> bool:
            return member.guild_permissions.administrator

        if not await check_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas la permission `Administrateur` !")
            return
        
        """Activer/désactiver la protection antiraid."""
        await self.ensure_guild_data(interaction.guild.id)
        guild_id = str(interaction.guild.id)

        if action.value == "on":
            self.raid_data[guild_id]["enabled"] = True
            save_raid_data(self.raid_data)
            await interaction.response.send_message("🛡️ Protection antiraid **activée**.", ephemeral=True)
        elif action.value == "off":
            self.raid_data[guild_id]["enabled"] = False
            save_raid_data(self.raid_data)
            await interaction.response.send_message("🛡️ Protection antiraid **désactivée**.", ephemeral=True)

    @app_commands.command(name="raid_config", description="Configurer les options de protection antiraid.")
    async def raid_config(self, interaction: discord.Interaction):
        
        async def check_permission(member: discord.Member) -> bool:
            return member.guild_permissions.administrator
        
        if not await check_permission(interaction.user):
            await interaction.response.send_message("❌ Vous n'avez pas la permission `Administrateur` !")
            return
        
        """Configurer les options via une interface utilisateur."""
        guild_id = str(interaction.guild.id)
        await self.ensure_guild_data(interaction.guild.id)

        embed = discord.Embed(
            title="Configuration Antiraid",
            description=(
                "Cliquez sur le bouton **Configurer** ci-dessous pour ouvrir le formulaire de configuration.\n\n"
                "Voici les options disponibles :\n"
                "**1. Limite de joins** : Nombre maximum de joins autorisés en un temps donné.\n"
                "**2. Intervalle** : Temps (en secondes) pendant lequel les joins sont comptabilisés.\n"
                "**3. Punition** : Action à appliquer en cas de détection de raid (kick, ban, mute).\n"
                "**4. Anti-Spam activé** : Activer ou désactiver l'anti-spam (true/false)."
            ),
            color=discord.Color.blue(),
        )

        await interaction.response.send_message(embed=embed, view=RaidConfigView(self, interaction.guild.id), ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Détecter les joins pour prévenir les raids."""
        guild_id = str(member.guild.id)
        await self.ensure_guild_data(member.guild.id)

        if not self.raid_data[guild_id]["enabled"]:
            return

        now = datetime.now()
        if guild_id not in self.join_logs:
            self.join_logs[guild_id] = []

        self.join_logs[guild_id].append(now)

        # Filtrer les joins dans la fenêtre temporelle
        self.join_logs[guild_id] = [
            join_time for join_time in self.join_logs[guild_id]
            if now - join_time < timedelta(seconds=self.raid_data[guild_id]["time_interval"])
        ]

        if len(self.join_logs[guild_id]) > self.raid_data[guild_id]["max_joins"]:
            punishment = self.raid_data[guild_id]["punishment"]
            if punishment == "kick":
                await member.kick(reason="Détection de raid")
            elif punishment == "ban":
                await member.ban(reason="Détection de raid")
            elif punishment == "mute":
                # Implémentez un rôle de mute si nécessaire
                pass

    @commands.Cog.listener()
    async def on_message(self, message):
        """Détecter le spam pour prévenir les abus."""
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        await self.ensure_guild_data(message.guild.id)

        anti_spam = self.raid_data[guild_id]["anti_spam"]
        if not anti_spam["enabled"]:
            return

        now = datetime.now()
        author_id = str(message.author.id)

        if guild_id not in self.message_logs:
            self.message_logs[guild_id] = {}

        if author_id not in self.message_logs[guild_id]:
            self.message_logs[guild_id][author_id] = []

        self.message_logs[guild_id][author_id].append(now)

        # Filtrer les messages dans la fenêtre temporelle
        self.message_logs[guild_id][author_id] = [
            msg_time for msg_time in self.message_logs[guild_id][author_id]
            if now - msg_time < timedelta(seconds=anti_spam["time_window"])
        ]

        if len(self.message_logs[guild_id][author_id]) > anti_spam["message_limit"]:
            punishment = anti_spam["punishment"]
            if punishment == "mute":
                # Implémentez un rôle de mute si nécessaire
                pass
            elif punishment == "kick":
                await message.author.kick(reason="Détection de spam")
            elif punishment == "ban":
                await message.author.ban(reason="Détection de spam")


async def setup(bot):
    await bot.add_cog(AntiRaid(bot))
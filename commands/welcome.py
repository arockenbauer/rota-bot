import discord
from discord.ext import commands
from discord import app_commands
import json

# Chargement ou création du fichier de configuration
CONFIG_FILE = "welcome.json"

def load_config():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    async def save_config(self):
        save_config(self.config)

    @app_commands.command(name="config_join", description="Configurer le système de bienvenue.")
    async def config_join(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Configure le système de bienvenue pour un serveur."""
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Vous devez être administrateur pour configurer cette fonctionnalité.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        self.config[guild_id] = {"channel_id": channel.id}

        await interaction.response.send_message("💬 Veuillez entrer le message de bienvenue à envoyer dans le salon spécifié (ou tapez `cancel` pour annuler). Vous pouvez utiliser les variables :"
                "\n- `{user.mention}` : Mentionne l'utilisateur."
                "\n- `{user.name}` : Nom de l'utilisateur sans mention."
                "\n- `{total_members}` : Nombre total de membres dans le serveur.", ephemeral=True)

        def check(m):
            return m.author == interaction.user and m.channel == interaction.channel

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=300)
            if msg.content.lower() == "cancel":
                await interaction.followup.send("❌ Configuration annulée.", ephemeral=True)
                return
            self.config[guild_id]["welcome_message"] = msg.content

            # Supprimer le message d'entrée pour libérer l'espace
            await msg.delete()

            # Demander si un lien d'invitation doit être envoyé
            embed = discord.Embed(
                title="🔗 Lien d'invitation",
                description="Souhaitez-vous envoyer un lien d'invitation inexpirable à l'utilisateur qui rejoint ?",
                color=discord.Color.blurple()
            )
            view = ConfirmationView()
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            await view.wait()

            if view.value:
                self.config[guild_id]["send_invite"] = True
                invite = await channel.create_invite(max_age=0, max_uses=0, unique=False)
                self.config[guild_id]["invite_link"] = str(invite)
            else:
                self.config[guild_id]["send_invite"] = False

            # Demander le message en MP
            await interaction.followup.send(
                "💌 Entrez le message à envoyer en MP lorsque quelqu'un rejoint. Vous pouvez utiliser les variables :"
                "\n- `{user.mention}` : Mentionne l'utilisateur."
                "\n- `{user.name}` : Nom de l'utilisateur sans mention."
                "\n- `{total_members}` : Nombre total de membres dans le serveur."
                "\nTapez `none` pour désactiver cette option.",
                ephemeral=True
            )
            msg = await self.bot.wait_for("message", check=check, timeout=300)
            if msg.content.lower() == "none":
                self.config[guild_id]["dm_message"] = None
            else:
                self.config[guild_id]["dm_message"] = msg.content

            await msg.delete()

            # Demander si les membres peuvent dire coucou
            embed = discord.Embed(
                title="👋 Message de bienvenue",
                description="Souhaitez-vous autoriser les membres à dire coucou aux nouveaux arrivants via un bouton sur le message de bienvenue ?",
                color=discord.Color.blurple()
            )
            view = ConfirmationView()
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            await view.wait()

            self.config[guild_id]["enable_greetings"] = view.value

            # Sauvegarder la configuration
            await self.save_config()
            await interaction.followup.send("✅ Configuration enregistrée avec succès.", ephemeral=True)

        except discord.Forbidden:
            await interaction.followup.send("❌ Je n'ai pas la permission nécessaire pour créer des liens d'invitation.")
        except TimeoutError:
            await interaction.followup.send("⏳ Temps écoulé. Configuration annulée.", ephemeral=True)

    @app_commands.command(name="remove_join", description="Désactiver le système de bienvenue.")
    async def remove_join(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message("❌ Vous devez être administrateur pour désactiver cette fonctionnalité.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        if guild_id in self.config:
            del self.config[guild_id]
            await self.save_config()
            await interaction.response.send_message("✅ Système de bienvenue désactivé.", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Le système de bienvenue n'est pas activé pour ce serveur.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.config:
            return

        config = self.config[guild_id]
        channel = self.bot.get_channel(config["channel_id"])
        if not channel:
            return

        # Envoyer le message de bienvenue dans le salon
        if "welcome_message" in config:
            message = config["welcome_message"].format(
                user=member,
                total_members=member.guild.member_count
            )
            view = GreetingView() if config.get("enable_greetings") else None
            await channel.send(message, view=view)

        # Envoyer un message en MP
        if config.get("dm_message"):
            dm_message = config["dm_message"].format(
                user=member,
                total_members=member.guild.member_count
            )
            try:
                await member.send(dm_message)
            except discord.Forbidden:
                pass

        # Envoyer un lien d'invitation en MP
        if config.get("send_invite"):
            try:
                await member.send(f"Voici un lien d'invitation au cas où : {config['invite_link']}")
            except discord.Forbidden:
                pass

class ConfirmationView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Oui", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

    @discord.ui.button(label="Non", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()

class GreetingView(discord.ui.View):
    @discord.ui.button(label="Faire coucou", style=discord.ButtonStyle.primary)
    async def say_hello(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"👋 {interaction.user.mention} vous souhaite la bienvenue !")

# Ajouter la classe au bot
async def setup(bot):
    await bot.add_cog(Welcome(bot))
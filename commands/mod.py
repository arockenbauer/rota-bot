import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Modération(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Supprime un certain nombre de messages dans le salon spécifié.")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(thinking=True, ephemeral=True)
        """Supprime un certain nombre de messages dans le salon spécifié."""
        try:
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.followup.send(
                    "⚠️ Vous n'avez pas la permission de gérer les messages.", ephemeral=True
                )
                return

            if amount < 1 or amount > 100:
                await interaction.followup.send(
                    "⚠️ Veuillez spécifier un nombre entre 1 et 100.", ephemeral=True
                )
                return

            await interaction.channel.purge(limit=amount)
            await interaction.followup.send(f"✅ {amount} messages ont été supprimés.", ephemeral=True)
        except Exception as e:
            print(e)

    @app_commands.command(name="warn", description="Envoie un avertissement en message privé à un utilisateur.")
    @app_commands.default_permissions(kick_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        """Envoie un avertissement en message privé à un utilisateur."""
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(
                "⚠️ Vous n'avez pas la permission d'envoyer des avertissements.", ephemeral=True
            )
            return

        await user.send(f"⚠️ Avertissement : {reason if reason else 'Aucune raison spécifiée'}")
        await interaction.response.send_message(f"📬 Avertissement envoyé à {user.mention}.", ephemeral=True)

    @app_commands.command(name="ban", description="Bannit un utilisateur spécifié.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        """Bannit un utilisateur du serveur."""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "⚠️ Vous n'avez pas la permission de bannir des membres.", ephemeral=True
            )
            return

        await member.ban(reason=reason)
        await interaction.response.send_message(
            f":hammer: {member.mention} a été banni. Raison : {reason if reason else 'Aucune raison spécifiée'}"
        )

    @app_commands.command(name="unban", description="Débannit un utilisateur à l'aide de son nom ou de son ID Discord.")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        """Débannit un utilisateur du serveur."""
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(
                "⚠️ Vous n'avez pas la permission de débannir des membres.", ephemeral=True
            )
            return

        await interaction.guild.unban(user)
        await interaction.response.send_message(f"🔓 {user.mention} a été débanni.")

    @app_commands.command(name="mute", description="Réduit au silence un utilisateur avec ou sans rôle Muted existant.")
    @app_commands.default_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = None):
        """Réduit au silence un utilisateur avec ou sans rôle Muted existant."""
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "⚠️ Vous n'avez pas la permission de gérer les rôles.", ephemeral=True
            )
            return

        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await interaction.guild.create_role(name="Muted")
            for channel in interaction.guild.text_channels:
                await channel.set_permissions(mute_role, send_messages=False)

        await member.add_roles(mute_role)
        await interaction.response.send_message(
            f"🔇 {member.mention} a été muté pour {duration} secondes." if duration else f"🔇 {member.mention} a été mute."
        )
        if duration:
            await asyncio.sleep(duration)
            await member.remove_roles(mute_role)

    @app_commands.command(name="unmute", description="Retire le mute d'un utilisateur.")
    @app_commands.default_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        """Retire le mute d'un utilisateur."""
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(
                "⚠️ Vous n'avez pas la permission de gérer les rôles.", ephemeral=True
            )
            return

        mute_role = discord.utils.get(interaction.guild.roles, name="Muted")
        if mute_role in member.roles:
            await member.remove_roles(mute_role)
            await interaction.response.send_message(f"🔊 {member.mention} a été démute.")
        else:
            await interaction.response.send_message(
                f"⚠️ {member.mention} n'a pas le rôle Muted.", ephemeral=True
            )
            
    @app_commands.command(name="candid", description="Envoie la candidature pour Helpeur, Modérateur ou Admin")
    @app_commands.choices(
        type=[
            app_commands.Choice(name="Helpeur", value="helpeur"),
            app_commands.Choice(name="Modérateur", value="moderateur"),
            app_commands.Choice(name="Admin", value="admin"),
        ]
    )
    async def candid(self, interaction: discord.Interaction, type: app_commands.Choice[str]):
        # Templates de candidature
        templates = {
            "helpeur": (
                "**Candidature pour devenir Helpeur :**\n\n"
                "- Pourquoi voulez-vous devenir Helpeur ?\n"
                "- Quelles sont vos disponibilités ?\n"
                "- Avez-vous de l'expérience dans ce rôle ? Si oui, laquelle ?\n"
                "- Que feriez-vous face à un membre ne respectant pas les règles ?"
            ),
            "moderateur": (
                "**Candidature pour devenir Modérateur :**\n\n"
                "- Pourquoi voulez-vous devenir Modérateur ?\n"
                "- Quelles sont vos forces pour ce rôle ?\n"
                "- Avez-vous déjà modéré un serveur Discord ?\n"
                "- Décrivez votre réaction face à une situation conflictuelle entre membres."
            ),
            "admin": (
                "**Candidature pour devenir Admin :**\n\n"
                "- Pourquoi pensez-vous être qualifié(e) pour ce rôle ?\n"
                "- Quelle est votre vision pour l'amélioration du serveur ?\n"
                "- Avez-vous une expérience de gestion ou d'administration de communauté ?\n"
                "- Quels changements souhaiteriez-vous apporter au serveur ?"
            ),
        }

        # Récupère le template correspondant
        template = templates.get(type.value)

        # Envoie le message dans le salon où la commande a été utilisée
        await interaction.response.send_message(f"Voici la candidature :\n\n{template}")

async def setup(bot: commands.Bot):
    await bot.add_cog(Modération(bot))
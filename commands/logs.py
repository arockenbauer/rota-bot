import discord
from discord.ext import commands
from discord import app_commands, ui
import json
from pathlib import Path

# Chemin pour sauvegarder les configurations
CONFIG_FILE = Path("logs.json")

# Couleurs des embeds
green = discord.Colour(0x1ec300)
orange = discord.Colour(0xfeb100)
red = discord.Colour(0x970000)

LOG_TYPES = {
    "member_update": "majs membres",
    "server_update": "maj serveur",
    "message_edit": "messages edit",
    "message_delete": "messages supp",
}

class LogsCog(commands.Cog):
    try:
        def __init__(self, bot):
            self.bot = bot
            self.config = self.load_config()

        def load_config(self):
            """Charge la configuration depuis un fichier JSON."""
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            return {}

        def save_config(self):
            """Sauvegarde la configuration dans un fichier JSON."""
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)

        async def setup_log_channels(self, guild):
            """Configure les salons pour les logs dans la catégorie 'Rota Logs'."""
            guild_id = str(guild.id)
            self.config.setdefault(guild_id, {"enabled_logs": {}, "log_channels": {}})
            category = discord.utils.get(guild.categories, name="Rota Logs")

            if category is None:
                category = await guild.create_category("Rota Logs")

            for log_type in LOG_TYPES:
                if log_type not in self.config[guild_id]["log_channels"]:
                    channel = await guild.create_text_channel(
                        name=LOG_TYPES[log_type].replace(" ", "-").lower(), category=category
                    )
                    self.config[guild_id]["log_channels"][log_type] = channel.id

            self.save_config()

        async def get_log_channel(self, guild, log_type):
            """Récupère le salon de logs pour un type spécifique."""
            guild_id = str(guild.id)
            channel_id = self.config[guild_id]["log_channels"].get(log_type)
            if channel_id:
                return guild.get_channel(channel_id)
            return None

        async def send_log(self, guild, log_type, embed):
            """Envoie un embed dans le salon de logs correspondant."""
            channel = await self.get_log_channel(guild, log_type)
            if channel:
                await channel.send(embed=embed)
                
        @app_commands.command(name="remove_logs", description="Supprime les salons et la catégorie des logs.")
        @app_commands.default_permissions(administrator=True)
        async def remove_logs(self, interaction: discord.Interaction):
            try:
                await interaction.response.defer(thinking=True, ephemeral=True)
                guild = interaction.guild
                guild_id = str(guild.id)

                # Vérifie si la configuration existe pour cette guilde
                if guild_id not in self.config:
                    await interaction.followup.send("Aucune configuration de logs n'a été trouvée pour ce serveur.")
                    return

                # Demande de confirmation
                confirmation_message = await interaction.followup.send(
                    embed=discord.Embed(
                        title="Confirmation requise",
                        description="Êtes-vous sûr de vouloir supprimer tous les salons et la catégorie des logs ? Cette action est irréversible.",
                        color=discord.Color.orange(),
                    ),
                    ephemeral=True
                )
                await confirmation_message.add_reaction("✅")
                await confirmation_message.add_reaction("❌")

                def check(reaction, user):
                    return user == interaction.user and str(reaction.emoji) in ["✅", "❌"]

                try:
                    reaction, user = await self.client.wait_for("reaction_add", timeout=30.0, check=check)
                except asyncio.TimeoutError:
                    await interaction.followup.send("La demande de suppression a expiré.", ephemeral=True)
                    return

                if str(reaction.emoji) == "❌":
                    await interaction.followup.send("Annulation de la suppression des logs.", ephemeral=True)
                    return

                # Supprime les salons et la catégorie des logs
                category = discord.utils.get(guild.categories, name="Rota logs")
                if category:
                    for channel in category.channels:
                        try:
                            await channel.delete()
                        except discord.Forbidden:
                            await interaction.followup.send(f"Impossible de supprimer le salon {channel.name}. Vérifiez mes permissions.", ephemeral=True)
                    try:
                        await category.delete()
                    except discord.Forbidden:
                        await interaction.followup.send("Impossible de supprimer la catégorie des logs. Vérifiez mes permissions.", ephemeral=True)

                # Supprime la configuration des logs
                self.config.pop(guild_id, None)
                with open(self.config_file, "w") as f:
                    json.dump(self.config, f)

                await interaction.followup.send("Tous les salons et la catégorie des logs ont été supprimés avec succès.", ephemeral=True)

            except Exception as e:
                print(e)
                
        @app_commands.command(name="config_logs", description="Configure les logs pour ce serveur.")
        @app_commands.guild_only()
        async def config_logs(self, interaction: discord.Interaction):
            await interaction.response.defer(thinking=True)
            guild_id = str(interaction.guild.id)
            self.config.setdefault(guild_id, {"enabled_logs": {}, "log_channels": {}})
            await self.setup_log_channels(interaction.guild)

            view = LogConfigView(self, interaction.guild)
            await interaction.followup.send(
                "Choisissez les types de logs à activer ou désactiver :", view=view, ephemeral=True
            )

        @commands.Cog.listener()
        async def on_ready(self):
            print("Logs cog prêt.")

        @commands.Cog.listener()
        async def on_member_update(self, before, after):
            guild_id = str(before.guild.id)
            if not self.config[guild_id]["enabled_logs"].get("member_update", False):
                return

            if before.display_name != after.display_name:
                embed = discord.Embed(
                    title="Mise à jour de pseudo",
                    description=f"{after.mention} a changé son pseudo.",
                    color=orange,
                )
                embed.add_field(name="Avant", value=before.display_name, inline=True)
                embed.add_field(name="Après", value=after.display_name, inline=True)
                await self.send_log(after.guild, "member_update", embed)

            if before.roles != after.roles:
                removed_roles = [r.mention for r in before.roles if r not in after.roles]
                added_roles = [r.mention for r in after.roles if r not in before.roles]

                embed = discord.Embed(
                    title="Mise à jour des rôles",
                    description=f"Les rôles de {after.mention} ont changé.",
                    color=orange,
                )
                embed.add_field(name="Rôles ajoutés", value=", ".join(added_roles) or "Aucun", inline=False)
                embed.add_field(name="Rôles retirés", value=", ".join(removed_roles) or "Aucun", inline=False)
                await self.send_log(after.guild, "member_update", embed)

        @commands.Cog.listener()
        async def on_message_edit(self, before, after):
            if before.author.bot:
                return

            guild_id = str(before.guild.id)
            if not self.config[guild_id]["enabled_logs"].get("message_edit", False):
                return

            embed = discord.Embed(
                title="Message modifié",
                description=f"Un message de {before.author.mention} a été modifié dans {before.channel.mention}.",
                color=orange,
            )
            embed.add_field(name="Avant", value=before.content or "Aucun contenu", inline=False)
            embed.add_field(name="Après", value=after.content or "Aucun contenu", inline=False)
            await self.send_log(before.guild, "message_edit", embed)

        @commands.Cog.listener()
        async def on_message_delete(self, message):
            if message.author.bot:
                return

            guild_id = str(message.guild.id)
            if not self.config[guild_id]["enabled_logs"].get("message_delete", False):
                return

            embed = discord.Embed(
                title="Message supprimé",
                description=f"Un message de {message.author.mention} a été supprimé dans {message.channel.mention}.",
                color=red,
            )
            embed.add_field(name="Contenu", value=message.content or "Aucun contenu", inline=False)
            await self.send_log(message.guild, "message_delete", embed)

            @commands.Cog.listener()
            async def on_channel_create(self, channel):
                guild_id = str(channel.guild.id)
                if not self.config[guild_id]["enabled_logs"].get("channel_create", False):
                    return

                embed = discord.Embed(
                    title="Salon créé",
                    description=f"Un nouveau salon a été créé : {channel.mention}.",
                    color=green,
                )
                embed.add_field(name="Nom du salon", value=channel.name, inline=True)
                embed.add_field(name="Type", value=str(channel.type).capitalize(), inline=True)
                await self.send_log(channel.guild, "channel_create", embed)

            @commands.Cog.listener()
            async def on_channel_delete(self, channel):
                guild_id = str(channel.guild.id)
                if not self.config[guild_id]["enabled_logs"].get("channel_delete", False):
                    return

                embed = discord.Embed(
                    title="Salon supprimé",
                    description=f"Un salon a été supprimé : #{channel.name}.",
                    color=red,
                )
                embed.add_field(name="Nom du salon", value=channel.name, inline=True)
                embed.add_field(name="Type", value=str(channel.type).capitalize(), inline=True)
                await self.send_log(channel.guild, "channel_delete", embed)

            @commands.Cog.listener()
            async def on_role_create(self, role):
                guild_id = str(role.guild.id)
                if not self.config[guild_id]["enabled_logs"].get("role_create", False):
                    return

                embed = discord.Embed(
                    title="Rôle créé",
                    description=f"Un nouveau rôle a été créé : {role.mention}.",
                    color=green,
                )
                embed.add_field(name="Nom du rôle", value=role.name, inline=True)
                embed.add_field(name="Permissions", value=", ".join([p[0] for p in role.permissions if p[1]]) or "Aucune", inline=False)
                await self.send_log(role.guild, "role_create", embed)

            @commands.Cog.listener()
            async def on_role_delete(self, role):
                guild_id = str(role.guild.id)
                if not self.config[guild_id]["enabled_logs"].get("role_delete", False):
                    return

                embed = discord.Embed(
                    title="Rôle supprimé",
                    description=f"Un rôle a été supprimé : {role.name}.",
                    color=red,
                )
                embed.add_field(name="Nom du rôle", value=role.name, inline=True)
                await self.send_log(role.guild, "role_delete", embed)

            @commands.Cog.listener()
            async def on_member_ban(guild, member):
                try:
                    # Récupérer les logs d'audit pour l'action de ban
                    logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
                    channel = guild.get_channel(CHANNEL_ID)

                    # Vérifier si le membre banni correspond à celui de l'audit log
                    logs = logs[0]
                    if logs.target == member:
                        # Créer l'embed de log
                        embed = discord.Embed(
                            title="Membre banni",
                            description=f"{logs.target.mention} a été banni du serveur.",
                            color=discord.Color.red()
                        )
                        embed.add_field(name="Banni par", value=logs.user, inline=False)
                        embed.add_field(name="ID de l'utilisateur", value=logs.target.id, inline=False)
                        embed.add_field(name="Date du ban", value=logs.created_at, inline=False)

                        # Ajouter la raison si présente
                        if logs.reason:
                            embed.add_field(name="Raison", value=logs.reason, inline=False)

                        # Envoyer l'embed dans le salon des logs
                        await channel.send(embed=embed)
                except Exception as e:
                    print(e)

            @commands.Cog.listener()
            async def on_member_unban(guild, member):
                # Récupérer les logs d'audit pour l'action de déban
                logs = await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
                channel = guild.get_channel(CHANNEL_ID)

                # Vérifier si le membre débanni correspond à celui de l'audit log
                logs = logs[0]
                if logs.target == member:
                    # Créer l'embed de log
                    embed = discord.Embed(
                        title="Membre débanni",
                        description=f"{logs.target.mention} a été débanni du serveur.",
                        color=discord.Color.green()
                    )
                    embed.add_field(name="Débanni par", value=logs.user, inline=False)
                    embed.add_field(name="ID de l'utilisateur", value=logs.target.id, inline=False)
                    embed.add_field(name="Date du déban", value=logs.created_at, inline=False)

                    # Envoyer l'embed dans le salon des logs
                    await channel.send(embed=embed)



        @commands.Cog.listener()
        async def on_voice_state_update(self, member, before, after):
            guild_id = str(member.guild.id)
            if not self.config[guild_id]["enabled_logs"].get("voice_update", False):
                return

            if before.channel != after.channel:
                embed = discord.Embed(
                    title="Changement de salon vocal",
                    description=f"{member.mention} a changé de salon vocal.",
                    color=orange,
                )
                embed.add_field(name="Avant", value=before.channel.name if before.channel else "Aucun", inline=True)
                embed.add_field(name="Après", value=after.channel.name if after.channel else "Aucun", inline=True)
                await self.send_log(member.guild, "voice_update", embed)

            if before.mute != after.mute:
                action = "muté" if after.mute else "démuté"
                embed = discord.Embed(
                    title="Mise à jour de l'état vocal",
                    description=f"{member.mention} a été {action}.",
                    color=orange,
                )
                await self.send_log(member.guild, "voice_update", embed)

            if before.deaf != after.deaf:
                action = "sourdé" if after.deaf else "désourdé"
                embed = discord.Embed(
                    title="Mise à jour de l'état auditif",
                    description=f"{member.mention} a été {action}.",
                    color=orange,
                )
                await self.send_log(member.guild, "voice_update", embed)
                
        @commands.Cog.listener()
        async def on_voice_state_update(self, member, before, after):
            guild_id = str(member.guild.id)
            if not self.config[guild_id]["enabled_logs"].get("voice_mute", False):
                return

            # Mute/Demute Microphone
            if before.self_mute != after.self_mute:
                if after.self_mute:
                    action = "a mute son micro"
                    color = red
                else:
                    action = "a demute son micro"
                    color = green

                embed = discord.Embed(
                    title="Microphone",
                    description=f"{member.mention} {action}.",
                    color=color,
                )
                embed.set_author(name=member.name, icon_url=member.avatar.url)
                await self.send_log(member.guild, "voice_mute", embed)

            # Mute/Demute Casque (Deafen)
            if before.self_deaf != after.self_deaf:
                if after.self_deaf:
                    action = "a mute son casque"
                    color = red
                else:
                    action = "a demute son casque"
                    color = green

                embed = discord.Embed(
                    title="Casque",
                    description=f"{member.mention} {action}.",
                    color=color,
                )
                embed.set_author(name=member.name, icon_url=member.avatar.url)
                await self.send_log(member.guild, "voice_mute", embed)

    except Exception as e:
        print(e)
    
class LogConfigView(ui.View):
    def __init__(self, cog: LogsCog, guild: discord.Guild):
        super().__init__()
        self.cog = cog
        self.guild = guild
        guild_id = str(guild.id)
        self.config = cog.config.setdefault(guild_id, {"enabled_logs": {}, "log_channels": {}})

        for log_type, label in LOG_TYPES.items():
            self.add_item(LogToggleButton(log_type, label, cog, guild))

class LogToggleButton(ui.Button):
    def __init__(self, log_type: str, label: str, cog: LogsCog, guild: discord.Guild):
        self.log_type = log_type
        self.cog = cog
        self.guild = guild
        guild_id = str(guild.id)
        enabled = cog.config[guild_id]["enabled_logs"].get(log_type, False)

        super().__init__(
            label=label,
            style=discord.ButtonStyle.success if enabled else discord.ButtonStyle.secondary,
        )

    async def callback(self, interaction: discord.Interaction):
        guild_id = str(self.guild.id)
        enabled_logs = self.cog.config[guild_id]["enabled_logs"]
        enabled_logs[self.log_type] = not enabled_logs.get(self.log_type, False)

        self.style = discord.ButtonStyle.success if enabled_logs[self.log_type] else discord.ButtonStyle.secondary
        self.cog.save_config()

        await interaction.response.edit_message(view=self.view)

async def setup(bot):
    await bot.add_cog(LogsCog(bot))
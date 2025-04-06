import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Fichier de stockage
DATA_FILE = "bump.json"

# Charger les données depuis le fichier JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

# Sauvegarder les données dans le fichier JSON
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

class Bump(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()  # Charger les données au démarrage

    @app_commands.command(name="setbump", description="Définit le salon où les bumps arriveront.")
    @app_commands.default_permissions(manage_guild=True)
    async def setbump(self, interaction: discord.Interaction, channel: discord.TextChannel):
        guild_id = str(interaction.guild.id)
        self.data[guild_id] = self.data.get(guild_id, {})
        self.data[guild_id]["bump_channel"] = channel.id
        save_data(self.data)
        await interaction.response.send_message(
            f"✅ Salon de bump défini sur {channel.mention}.", ephemeral=True
        )

    @app_commands.command(name="config", description="Définit le message envoyé lors d'un bump.")
    @app_commands.default_permissions(manage_guild=True)
    async def config(self, interaction: discord.Interaction):
        """Configurer le message de description du serveur."""
        await interaction.response.send_message(
            "📋 Veuillez envoyer le message de bump que vous souhaitez utiliser dans les 60 secondes.", ephemeral=True
        )

        def check(msg):
            return (
                msg.author == interaction.user
                and msg.channel == interaction.channel
                and msg.content
            )

        try:
            msg = await self.bot.wait_for("message", timeout=60, check=check)
            # Vérifier si le message contient un ping
            if "@everyone" in msg.content or "@here" in msg.content or any(f"<@{member.id}>" in msg.content for member in interaction.guild.members):
                await interaction.followup.send(
                    "⚠️ Le message de bump ne peut pas contenir de mentions (@everyone, @here ou mentions de membres). Veuillez réessayer.",
                    ephemeral=True
                )
                return

            guild_id = str(interaction.guild.id)
            self.data[guild_id] = self.data.get(guild_id, {})
            self.data[guild_id]["bump_message"] = msg.content
            save_data(self.data)
            await msg.delete()
            await interaction.followup.send("✅ Message de bump configuré avec succès.", ephemeral=True)
        except asyncio.TimeoutError:
            await interaction.followup.send("⏰ Temps écoulé, veuillez réessayer.", ephemeral=True)

    @app_commands.command(name="bump", description="Bump le serveur")
    async def bump(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        guild_id = str(interaction.guild.id)
        guild_data = self.data.get(guild_id)

        # Vérifier si le serveur qui initie le bump est correctement configuré
        if not guild_data or "bump_channel" not in guild_data or "bump_message" not in guild_data:
            await interaction.followup.send(
                "⚠️ Le bump n'est pas configuré pour ce serveur. Utilisez `/setbump` et `/config` pour configurer.",
                ephemeral=True,
            )
            return

        # Vérifier le cooldown pour le serveur qui initie le bump
        now = time.time()
        last_bump = guild_data.get("last_bump", 0)
        cooldown = 3600  # 1 heure

        if now - last_bump < cooldown:
            time_left = int(cooldown - (now - last_bump))
            minutes, seconds = divmod(time_left, 60)
            await interaction.followup.send(
                embed=discord.Embed(
                    title="⏳ Pas si vite !",
                    description=(
                        f"Vous devez attendre encore **{minutes} minutes et {seconds} secondes** "
                        f"avant de pouvoir effectuer un nouveau bump."
                    ),
                    color=discord.Color.orange(),
                )
            )
            return

        # Créer un lien d'invitation pour le serveur qui initie le bump
        invite = await interaction.channel.create_invite(max_age=0, max_uses=0, unique=True)

        # Récupérer le message de bump du serveur d'origine
        bump_message = guild_data["bump_message"]

        # Récupérer la liste des serveurs
        servers = list(self.data.items())
        total_servers = len(servers)

        # Diviser les serveurs en lots de 50
        max_threads = 25
        server_batches = [
            servers[i : i + max_threads] for i in range(0, total_servers, max_threads)
        ]

        # Message de progression initial
        progress_msg = await interaction.followup.send(embed=discord.Embed(
            title="📤 Bump en cours...",
            description=f"0/{total_servers} serveurs bumpés\n🕒 Préparation...",
            color=discord.Color.blue(),
        ))

        bumped_servers = []
        failed_servers = []

        # Fonction d'envoi dans un serveur
        async def send_bump(guild_id, guild_data):
            if "bump_channel" not in guild_data:
                return False

            bump_channel = self.bot.get_channel(guild_data["bump_channel"])
            if not bump_channel:
                return False

            try:
                bump_embed=discord.Embed(title="Nouveau bump !", description=bump_message, color=0x00ff00)

                await bump_channel.send(embed=bump_embed, content=invite.url)
                return True
            except Exception as e:
                print(f"Erreur pour le serveur {guild_id}: {e}")
                return False

        # Gérer les threads
        async def handle_batch(batch):
            futures = []
            for guild_id, guild_data in batch:
                futures.append(send_bump(guild_id, guild_data))

            results = await asyncio.gather(*futures)
            for idx, result in enumerate(results):
                guild_id = batch[idx][0]
                if result:
                    bumped_servers.append(int(guild_id))
                else:
                    failed_servers.append(int(guild_id))

        # Processus par lots
        completed = 0
        for i, batch in enumerate(server_batches, start=1):
            await handle_batch(batch)

            completed += len(batch)
            progress = completed / total_servers
            progress_embed = discord.Embed(
                title="📤 Bump en cours...",
                description=f"{completed}/{total_servers} serveurs bumpés\n"
                            + "▓" * int(progress * 20) + "░" * (20 - int(progress * 20)),
                color=discord.Color.blue(),
            )
            await progress_msg.edit(embed=progress_embed)

        # Mise à jour du cooldown
        self.data[guild_id]["last_bump"] = now
        save_data(self.data)

        # Résumé final
        success_count = len(bumped_servers)
        failure_count = len(failed_servers)
        final_embed = discord.Embed(
            title="🎉 Serveur bumpé !",
            description="Voici les résultats du bump :",
            color=discord.Color.green(),
        )
        final_embed.add_field(
            name="✅ Succès",
            value=f"{success_count} serveurs ont reçu le bump avec succès.",
            inline=False,
        )
        if failed_servers:
            final_embed.add_field(
                name="⚠️ Échecs",
                value=f"{failure_count} serveurs n'ont pas pu être bumpés.\n",
                inline=False,
            )
        else:
            final_embed.add_field(
                name="⚠️ Échecs",
                value="Aucun échec ! Tous les serveurs ont reçu le bump.",
                inline=False,
            )
        final_embed.set_footer(text=f"Bumpé par {interaction.user}", icon_url=interaction.user.avatar.url)

        await progress_msg.edit(embed=final_embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Bump(bot))
import discord
from discord.ext import commands, tasks
from discord import app_commands
import json
from datetime import datetime, timedelta
import re
import time  # Utilisé pour générer des timestamps Discord

class Rappel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_path = "rappels.json"
        self.load_rappels()
        self.check_rappels.start()  # Démarre la tâche qui vérifie les rappels

    def load_rappels(self):
        """Charge les rappels depuis le fichier JSON."""
        try:
            with open(self.file_path, "r") as f:
                self.rappels = json.load(f)
        except FileNotFoundError:
            self.rappels = {}

    def save_rappels(self):
        """Sauvegarde les rappels dans le fichier JSON."""
        with open(self.file_path, "w") as f:
            json.dump(self.rappels, f, indent=4)

    def parse_time(self, time_str):
        """Parse une chaîne de temps sous la forme '1d', '2h', '3m', etc., et retourne un timedelta."""
        pattern = r"(\d+)([d,h,m,s,mo,y])"
        match = re.match(pattern, time_str)
        if not match:
            return None
        value, unit = match.groups()
        value = int(value)

        if unit == "d":
            return timedelta(days=value)
        elif unit == "h":
            return timedelta(hours=value)
        elif unit == "m":
            return timedelta(minutes=value)
        elif unit == "s":
            return timedelta(seconds=value)
        elif unit == "mo":
            return timedelta(days=value * 30)  # Approximation 1 mois = 30 jours
        elif unit == "y":
            return timedelta(days=value * 365)  # Approximation 1 an = 365 jours

    @tasks.loop(seconds=1)  # Vérifie les rappels toutes les 1 seconde
    async def check_rappels(self):
        """Vérifie et envoie les rappels arrivés à échéance."""
        now = datetime.now().timestamp()
        to_delete = []

        for user_id, user_rappels in self.rappels.items():
            for title, data in list(user_rappels.items()):
                rappel_time = datetime.strptime(data["date"], "%Y-%m-%d %H:%M").timestamp()
                if rappel_time <= now:
                    user = self.bot.get_user(int(user_id))
                    if user:
                        embed = discord.Embed(
                            title=f"🔔 Rappel: {title}",
                            description=f"**Raison:** {data['raison']}\n**Échéance:** <t:{int(rappel_time)}:F>",
                            color=discord.Color.green()
                        )
                        await user.send(embed=embed)
                    to_delete.append((user_id, title))

        # Supprime les rappels envoyés
        for user_id, title in to_delete:
            del self.rappels[user_id][title]
            if not self.rappels[user_id]:  # Si l'utilisateur n'a plus de rappels, supprime l'entrée
                del self.rappels[user_id]

        self.save_rappels()

    @app_commands.command(name="rappel", description="Gestion des rappels.")
    @app_commands.describe(action="L'action à effectuer sur les rappels: créer, lister, modifier ou supprimer")
    @app_commands.choices(action=[
        app_commands.Choice(name="Créer", value="creer"),
        app_commands.Choice(name="Lister", value="lister"),
        app_commands.Choice(name="Modifier", value="modifier"),
        app_commands.Choice(name="Supprimer", value="supprimer")
    ])
    async def rappel(self, interaction: discord.Interaction, action: str, raison: str = None, temps: str = None):
        """Commande pour gérer les rappels"""
        user_id = str(interaction.user.id)

        if action == "creer":
            if not raison or not temps:
                await interaction.response.send_message("❌ Vous devez spécifier une raison et un délai de rappel.", ephemeral=True)
                return
            
            time_delta = self.parse_time(temps)
            if not time_delta:
                await interaction.response.send_message("❌ Le format du délai est invalide. Utilisez des unités comme '1d' pour 1 jour, '1h' pour 1 heure, etc.", ephemeral=True)
                return

            # Calcul de la date d'échéance
            date_obj = datetime.now() + time_delta
            discord_timestamp = int(date_obj.timestamp())
            if user_id not in self.rappels:
                self.rappels[user_id] = {}

            # Ajout du rappel dans le dictionnaire de l'utilisateur
            self.rappels[user_id][raison] = {
                "raison": raison,
                "date": date_obj.strftime("%Y-%m-%d %H:%M")
            }
            self.save_rappels()

            embed = discord.Embed(
                title=f"✅ Rappel créé",
                description=f"**Raison:** {raison}\n**Délai:** {temps}\n**Échéance:** <t:{discord_timestamp}:F>",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)

        elif action == "lister":
            if user_id not in self.rappels or not self.rappels[user_id]:
                await interaction.response.send_message("❌ Aucun rappel trouvé.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="📋 Liste de vos rappels",
                color=discord.Color.orange()
            )
            for title, data in self.rappels[user_id].items():
                rappel_time = datetime.strptime(data["date"], "%Y-%m-%d %H:%M").timestamp()
                embed.add_field(
                    name=f"📌 {title}",
                    value=f"**Raison:** {data['raison']}\n**Échéance:** <t:{int(rappel_time)}:F>",
                    inline=False
                )
            await interaction.response.send_message(embed=embed)

        elif action == "modifier":
            if not raison or not temps:
                await interaction.response.send_message("❌ Vous devez spécifier une raison et un nouveau délai pour modifier un rappel.", ephemeral=True)
                return

            if user_id not in self.rappels or raison not in self.rappels[user_id]:
                await interaction.response.send_message(f"❌ Aucun rappel trouvé avec la raison '{raison}'.", ephemeral=True)
                return

            time_delta = self.parse_time(temps)
            if not time_delta:
                await interaction.response.send_message("❌ Le format du délai est invalide. Utilisez des unités comme '1d' pour 1 jour, '1h' pour 1 heure, etc.", ephemeral=True)
                return

            # Modification du rappel
            date_obj = datetime.now() + time_delta
            discord_timestamp = int(date_obj.timestamp())
            self.rappels[user_id][raison] = {
                "raison": raison,
                "date": date_obj.strftime("%Y-%m-%d %H:%M")
            }
            self.save_rappels()

            embed = discord.Embed(
                title=f"✅ Rappel modifié",
                description=f"**Raison:** {raison}\n**Nouveau délai:** {temps}\n**Nouvelle échéance:** <t:{discord_timestamp}:F>",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        elif action == "supprimer":
            if not raison:
                await interaction.response.send_message("❌ Vous devez spécifier une raison pour supprimer un rappel.", ephemeral=True)
                return

            if user_id not in self.rappels or raison not in self.rappels[user_id]:
                await interaction.response.send_message(f"❌ Aucun rappel trouvé avec la raison '{raison}'.", ephemeral=True)
                return

            del self.rappels[user_id][raison]
            if not self.rappels[user_id]:  # Si l'utilisateur n'a plus de rappels, supprime l'entrée
                del self.rappels[user_id]

            self.save_rappels()

            embed = discord.Embed(
                title=f"✅ Rappel supprimé",
                description=f"Le rappel '{raison}' a été supprimé avec succès.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

        else:
            await interaction.response.send_message("❌ Action invalide. Utilisez 'creer', 'lister', 'modifier' ou 'supprimer'.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Rappel(bot))


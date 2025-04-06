print("[+] Initialisation des modules...")

print("[+] Initialisation du module discord...")
import discord
print("[+] Initialisation du module discord.ext...")
from discord.ext import commands
print("[+] Initialisation du module asyncio...")
import asyncio
print("[+] Initialisation du module json...")
import json
print("[+] Initialisation du module ...os")
import os
print("[+] Modules chargés !")

print("[+] Initialisation du bot...")

# Chargement des configurations depuis config.json
with open("config.json", "r") as config_file:
    config = json.load(config_file)

TOKEN = config["token"]  # Token du bot extrait du fichier config.json

# Initialisation du bot avec une synchronisation des commandes slash
class CustomBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()  # Toutes les permissions d'intention sont activées
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        # Définition des dossiers principaux à explorer
        base_directories = ["commands", "commands/think"]

        for base_dir in base_directories:
            if os.path.isdir(base_dir):  # Vérifie si le répertoire existe
                for root, _, files in os.walk(base_dir):  # Explore récursivement les sous-dossiers
                    for file in files:
                        if file.endswith(".py") and not file.startswith("__"):
                            relative_path = os.path.relpath(root, ".")  # Chemin relatif depuis le dossier actuel
                            module_name = f"{relative_path.replace(os.sep, '.')}.{file[:-3]}"  # Conversion en import Python
                            try:
                                await self.load_extension(module_name)
                                print(f"L'extension {module_name} a été chargée avec succès.")
                            except Exception as e:
                                print(f"Erreur lors du chargement de l'extension {module_name}: {e}")

        # Synchronisation des commandes avec Discord
        try:
            synced = await self.tree.sync()  # Synchronisation des commandes Slash
            print(f"Commandes Slash synchronisées : {len(synced)}")
        except Exception as e:
            print(f"Erreur lors de la synchronisation des commandes Slash : {e}")

# Initialisation du bot
bot = CustomBot()

# Événement déclenché lorsque le bot est prêt
@bot.event
async def on_ready():
    print(f"Bot connecté en tant que {bot.user} et prêt à l'utilisation.")

# Fonction principale pour démarrer le bot
async def main():
    async with bot:
        await bot.start(TOKEN)

print("[+] Démarrage du bot...")
        
try:
    # Démarrage du bot
    asyncio.run(main())
except KeyboardInterrupt:
    print("[+] Bot arrêté !")
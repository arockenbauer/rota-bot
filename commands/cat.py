import discord
import asyncio
import json
import random
import aiohttp
from discord.ext import commands
from discord import app_commands

class Cat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cat", description="Une commande qui envoie une image de chat aléatoire.")
    async def cat(self, interaction: discord.Interaction):
        try:
            # Indiquer à Discord que le bot réfléchit
            await interaction.response.defer(thinking=True)

            # Définir l'URL de l'API
            url = "https://api.thecatapi.com/v1/images/search?limit=10"

            # Vérifier si le fichier cats.json existe et le charger, sinon faire la requête à l'API
            try:
                with open('cats.json', 'r') as f:
                    cats_data = json.load(f)
            except FileNotFoundError:
                # Si le fichier n'existe pas, on fait une requête à l'API
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 429:
                            # Si on reçoit une erreur 429, on ignore la requête et sélectionne une image aléatoire
                            random_cat = random.choice(cats_data)  # Sélectionner un chat déjà dans le fichier
                            cat_url = random_cat['url']
                            embed = discord.Embed(title="Voici un chat ! 🐱", description="Un chat mignon pour toi !", color=0x3498db)
                            embed.set_image(url=cat_url)
                            await interaction.followup.send(embed=embed)
                            return
                        else:
                            # Si la réponse est valide, récupérer les données
                            new_cats_data = await response.json()
                            # Sauvegarder les résultats dans le fichier JSON
                            with open('cats.json', 'w') as f:
                                json.dump(new_cats_data, f)
                            cats_data = new_cats_data

            # Faire une requête à l'API pour obtenir de nouvelles images (si aucune erreur 429)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 429:
                            # Si on reçoit une erreur 429, on ignore la requête et sélectionne une image aléatoire
                            random_cat = random.choice(cats_data)  # Sélectionner un chat déjà dans le fichier
                            cat_url = random_cat['url']
                            embed = discord.Embed(title="Voici un chat ! 🐱", description="Un chat mignon pour toi !", color=0x3498db)
                            embed.set_image(url=cat_url)
                            await interaction.followup.send(embed=embed)
                            return
                        else:
                            new_cats_data = await response.json()

                # Ajouter les nouvelles images au fichier sans doublons
                for new_cat in new_cats_data:
                    if new_cat not in cats_data:
                        cats_data.append(new_cat)

                # Sauvegarder les résultats mis à jour dans le fichier JSON
                with open('cats.json', 'w') as f:
                    json.dump(cats_data, f)

            except Exception as e:
                print(f"Erreur lors de la requête API: {e}")

            # Sélectionner un chat aléatoire
            random_cat = random.choice(cats_data)
            cat_url = random_cat['url']

            # Créer un embed avec l'image du chat
            embed = discord.Embed(title="Voici un chat ! 🐱", description="Un chat mignon pour toi !", color=0x3498db)
            embed.set_image(url=cat_url)

            # Répondre à l'interaction avec l'embed
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Cat(bot))
import discord
import json
import asyncio
from discord.ext import commands
from discord import app_commands
import requests

# Chargement du token depuis token.json
with open('token.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']

class ChatBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cooldowns = {}

    async def check_cooldown(self, user_id):
        try:
            now = discord.utils.utcnow().timestamp()  # Obtention du timestamp actuel
            if user_id in self.cooldowns:
                if now - self.cooldowns[user_id] < 60:
                    return False  # Trop de demandes
            self.cooldowns[user_id] = now
            return True
        except Exception as e:
            print(e)

    @app_commands.command(name="chatbot", description="Définir un salon chatbot pour le serveur.")
    @app_commands.default_permissions(administrator=True)
    async def chatbot_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        with open(f'settings/{interaction.guild.id}_chatbot.json', 'w') as f:
            json.dump({'channel_id': channel.id}, f)

        await interaction.response.send_message(f"Salon chatbot défini sur : {channel.mention}")

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            channel = message.channel
            if message.guild:
                try:
                    with open(f'settings/{message.guild.id}_chatbot.json', 'r') as f:
                        data = json.load(f)
                        channel_id = data['channel_id']

                        if message.channel.id == channel_id and not message.author.bot:
                            if not await self.check_cooldown(message.author.id):
                                await message.reply('Vous posez des questions trop vite ! Une question par minute maximum')
                                return
                            
                            def removepub(message):
                                text_to_remove = "-# Utilisation de l'API gratuite de [SkyWay](<https://www.skyway-bot.fr/>)"
                                return message.replace(text_to_remove, '')
                            
                            try:
                                response = requests.post(
                                    'https://api.skyway-bot.fr/v1/gpt',
                                    json={"content": message.content},
                                    headers={"Authorization": f"{TOKEN}"}
                                )
                                response_data = response.json()
                                response = removepub(response_data['content'])
                                await message.reply(response)
                                print(f'[INFO] Réponse envoyée à la question : {message.content}')
                            except requests.exceptions.RequestException as error:
                                print(f'[ERREUR] {str(error)}')
                                await message.reply('Une erreur est survenue lors du traitement de votre demande.')
                except FileNotFoundError as e:

                    return

        except Exception as e:
            print(e)
            
async def setup(bot):
    await bot.add_cog(ChatBot(bot))
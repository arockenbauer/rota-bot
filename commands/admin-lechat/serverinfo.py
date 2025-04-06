import discord
from discord.ext import commands
from discord.ext.commands import Bot

class ServerInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Vérification du préfixe et si l'utilisateur est autorisé (whitelist)
        if message.content.lower().startswith("rb!serverinfo"):
            if message.author.id != 1161709894685179985:
                return
            
            # Extraction de l'ID du serveur
            content = message.content.split()
            if len(content) < 2:
                await message.channel.send("Veuillez spécifier l'ID du serveur.")
                return
            
            server_id = content[1]
            guild = self.bot.get_guild(int(server_id))
            
            if guild is None:
                await message.channel.send(f"Le serveur avec l'ID `{server_id}` n'a pas pu être trouvé.")
                return
            
            # Création de l'embed dynamique avec les informations du serveur
            embed = discord.Embed(
                title=f"Informations sur le serveur {guild.name}",
                description=f"Voici les informations pour le serveur `{guild.name}`.",
                color=discord.Color.blue()
            )
            embed.add_field(name="ID du serveur", value=guild.id, inline=False)
            embed.add_field(name="Propriétaire", value=f"{guild.owner} ({guild.owner.id})", inline=False)
            embed.add_field(name="Membres", value=guild.member_count, inline=False)
            #embed.add_field(name="Région", value=guild.region, inline=False)
            embed.add_field(name="Créé le", value=guild.created_at.strftime("%d/%m/%Y %H:%M:%S"), inline=False)
            embed.add_field(name="Nombre de salons", value=len(guild.text_channels) + len(guild.voice_channels), inline=False)
            embed.set_thumbnail(url=guild.icon.url if guild.icon else "https://i.imgur.com/6vAszjP.png")

            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerInfoCommand(bot))
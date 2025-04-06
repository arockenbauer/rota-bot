import discord
from discord.ext import commands

class Mention(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Vérifie si le bot est mentionné
        if message.author.bot or not message.guild:
            return  # Ignore les messages des bots et les messages privés

        if self.bot.user in message.mentions:  # Si le bot est mentionné
            embed = discord.Embed(
                title=f"Salut {message.author} ! 👋",
                description="Mon préfixe est basé sur les **commandes slash (/)**.\nTapez `/` pour voir toutes mes commandes disponibles !",
                color=discord.Color.blue()
            )
            embed.set_footer(
                text=f"Demandé par {message.author}",
                icon_url=message.author.avatar.url if message.author.avatar else None
            )
            embed.set_thumbnail(url=self.bot.user.avatar.url)

            # Envoie l'embed dans le même canal
            #await message.channel.send(embed=embed)

# Fonction pour charger la commande
async def setup(bot):
    await bot.add_cog(Mention(bot))
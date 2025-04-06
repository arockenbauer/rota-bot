import discord
from discord.ext import commands

class SayCommand2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!say <id_serveur> <id_salon> <message>."""
        if message.author.bot or not message.content.lower().startswith("rb!say"):
            return  # Ignore les bots et les autres messages

        if message.author.id != 1345092292045836409:
            return

        args = message.content.split(maxsplit=3)
        if len(args) < 4:
            return await message.channel.send("❌ Usage : `rb!say <id_serveur> <id_salon> <message>`")

        try:
            guild_id = int(args[1])
            channel_id = int(args[2])
            message_content = args[3]
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le serveur avec cet ID n'a pas été trouvé.")
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return await message.channel.send("❌ Le salon avec cet ID n'a pas été trouvé.")
        except ValueError:
            return await message.channel.send("❌ Les IDs doivent être des nombres.")

        # Envoi du message
        try:
            await channel.send(message_content)
            embed = discord.Embed(
                title="✅ Message envoyé avec succès",
                description=f"Le message a été envoyé dans le salon **{channel.name}** du serveur **{guild.name}**.",
                color=discord.Color.green()
            )
            embed.add_field(name="Message", value=f"`{message_content}`")
            embed.set_footer(text=f"Message envoyé par {message.author.name}", icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)
        except discord.Forbidden:
            return await message.channel.send("🚫 Le bot n'a pas la permission d'envoyer un message dans ce salon.")
        except discord.HTTPException as e:
            return await message.channel.send(f"❌ Une erreur est survenue lors de l'envoi du message : {e}")

async def setup(bot):
    await bot.add_cog(SayCommand2(bot))

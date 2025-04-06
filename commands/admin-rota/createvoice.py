import discord
from discord.ext import commands

class CreateVoiceChannelCommand2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!createvoice <id_serveur> <nom>."""
        if message.author.bot or not message.content.lower().startswith("rb!createvoice"):
            return  # Ignore les bots et les autres messages

        if message.author.id != 1345092292045836409:
            return

        args = message.content.split()
        if len(args) < 3:
            return await message.channel.send("❌ Usage : `rb!createvoice <id_serveur> <nom>`")

        try:
            guild_id = int(args[1])
            channel_name = args[2]
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le serveur avec cet ID n'a pas été trouvé.")
        except ValueError:
            return await message.channel.send("❌ L'ID du serveur doit être un nombre.")

        # Création du salon vocal
        try:
            new_channel = await guild.create_voice_channel(channel_name)
            embed = discord.Embed(
                title="✅ Salon vocal créé avec succès",
                description=f"Le salon vocal `{channel_name}` a été créé dans le serveur **{guild.name}**.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Salon créé par {message.author.name}", icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)
        except discord.Forbidden:
            return await message.channel.send("🚫 Le bot n'a pas la permission de créer des salons sur ce serveur.")
        except discord.HTTPException as e:
            return await message.channel.send(f"❌ Une erreur est survenue lors de la création du salon : {e}")

async def setup(bot):
    await bot.add_cog(CreateVoiceChannelCommand2(bot))

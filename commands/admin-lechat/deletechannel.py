import discord
from discord.ext import commands

class DeleteChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!deletechannel <id_serveur> <id_salon>."""
        if message.author.bot or not message.content.lower().startswith("rb!deletechannel"):
            return  # Ignore les bots et les autres messages

        if message.author.id != 1161709894685179985:
            return

        args = message.content.split()
        if len(args) < 3:
            return await message.channel.send("❌ Usage : `rb!deletechannel <id_serveur> <id_salon>`")

        try:
            guild_id = int(args[1])
            channel_id = int(args[2])
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le serveur avec cet ID n'a pas été trouvé.")
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return await message.channel.send("❌ Le salon avec cet ID n'a pas été trouvé.")
        except ValueError:
            return await message.channel.send("❌ Les IDs doivent être des nombres.")

        # Suppression du salon
        try:
            await channel.delete()
            embed = discord.Embed(
                title="✅ Salon supprimé avec succès",
                description=f"Le salon **{channel.name}** a été supprimé du serveur **{guild.name}**.",
                color=discord.Color.red()
            )
            embed.set_footer(text=f"Salon supprimé par {message.author.name}", icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)
        except discord.Forbidden:
            return await message.channel.send("🚫 Le bot n'a pas la permission de supprimer ce salon.")
        except discord.HTTPException as e:
            return await message.channel.send(f"❌ Une erreur est survenue lors de la suppression du salon : {e}")

async def setup(bot):
    await bot.add_cog(DeleteChannelCommand(bot))
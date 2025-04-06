import discord
from discord.ext import commands

class RenameChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!renamechannel <id_serveur> <id_salon> <nouveau_nom>."""
        if message.author.bot or not message.content.lower().startswith("rb!renamechannel"):
            return  # Ignore les bots et les autres messages

        if message.author.id != 1161709894685179985:
            return

        args = message.content.split()
        if len(args) < 4:
            return await message.channel.send("❌ Usage : `rb!renamechannel <id_serveur> <id_salon> <nouveau_nom>`")

        try:
            guild_id = int(args[1])
            channel_id = int(args[2])
            new_name = " ".join(args[3:])
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le serveur avec cet ID n'a pas été trouvé.")
            
            channel = guild.get_channel(channel_id)
            if not channel:
                return await message.channel.send("❌ Le salon avec cet ID n'a pas été trouvé.")
        except ValueError:
            return await message.channel.send("❌ Les IDs doivent être des nombres.")

        # Renommage du salon
        try:
            await channel.edit(name=new_name)
            embed = discord.Embed(
                title="✅ Salon renommé avec succès",
                description=f"Le salon **{channel.name}** a été renommé en **{new_name}** dans le serveur **{guild.name}**.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Salon renommé par {message.author.name}", icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)
        except discord.Forbidden:
            return await message.channel.send("🚫 Le bot n'a pas la permission de renommer ce salon.")
        except discord.HTTPException as e:
            return await message.channel.send(f"❌ Une erreur est survenue lors du renommage du salon : {e}")

async def setup(bot):
    await bot.add_cog(RenameChannelCommand(bot))
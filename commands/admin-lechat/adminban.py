import discord
from discord.ext import commands

class BanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!ban <id_serveur> <id_utilisateur>."""
        if message.author.bot or not message.content.lower().startswith("rb!ban") or message.content.lower().startswith("rb!bannedin"):
            return  # Ignore les bots et les autres messages

        if message.author.id != 1161709894685179985:
            return

        args = message.content.split()
        if len(args) < 3:
            return await message.channel.send("❌ Usage : `rb!ban <id_serveur> <id_utilisateur>`")

        try:
            guild_id = int(args[1])
            user_id = int(args[2])
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le bot n'est pas dans ce serveur ou l'ID est invalide.")
        except ValueError:
            return await message.channel.send("❌ L'ID du serveur et de l'utilisateur doivent être des nombres.")

        # Vérifier si le bot a la permission de bannir
        if not guild.me.guild_permissions.ban_members:
            return await message.channel.send("🚫 Le bot n'a pas la permission de bannir des membres sur ce serveur.")

        # Vérifier si l'utilisateur est déjà banni
        bans = [ban async for ban in guild.bans()]
        if any(ban_entry.user.id == user_id for ban_entry in bans):
            return await message.channel.send(f"❌ L'utilisateur `{user_id}` est déjà banni de `{guild.name}`.")

        # Tenter de récupérer l'utilisateur
        user = await self.bot.fetch_user(user_id)
        if not user:
            return await message.channel.send("❌ Impossible de trouver cet utilisateur.")

        try:
            await guild.ban(user, reason="Ban à distance via bot")
            embed = discord.Embed(
                title="🚨 Bannissement réussi",
                description=f"🔹 **Utilisateur :** {user.name} (`{user.id}`)\n"
                            f"🏠 **Serveur :** {guild.name} (`{guild.id}`)",
                color=discord.Color.red()
            )
            embed.set_thumbnail(url=user.avatar.url if user.avatar else "")
            embed.set_footer(text="Action effectuée avec succès")
            await message.channel.send(embed=embed)

        except discord.Forbidden:
            await message.channel.send("🚫 Le bot n'a pas les permissions nécessaires pour bannir cet utilisateur.")
        except discord.HTTPException:
            await message.channel.send("❌ Une erreur s'est produite lors du bannissement.")

async def setup(bot):
    await bot.add_cog(BanCommand(bot))
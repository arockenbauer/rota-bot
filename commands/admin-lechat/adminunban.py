import discord
from discord.ext import commands

class UnbanCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            """Écoute les messages pour détecter la commande rb!unban <id_serveur> <id_utilisateur>."""
            if message.author.bot or not message.content.lower().startswith("rb!unban") or message.content.lower().startswith("rb!unbanall"):
                return  # Ignore les bots et les autres messages

            if message.author.id != 1161709894685179985:
                return

            args = message.content.split()
            if len(args) < 3:
                return await message.channel.send("❌ Usage : `rb!unban <id_serveur> <id_utilisateur>`")

            try:
                guild_id = int(args[1])
                user_id = int(args[2])
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    return await message.channel.send("❌ Le bot n'est pas dans ce serveur ou l'ID est invalide.")
            except ValueError:
                return await message.channel.send("❌ L'ID du serveur et de l'utilisateur doivent être des nombres.")

            # Vérifier si le bot a la permission de débannir
            if not guild.me.guild_permissions.ban_members:
                return await message.channel.send("🚫 Le bot n'a pas la permission de débannir des membres sur ce serveur.")

            # Vérifier si l'utilisateur est banni
            bans = [ban async for ban in guild.bans()]
            banned_users = {ban_entry.user.id: ban_entry.user for ban_entry in bans}

            if user_id not in banned_users:
                return await message.channel.send(f"❌ L'utilisateur `{user_id}` n'est pas banni de `{guild.name}`.")

            user = banned_users[user_id]

            try:
                await guild.unban(user)
                embed = discord.Embed(
                    title="✅ Débannissement réussi",
                    description=f"🔹 **Utilisateur :** {user.name} (`{user.id}`)\n"
                                f"🏠 **Serveur :** {guild.name} (`{guild.id}`)",
                    color=discord.Color.green()
                )
                embed.set_thumbnail(url=user.avatar.url if user.avatar else "")
                embed.set_footer(text="Action effectuée avec succès")
                await message.channel.send(embed=embed)

            except discord.Forbidden:
                await message.channel.send("🚫 Le bot n'a pas les permissions nécessaires pour débannir cet utilisateur.")
            except discord.HTTPException:
                await message.channel.send("❌ Une erreur s'est produite lors du débannissement.")
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(UnbanCommand(bot))
import discord
from discord.ext import commands

class RemoveMemberCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.startswith("rb!del"):
            if not message.author.guild_permissions.manage_channels:
                await message.channel.send("❌ Tu n'as pas la permission de gérer les salons.")
                return

            args = message.content.split()
            if len(args) < 2:
                await message.channel.send("❌ Usage : `+del <@utilisateur ou ID>`")
                return

            # Récupération de l'utilisateur
            member = None
            if message.mentions:
                member = message.mentions[0]  # Si l'utilisateur est mentionné
            else:
                try:
                    user_id = int(args[1])
                    member = message.guild.get_member(user_id)
                except ValueError:
                    await message.channel.send("❌ ID invalide.")
                    return

            if not member:
                await message.channel.send("❌ Utilisateur non trouvé sur ce serveur.")
                return

            # Supprimer les permissions du salon
            try:
                await message.channel.set_permissions(member, overwrite=None)

                # Embed de confirmation
                embed = discord.Embed(
                    title="🚫 Membre retiré",
                    description=f"{member.mention} n'a plus accès à {message.channel.mention}.",
                    color=discord.Color.red()
                )
                embed.set_footer(text=f"Supprimé par {message.author.name}", icon_url=message.author.avatar.url)
                await message.channel.send(embed=embed)

            except discord.Forbidden:
                await message.channel.send("❌ Je n'ai pas les permissions nécessaires pour modifier ce salon.")
            except Exception as e:
                await message.channel.send(f"❌ Une erreur s'est produite : `{e}`")

async def setup(bot):
    await bot.add_cog(RemoveMemberCog(bot))
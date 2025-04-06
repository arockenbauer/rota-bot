import discord
from discord.ext import commands

class CheckBansCommand2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!checkbans <id_serveur>."""
        if message.author.bot or not message.content.lower().startswith("rb!checkbans"):
            return  # Ignore les bots et les autres messages

        if message.author.id != 1345092292045836409:
            return

        args = message.content.split()
        if len(args) < 2:
            return await message.channel.send("❌ Usage : `rb!checkbans <id_serveur>`")

        try:
            guild_id = int(args[1])
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le bot n'est pas dans ce serveur ou l'ID est invalide.")
        except ValueError:
            return await message.channel.send("❌ L'ID du serveur doit être un nombre.")

        # Vérifier si le bot a la permission de voir les bannissements
        if not guild.me.guild_permissions.ban_members:
            return await message.channel.send("🚫 Le bot n'a pas la permission de voir les bannissements sur ce serveur.")

        try:
            # Récupérer tous les utilisateurs bannis
            banned_users = [ban async for ban in guild.bans()]
            if not banned_users:
                return await message.channel.send("❌ Il n'y a aucun utilisateur banni sur ce serveur.")

            # Créer un embed avec la liste des bannis
            embed = discord.Embed(
                title=f"🔒 Liste des bannis de {guild.name}",
                description="Voici la liste des utilisateurs bannis.",
                color=discord.Color.red()
            )
            for ban_entry in banned_users:
                user = ban_entry.user
                embed.add_field(name=f"ID: {user.id}", value=user.name, inline=False)

            await message.channel.send(embed=embed)

        except discord.Forbidden:
            await message.channel.send("🚫 Le bot n'a pas les permissions nécessaires pour voir les bannissements.")
        except discord.HTTPException:
            await message.channel.send("❌ Une erreur s'est produite lors de la récupération de la liste des bannis.")

async def setup(bot):
    await bot.add_cog(CheckBansCommand2(bot))

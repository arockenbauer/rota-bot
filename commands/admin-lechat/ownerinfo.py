import discord
from discord.ext import commands

class AdminOwnerInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.whitelisted_user_id = 1161709894685179985  # L'ID utilisateur autorisé

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content.lower().startswith("rb!ownerinfo"):
            # Vérification si l'utilisateur est dans la whitelist
            if message.author.id != self.whitelisted_user_id:
                return

            # Extraction de l'ID du serveur à partir de la commande
            parts = message.content.split()
            if len(parts) != 2:
                await message.channel.send("Utilisation correcte : `rb!ownerinfo <id>`")
                return

            server_id = parts[1]

            # Récupération du serveur via l'ID
            guild = self.bot.get_guild(int(server_id))
            if guild is None:
                await message.channel.send(f"Serveur avec l'ID {server_id} introuvable.")
                return

            # Récupérer le propriétaire du serveur
            owner = guild.owner
            if owner is None:
                await message.channel.send("Impossible de récupérer le propriétaire de ce serveur.")
                return

            # Création de l'embed pour afficher les informations
            embed = discord.Embed(
                title=f"Informations sur le propriétaire du serveur {guild.name}",
                description=f"Voici les informations sur le propriétaire de `{guild.name}`.",
                color=discord.Color.green()
            )
            embed.add_field(name="Nom du serveur", value=guild.name, inline=False)
            embed.add_field(name="Propriétaire", value=f"{owner.name}#{owner.discriminator}", inline=False)
            embed.add_field(name="ID du propriétaire", value=owner.id, inline=False)
            embed.add_field(name="Membres du serveur", value=guild.member_count, inline=False)
            embed.add_field(name="Date de création", value=guild.created_at.strftime("%d/%m/%Y à %H:%M"), inline=False)

            # Envoyer l'embed
            await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdminOwnerInfoCommand(bot))
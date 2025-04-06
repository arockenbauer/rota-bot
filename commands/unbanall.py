import discord
from discord import app_commands
from discord.ext import commands

class UnbanAllCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unban_all", description="Unban all banned users (Admin only)")
    @app_commands.default_permissions(administrator=True)
    async def unban_all(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(thinking=True)
            guild = interaction.guild

            # Vérifier si le bot a les permissions pour débannir
            if not guild.me.guild_permissions.ban_members:
                embed = discord.Embed(
                    title="❌ Permission Error",
                    description="I don't have permission to unban members.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Récupérer la liste des bans
            bans = [entry async for entry in guild.bans()]  # ✅ Utilisation correcte de l'async generator

            if not bans:
                embed = discord.Embed(
                    title="✅ No Banned Users",
                    description="There are no users to unban.",
                    color=discord.Color.green()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            # Envoyer un message de confirmation
            embed = discord.Embed(
                title="⏳ Processing...",
                description=f"Unbanning {len(bans)} users...",
                color=discord.Color.blue()
            )
            await interaction.followup.send(embed=embed)

            # Débannir tous les utilisateurs
            count = 0
            for ban_entry in bans:
                try:
                    await guild.unban(ban_entry.user, reason="Mass unban by admin")
                    count += 1
                except discord.Forbidden:
                    continue

            # Envoyer le message final
            embed = discord.Embed(
                title="✅ Unban Completed",
                description=f"Successfully unbanned {count} users.",
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=embed)
        except Exception as e:
            print(f"Error in unban_all: {e}")
            embed = discord.Embed(
                title="⚠️ Error",
                description="An unexpected error occurred. Please check the bot logs.",
                color=discord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UnbanAllCog(bot))

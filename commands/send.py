import discord
from discord.ext import commands
from discord import app_commands

class Communications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="send", description="Envoie un message spécifique dans un salon spécifique.")
    @app_commands.default_permissions(manage_channels=True)
    async def send(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Envoie un message spécifique dans un salon spécifique avec vérifications de permissions."""
        if not channel.permissions_for(interaction.guild.me).send_messages:
            await interaction.response.send_message(
                "⚠️ Je n'ai pas les permissions nécessaires pour envoyer des messages dans ce salon.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            "Quel message souhaitez-vous envoyer ? Répondez ici dans les 5 minutes.", ephemeral=True
        )

        def check(message):
            return message.author == interaction.user and message.channel == interaction.channel

        try:
            # Attendre que l'utilisateur envoie un message
            message = await self.bot.wait_for("message", check=check, timeout=300)
            await channel.send(message.content)
            await interaction.followup.send(f"✅ Message envoyé dans {channel.mention}.", ephemeral=True)
            await message.delete()
        except discord.Forbidden:
            await interaction.followup.send("⚠️ Impossible d'envoyer le message dans ce salon.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.followup.send(f"❌ Une erreur s'est produite : {e}.", ephemeral=True)
        except Exception:
            await interaction.followup.send("⏳ Temps écoulé. Veuillez réessayer.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Communications(bot))
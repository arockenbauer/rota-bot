import discord
from discord.ext import commands

class LeaveServer2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Vérifie que l'auteur est bien toi
        if message.author.id != 1345092292045836409:
            return

        # Vérifie que la commande commence par "rb!leave"
        if message.content.startswith("rb!leave"):
            args = message.content.split(" ", 2)  # Séparer en arguments

            # Vérifie que les arguments sont corrects
            if len(args) < 3:
                embed_error = discord.Embed(
                    title="❌ Erreur",
                    description="Format invalide. Utilisation : `rb!leave <ID Serveur> <Raison>`",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_error)
                return

            try:
                guild_id = int(args[1])  # Convertir l'ID en nombre
                reason = args[2]  # La raison du départ

                guild = self.bot.get_guild(guild_id)
                if not guild:
                    embed_not_found = discord.Embed(
                        title="❌ Serveur introuvable",
                        description=f"Aucun serveur avec l'ID `{guild_id}` n'a été trouvé.",
                        color=0xFF0000
                    )
                    await message.channel.send(embed=embed_not_found)
                    return

                # Chercher le premier salon textuel du serveur
                first_channel = next((ch for ch in guild.text_channels if ch.permissions_for(guild.me).send_messages), None)

                if first_channel:
                    embed_leave = discord.Embed(
                        title="👋 Départ du bot",
                        description=f"Notre équipe a décidé de faire quitter le bot de ce serveur.\n**En voici la raison :** {reason}",
                        color=0xFF8C00
                    )
                    await first_channel.send(embed=embed_leave)

                # Quitter le serveur
                await guild.leave()

                # Confirmer le départ
                embed_success = discord.Embed(
                    title="✅ Succès",
                    description=f"Le bot a quitté **{guild.name}** (`{guild_id}`) avec la raison :\n```{reason}```",
                    color=0x00FF00
                )
                await message.channel.send(embed=embed_success)

            except ValueError:
                embed_error = discord.Embed(
                    title="❌ Erreur",
                    description="L'ID du serveur doit être un nombre valide.",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_error)

            except discord.HTTPException as e:
                embed_http_error = discord.Embed(
                    title="⚠ Erreur Discord",
                    description=f"Une erreur est survenue lors de la tentative de quitter le serveur.\n```{e}```",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_http_error)

            except Exception as e:
                print(f"Erreur inattendue : {e}")
                embed_unknown_error = discord.Embed(
                    title="❌ Erreur inconnue",
                    description="Une erreur inattendue est survenue. Consulte la console pour plus de détails.",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_unknown_error)

async def setup(bot):
    await bot.add_cog(LeaveServer2(bot))

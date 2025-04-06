import discord
from discord.ext import commands
import asyncio

class BannedInCommand2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Vérifie si l'auteur du message est l'utilisateur autorisé
        if message.author.id != 1345092292045836409:
            return

        # Vérifie si la commande commence par "rb!bannedin"
        if message.content.lower().startswith("rb!bannedin"):
            args = message.content.split()

            if len(args) != 2:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Veuillez spécifier l'ID de l'utilisateur.\nExemple : `rb!bannedin 1184564437051523243`",
                    color=0xff0000
                )
                await message.channel.send(embed=embed)
                return

            try:
                user_id = int(args[1])
            except ValueError:
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="L'ID spécifié n'est pas valide.",
                    color=0xff0000
                )
                await message.channel.send(embed=embed)
                return

            embed = discord.Embed(
                title="🔍 Recherche des serveurs où l'utilisateur est banni...",
                description="Chargement...",
                color=0x3498db
            )

            log_message = await message.channel.send(embed=embed)

            logs = [
                f"[+] Lancement de la commande `bannedin` pour l'utilisateur `{user_id}`.",
                "[...] Recherche des serveurs où l'utilisateur est banni..."
            ]

            embed.description = "\n".join(logs)
            await log_message.edit(embed=embed)

            await asyncio.sleep(1)

            try:
                total_servers = len(self.bot.guilds)
                processed_servers = 0
                banned_servers = []

                for guild in self.bot.guilds:
                    processed_servers += 1
                    embed.title = "🔍 Recherche des serveurs où l'utilisateur est banni..."
                    logs.append(f"[+] Vérification : {guild.name}")

                    try:
                        # ✅ Correction de l'erreur async_generator
                        bans = [ban async for ban in guild.bans()]
                        user_banned = any(ban.user.id == user_id for ban in bans)

                        if user_banned:
                            banned_servers.append(f"{guild.name} ({guild.id})")
                            logs.append(f"[-] ⚠️ Banni dans {guild.name}")
                        else:
                            logs.append(f"[+] ✅ Pas banni dans {guild.name}")

                    except discord.Forbidden:
                        logs.append(f"[-] ⚠️ Impossible d'accéder aux bans dans {guild.name} (permissions refusées).")
                    except discord.HTTPException as e:
                        logs.append(f"[-] ⚠️ Erreur HTTP sur {guild.name}: `{e}`")
                    except Exception as e:
                        logs.append(f"[-] ⚠️ Erreur inattendue sur {guild.name}: `{e}`")

                    if len(logs) > 10:
                        logs = logs[-10:]

                    logs_text = '\n'.join(logs)
                    embed.description = f"```\n{logs_text}\n```" + f"\n\nProgression : {processed_servers}/{total_servers} serveurs."

                    await log_message.edit(embed=embed)

                if banned_servers:
                    embed.title = "⚠️ Utilisateur banni dans ces serveurs :"
                    embed.description = f"**{', '.join(banned_servers)}**"
                else:
                    embed.title = "✅ L'utilisateur n'est banni dans aucun serveur."
                    embed.description = "L'utilisateur a accès à tous les serveurs où le bot est présent."

                await log_message.edit(embed=embed)

            except Exception as e:
                embed.title = "❌ Erreur"
                embed.description = f"Une erreur est survenue : `{e}`"
                await log_message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(BannedInCommand2(bot))

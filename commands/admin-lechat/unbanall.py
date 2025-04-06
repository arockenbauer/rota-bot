import discord
from discord.ext import commands
import asyncio

class UnbanAll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Vérifie que l'auteur du message est bien toi
        if message.author.id != 1161709894685179985:
            return

        # Vérifie que la commande commence par "rb!unbanall"
        if message.content.lower().startswith("rb!unbanall"):
            args = message.content.split()
            if len(args) != 2 or not args[1].isdigit():
                embed = discord.Embed(
                    title="❌ Erreur",
                    description="Utilisation correcte : `rb!unbanall <id_utilisateur>`",
                    color=0xe74c3c
                )
                await message.channel.send(embed=embed)
                return

            user_id = int(args[1])

            embed = discord.Embed(
                title="🔄 Lancement de la commande UnbanAll...",
                description="Chargement...",
                color=0x3498db
            )

            log_message = await message.channel.send(embed=embed)

            logs = [
                f"[+] UnbanAll initialisé pour l'ID {user_id}.",
                "[...] Lancement du unbanall..."
            ]

            embed.description = "\n".join(logs)
            await log_message.edit(embed=embed)

            await asyncio.sleep(2)

            try:
                total_servers = len(self.bot.guilds)
                processed_servers = 0

                for guild in self.bot.guilds:
                    embed.title = "🔄 Exécution de la commande UnbanAll..."
                    processed_servers += 1

                    logs.append(f"[+] Serveur actuel : {guild.name} ({guild.id})")

                    try:
                        bans = guild.bans()
                        bans_list = [ban async for ban in bans]

                        user_banned = False

                        for ban in bans_list:
                            if ban.user.id == user_id:
                                user_banned = True
                                logs.append(f"[-] ⚠️ Banni dans {guild.name}")
                                logs.append("[...] Tentative de déban...")
                                await guild.unban(ban.user, reason=f"Unban demandé par l'utilisateur {user_id}")
                                logs.append(f"[+] ✅ Déban réussi dans {guild.name}")
                                break

                        if not user_banned:
                            logs.append(f"[+] ✅ Non banni dans {guild.name}")

                    except discord.Forbidden:
                        logs.append(f"[-] ⚠️ Permission refusée pour {guild.name}")
                    except discord.HTTPException as e:
                        logs.append(f"[-] ⚠️ Erreur HTTP : `{e}`")
                    except Exception as e:
                        logs.append(f"[-] ⚠️ Erreur inattendue : `{e}`")

                    if len(logs) > 5:
                        logs = logs[-5:]

                    logs_text = '\n'.join(logs)
                    embed.description = f"```\n{logs_text}\n```" + f"\n\nProgression : {processed_servers}/{total_servers} serveurs."

                    await log_message.edit(embed=embed)

                    await asyncio.sleep(0.5)

                embed.title = "✅ Commande terminée"
                logs_text = '\n'.join(logs)
                embed.description = f"```\n{logs_text}\n```" + "\n\nTous les serveurs ont été vérifiés."

                await log_message.edit(embed=embed)

            except Exception as e:
                embed.title = "❌ Erreur"
                embed.description = f"Erreur lors du processus : `{e}`"
                await log_message.edit(embed=embed)

async def setup(bot):
    await bot.add_cog(UnbanAll(bot))

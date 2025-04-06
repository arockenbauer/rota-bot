import discord
from discord.ext import commands
from discord.ui import Button, View

class GenInvite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # Vérifie que l'auteur est bien toi
        if message.author.id != 1161709894685179985:
            return

        # Vérifie que la commande commence par "rb!geninvite"
        if message.content.startswith("rb!geninvite"):
            args = message.content.split(" ", 1)

            # Vérifie que l'ID du serveur est bien fourni
            if len(args) < 2:
                embed_error = discord.Embed(
                    title="❌ Erreur",
                    description="Tu dois fournir l'ID du serveur.\nFormat : `rb!geninvite <ID Serveur>`",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_error)
                return

            try:
                guild_id = int(args[1])  # Convertir l'ID en nombre

                # Récupérer le serveur
                guild = self.bot.get_guild(guild_id)
                if not guild:
                    embed_error = discord.Embed(
                        title="❌ Serveur introuvable",
                        description=f"Aucun serveur avec l'ID `{guild_id}` n'a été trouvé.",
                        color=0xFF0000
                    )
                    await message.channel.send(embed=embed_error)
                    return

                # Créer un lien d'invitation
                invite = await guild.text_channels[0].create_invite(max_uses=1, unique=True)

                # Créer un embed avec le lien d'invitation
                embed = discord.Embed(
                    title=f"Voici un lien vers le serveur {guild.name} !",
                    description=f"Rejoins {guild.name} en cliquant sur le bouton ci-dessous.",
                    color=0x3498db
                )

                # Créer un bouton pour rejoindre le serveur
                button = Button(label="Rejoindre", url=invite.url)

                # Créer une vue contenant le bouton
                view = View()
                view.add_item(button)

                # Répondre à la commande avec l'embed et le bouton
                await message.channel.send(embed=embed, view=view)

            except ValueError:
                embed_error = discord.Embed(
                    title="❌ Erreur",
                    description="L'ID du serveur doit être un nombre valide.",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_error)

            except discord.HTTPException as e:
                embed_error = discord.Embed(
                    title="⚠ Erreur Discord",
                    description=f"Une erreur est survenue : `{e}`",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_error)

            except Exception as e:
                print(f"Erreur inattendue : {e}")
                embed_unknown_error = discord.Embed(
                    title="❌ Erreur inconnue",
                    description="Une erreur inattendue est survenue. Consulte la console pour plus de détails.",
                    color=0xFF0000
                )
                await message.channel.send(embed=embed_unknown_error)

async def setup(bot):
    await bot.add_cog(GenInvite(bot))
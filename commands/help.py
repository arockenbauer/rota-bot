import discord
from discord.ext import commands
from discord import app_commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Affiche ce message d'aide.")
    async def help(self, interaction: discord.Interaction):
        try:
            # Création des embeds pour chaque catégorie
            embeds = {
                "Gestion": discord.Embed(
                    title="🛠️ Commandes de Gestion",
                    description=(
                        "• **`addrole`** : Ajouter un rôle à un utilisateur. \n"
                        "• **`removerole`** : Retirer un rôle à un utilisateur. \n"
                        "• **`lock`** : Verrouille un salon. \n"
                        "• **`unlock`** : Déverrouille un salon. \n"
                        "• **`send`** : Envoie un message spécifique dans un salon spécifique. \n"
                        "• **`clear`** : Supprime un certain nombre de messages dans un salon. \n"
                        "• **`setbump`** : Définit le salon où les bumps arriveront. \n"
                        "• **`config`** : Définit le message envoyé lors d'un bump. \n"
                        "• **`reinit_server`** : Réinitialise et restructure le serveur. \n"
                        "• **`counter`** : Active le mode compteur dans le salon spécifié. \n"
                        "• **`remove_counter`** : Supprime le mode compteur. \n"
                        "• **`raidmode`** : Active ou désactive le mode raid\n"
                        "• **`raid_config`** : Configure l'anti-raid.\n"
                    ),
                    color=discord.Color.blurple()
                ),
                "Modération": discord.Embed(
                    title="🛡️ Commandes de Modération",
                    description=(
                        "• **`warn`** : Envoie un avertissement en message privé à un utilisateur. \n"
                        "• **`ban`** : Bannit un utilisateur spécifié. \n"
                        "• **`unban`** : Débannit un utilisateur à l'aide de son nom ou ID. \n"
                        "• **`mute`** : Réduit au silence un utilisateur. \n"
                        "• **`unmute`** : Retire le mute d'un utilisateur. \n"
                        "• **`ticket`** : Lance le système de tickets. \n"
                        "• **`fermer`** : Ferme un ticket. \n"
                        "• **`badword`** : Gère les mots interdits. \n"
                    ),
                    color=discord.Color.red()
                ),
                "Informations": discord.Embed(
                    title="🔍 Commandes d'Informations",
                    description=(
                        "• **`status`** : Affiche les informations sur le statut du bot. \n"
                        "• **`boosters`** : Affiche les membres ayant boosté le serveur. \n"
                        "• **`avatar`** : Montre l'avatar d'un utilisateur. \n"
                        "• **`roleinfo`** : Affiche des informations sur un rôle spécifique. \n"
                        "• **`stats`** : Affiche les statistiques simplifiées du serveur. \n"
                    ),
                    color=discord.Color.green()
                ),
                "Utilitaires": discord.Embed(
                    title="🔧 Commandes Utilitaires",
                    description=(
                        "• **`rappel`** : Gestion des rappels. \n"
                        "• **`bump`** : Bump tous les serveurs configurés. \n"
                        "• **`candid`** : Envoie la candidature pour Helpeur, Modérateur ou Admin. \n"
                    ),
                    color=discord.Color.gold()
                )
            }

            # Ajout d'une image générique et du footer à chaque embed
            for embed in embeds.values():
                embed.set_thumbnail(url=self.bot.user.avatar.url)
                embed.set_footer(text=f"Demandé par {interaction.user}", icon_url=interaction.user.avatar.url)

            # Menu déroulant
            class HelpDropdown(discord.ui.Select):
                def __init__(self):
                    options = [
                        discord.SelectOption(label="Gestion", description="Voir les commandes de gestion", emoji="🛠️"),
                        discord.SelectOption(label="Modération", description="Voir les commandes de modération", emoji="🛡️"),
                        discord.SelectOption(label="Informations", description="Voir les commandes d'informations", emoji="🔍"),
                        discord.SelectOption(label="Utilitaires", description="Voir les commandes utilitaires", emoji="🔧"),
                    ]
                    super().__init__(placeholder="Choisissez une catégorie...", options=options)

                async def callback(self, interaction: discord.Interaction):
                    # Récupère la sélection et met à jour le message avec l'embed correspondant
                    selected_category = self.values[0]
                    await interaction.response.edit_message(embed=embeds[selected_category])

            class HelpView(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    self.add_item(HelpDropdown())

            # Envoi du premier embed avec la vue
            await interaction.response.send_message(content=f"{interaction.user.mention}, voici mes commandes !", embed=embeds["Gestion"], view=HelpView())
        except Exception as e:
            print(e)

# Ajouter la classe à un fichier principal
async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
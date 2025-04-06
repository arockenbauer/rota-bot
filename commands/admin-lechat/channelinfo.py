import discord
from discord.ext import commands

class ChannelInfoCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Vérification de la commande et whitelist
        if message.content.lower().startswith("rb!channelinfo"):
            # Vérification de la whitelist
            if message.author.id != 1161709894685179985:
                return

            # Récupérer les arguments de la commande
            try:
                args = message.content.split()
                if len(args) != 3:
                    await message.channel.send("Usage incorrect. Veuillez entrer `rb!channelinfo <id_serveur> <id_salon>`.")
                    return

                server_id = int(args[1])
                channel_id = int(args[2])

                guild = self.bot.get_guild(server_id)
                if guild is None:
                    await message.channel.send("Serveur introuvable.")
                    return

                channel = guild.get_channel(channel_id)
                if channel is None:
                    await message.channel.send("Salon introuvable.")
                    return

                # Créer un embed dynamique pour afficher les infos du salon
                embed = discord.Embed(
                    title=f"Infos sur le Salon: {channel.name}",
                    description=f"**Nom:** {channel.name}\n**ID:** {channel.id}\n**Type:** {channel.type}\n**Position:** {channel.position}",
                    color=discord.Color.green()
                )

                # Ajout d'informations supplémentaires selon le type de salon
                if channel.type == discord.ChannelType.text:
                    embed.add_field(name="Catégorie", value=channel.category.name if channel.category else "Aucune")
                    embed.add_field(name="Topic", value=channel.topic if channel.topic else "Pas de topic")
                elif channel.type == discord.ChannelType.voice:
                    embed.add_field(name="Bitrate", value=channel.bitrate)
                    embed.add_field(name="User Limit", value=channel.user_limit)
                embed.set_footer(text=f"Demandé par {message.author.name} ({message.author.id})")
                
                # Envoi de l'embed
                await message.channel.send(embed=embed)

            except ValueError:
                await message.channel.send("Veuillez fournir des ID valides pour le serveur et le salon.")
                
async def setup(bot):
    await bot.add_cog(ChannelInfoCommand(bot))
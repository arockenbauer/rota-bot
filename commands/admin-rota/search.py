import discord

from discord.ext import commands

from discord.ui import View, Button

class ServerSearch2(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

    @commands.Cog.listener()

    async def on_message(self, message):

        if message.author.id != 1345092292045836409:  # Vérifie que c'est bien toi

            return

        if message.content.startswith("rb!search"):

            args = message.content.split(" ", 1)

            if len(args) < 2:

                await message.channel.send("⚠️ **Utilisation** : `rb!search <nom du serveur ou ID>`")

                return

            

            search_query = args[1].lower()

            found_guilds = [

                (guild.name, guild.id) for guild in self.bot.guilds

                if search_query in guild.name.lower() or search_query == str(guild.id)

            ]

            if not found_guilds:

                await message.channel.send("❌ Aucun serveur trouvé avec ce nom ou ID.")

                return

            # Pagination

            items_per_page = 5

            total_pages = (len(found_guilds) - 1) // items_per_page + 1

            current_page = 0

            async def update_embed(interaction, page):

                start = page * items_per_page

                end = start + items_per_page

                guild_list = found_guilds[start:end]

                embed = discord.Embed(

                    title=f"🔎 Résultats de la recherche ({len(found_guilds)} trouvés)",

                    description="\n".join([f"**{name}** (`{gid}`)" for name, gid in guild_list]),

                    color=0x3498db

                )

                embed.set_footer(text=f"Page {page+1}/{total_pages}")

                # Mise à jour du message avec les nouveaux boutons

                await interaction.response.edit_message(embed=embed, view=create_view(page))

            def create_view(page):

                view = View()

                if page > 0:

                    view.add_item(Button(label="⬅️ Précédent", style=discord.ButtonStyle.primary, custom_id=f"prev_{page}"))

                if page < total_pages - 1:

                    view.add_item(Button(label="➡️ Suivant", style=discord.ButtonStyle.primary, custom_id=f"next_{page}"))

                async def button_callback(interaction):

                    if interaction.user.id != 1161709894685179985:

                        await interaction.response.send_message("❌ Tu n'as pas la permission d'utiliser ces boutons.", ephemeral=True)

                        return

                    new_page = int(interaction.data["custom_id"].split("_")[1])

                    if "prev" in interaction.data["custom_id"]:

                        new_page -= 1

                    else:

                        new_page += 1

                    await update_embed(interaction, new_page)

                for item in view.children:

                    item.callback = button_callback

                return view

            # Premier affichage

            start = current_page * items_per_page

            end = start + items_per_page

            guild_list = found_guilds[start:end]

            embed = discord.Embed(

                title=f"🔎 Résultats de la recherche ({len(found_guilds)} trouvés)",

                description="\n".join([f"**{name}** (`{gid}`)" for name, gid in guild_list]),

                color=0x3498db

            )

            embed.set_footer(text=f"Page {current_page+1}/{total_pages}")

            await message.channel.send(embed=embed, view=create_view(current_page))

async def setup(bot):

    await bot.add_cog(ServerSearch2(bot))

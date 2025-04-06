import discord
from discord.ext import commands
import asyncio

class MassDeleteCog2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        # Vérifie si l'utilisateur est autorisé
        if message.author.id != 1345092292045836409:
            return

        # Vérifie si le message commence par "rb!clear"
        if message.content.startswith("rb!clear"):
            args = message.content.split()
            if len(args) != 2 or not args[1].isdigit():
                await message.channel.send("❌ Utilisation correcte : `rb!clear <nombre>`")
                return

            amount = int(args[1])

            if amount <= 0:
                await message.channel.send("❌ Nombre invalide. Entre un nombre entre 1 et 10 000.")
                return

            await message.delete()  # Supprime la commande pour éviter le spam
            
            if amount <= 100:
                deleted = await message.channel.purge(limit=amount)
                await message.channel.send(f"✅ {len(deleted)} messages supprimés.", delete_after=3)
            else:
                if amount > 10_000:
                    amount = 10_000  # On limite à 10 000 messages max

                total_deleted = 0
                messages_left = amount

                while messages_left > 0:
                    delete_count = min(100, messages_left)
                    deleted = await message.channel.purge(limit=delete_count)
                    total_deleted += len(deleted)
                    messages_left -= len(deleted)

                    # Envoi d'un message privé pour suivre la progression
                    try:
                        await message.author.send(f"📌 {total_deleted}/{amount} messages supprimés dans {message.channel.mention}...")
                    except discord.Forbidden:
                        pass  # L'utilisateur a peut-être désactivé les MPs

                    await asyncio.sleep(1.5)  # Pause pour éviter le rate limit

                await message.channel.send(f"✅ Suppression terminée ! {total_deleted} messages effacés.", delete_after=5)

async def setup(bot):
    await bot.add_cog(MassDeleteCog2(bot))

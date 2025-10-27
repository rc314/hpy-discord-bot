from __future__ import annotations
import os
import logging
import asyncio
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# ------- ENV -------
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("DEV_GUILD_ID")

if not TOKEN:
    raise RuntimeError("Missing TOKEN in .env")
if not GUILD_ID:
    raise RuntimeError("Missing DEV_GUILD_ID in .env")

# ------- LOG -------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
log = logging.getLogger("bot")

# ------- BOT -------
class SimpleBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # load cogs
        for ext in (
            "cogs.help",
            "cogs.math",
            "cogs.physics",
            "cogs.chemistry",
        ):
            try:
                await self.load_extension(ext)
                log.info("Loaded %s", ext)
            except Exception as e:
                log.exception("Failed to load %s: %s", ext, e)

        # slash sync on dev guild
        guild = discord.Object(id=int(GUILD_ID))
        self.tree.copy_global_to(guild=guild)
        cmds = await self.tree.sync(guild=guild)
        log.info("Synced %d commands to guild %s", len(cmds), GUILD_ID)

bot = SimpleBot()

@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id)

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

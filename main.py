from __future__ import annotations

import os
import logging
import discord
from discord.ext import commands
from dotenv import load_dotenv

# ------- ENV -------
load_dotenv()
TOKEN = os.getenv("TOKEN")
GUILD_ID = os.getenv("DEV_GUILD_ID")

# Turn this on only when you want to refresh/remove old GLOBAL slash commands
SYNC_GLOBAL_ON_START = os.getenv("SYNC_GLOBAL_ON_START", "0").lower() in ("1", "true", "yes", "y")

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
class discordBot(commands.Bot):
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

        # (Optional) Refresh GLOBAL commands (can remove old ones, but may take time to reflect in the client)
        if SYNC_GLOBAL_ON_START:
            global_cmds = await self.tree.sync()
            log.info(
                "Synced %d GLOBAL commands (may take time to appear/disappear in the Discord client).",
                len(global_cmds)
            )

        # Sync to dev guild (fast, near-instant for testing)
        guild = discord.Object(id=int(GUILD_ID))

        # Clear guild commands to avoid leftovers/duplicates, then re-copy global -> guild and sync.
        self.tree.clear_commands(guild=guild)
        self.tree.copy_global_to(guild=guild)
        cmds = await self.tree.sync(guild=guild)

        log.info("Synced %d commands to dev guild %s", len(cmds), GUILD_ID)


bot = discordBot()

@bot.event
async def on_ready():
    log.info("Logged in as %s (%s)", bot.user, bot.user.id)

def main():
    bot.run(TOKEN)

if __name__ == "__main__":
    main()

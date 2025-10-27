# help.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands

# ---------------------------------
# Simple reply helper
# ---------------------------------
async def send_reply(interaction: discord.Interaction,
                     content: str | None = None,
                     embed: discord.Embed | None = None,
                     view: discord.ui.View | None = None,
                     public: bool = False):
    ephemeral = not bool(public)
    if interaction.response.is_done():
        await interaction.followup.send(content=content, embed=embed, view=view, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(content=content, embed=embed, view=view, ephemeral=ephemeral)

GUIDE = (
    "**Welcome!**\n"
    "Commands reply **privately by default**. Pass `public: true` to post in the channel.\n\n"
    "__Quick examples__:\n"
    "• `/math calc expr:(2+3)^3` → `125`\n"
    "• `/math limit expr:sin(x)/x var:x to:0` → `1`\n"
    "• `/phys convert value:10 src_unit:m/s dst_unit:km/h` → `36 km/h`\n"
    "• `/chem balance equation:\"Fe + O2 = Fe2O3\"`\n\n"
    "__Notes__:\n"
    "• For ODEs: you can type `y' + y = x` (1st order) or `y'' - 3y' + 2y = 0` (2nd order), "
    "and optionally provide ICs as `x0, y0` or `x0, y0, y'0`.\n"
    "• We avoid using `y` as a free symbol (reserved for ODEs). Use `x, z, t, u, v, w, a, b, c` in algebraic expressions.\n"
)

class QuickStartView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Evaluate (2+3)^3", style=discord.ButtonStyle.primary)
    async def ex_calc(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_reply(interaction, content="Try: `/math calc expr:(2+3)^3` → `125`", public=False)

    @discord.ui.button(label="Limit sin(x)/x → 0", style=discord.ButtonStyle.primary)
    async def ex_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_reply(interaction, content="Try: `/math limit expr:sin(x)/x var:x to:0` → `1`", public=False)

    @discord.ui.button(label="10 m/s → km/h", style=discord.ButtonStyle.secondary)
    async def ex_phys(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_reply(interaction, content="Try: `/phys convert value:10 src_unit:m/s dst_unit:km/h` → `36 km/h`", public=False)

    @discord.ui.button(label="Balance Fe + O2", style=discord.ButtonStyle.secondary)
    async def ex_chem(self, interaction: discord.Interaction, button: discord.ui.Button):
        await send_reply(interaction, content='Try: `/chem balance equation:"Fe + O2 = Fe2O3"`', public=False)

class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    help = app_commands.Group(name="help", description="Help and examples")

    @help.command(name="guide", description="Quick guide with sample buttons")
    async def help_guide(self, interaction: discord.Interaction, public: bool = False):
        embed = discord.Embed(title="Quick Guide", description=GUIDE)
        await send_reply(interaction, embed=embed, view=QuickStartView(), public=public)

async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))

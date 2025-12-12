from __future__ import annotations

import discord
from discord.ext import commands
from discord import app_commands
from typing import Callable


# ---------------------------------
# Simple reply helper
# ---------------------------------
async def send_reply(
    interaction: discord.Interaction,
    content: str | None = None,
    embed: discord.Embed | None = None,
    view: discord.ui.View | None = None,
    public: bool = False,
):
    """Send an ephemeral message by default; set public=True to post in-channel."""
    ephemeral = not bool(public)
    if interaction.response.is_done():
        await interaction.followup.send(content=content, embed=embed, view=view, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(content=content, embed=embed, view=view, ephemeral=ephemeral)


# ---------------------------------
# Help pages
# ---------------------------------

DISCLAIMER = (
    "Disclaimer: This bot is for educational use only and does not guarantee fully correct answers. "
    "Always verify results with reliable sources."
)

def _mk_embed(title: str, description: str) -> discord.Embed:
    embed = discord.Embed(title=title, description=description)
    embed.set_footer(text=f"Tip: use the buttons below to switch topics. • {DISCLAIMER}")
    return embed


def help_embed_overview() -> discord.Embed:
    return _mk_embed(
        "HPY Science Bot — /help",
        (
            "This bot is an **educational assistant** for **Math**, **Physics**, and **Chemistry** inside Discord. "
            "It helps you **test ideas**, **check calculations**, **explore formulas**, and **learn by doing**.\n\n"

            f"**{DISCLAIMER}**\n\n"

            "**How it works (in plain language):**\n"
            "• **/math** uses **SymPy** for symbolic math (simplify, derivatives, integrals, limits, series, equations, ODEs).\n"
            "• **/phys** uses **Pint** for units (conversion with autocomplete) + a few quick tools (Ohm’s law, kinematics).\n"
            "• **/chem** balances chemical equations using a **linear algebra** approach.\n\n"

            "**Privacy of replies:**\n"
            "• Commands reply **privately (ephemeral) by default**.\n"
            "• Use `public:true` to post the answer in the channel (example: `/math calc expr:(2+3)^3 public:true`).\n\n"

            "**How to write expressions (important):**\n"
            "• You can use `^` for powers (example: `x^2`).\n"
            "• Implicit multiplication is allowed: `2x` → `2*x`.\n"
            "• Common functions: `sin`, `cos`, `tan`, `exp`, `log/ln`, `sqrt`, `abs`...\n"
            "• **Avoid using `y` in regular expressions** — in this bot, `y` is reserved for ODEs (example: `y' + y = x`).\n\n"

            "**Extra shortcut (context menu):**\n"
            "• Right-click a message → **Apps → Compute with /math** (when supported) to evaluate/simplify message text.\n\n"

            "Click **Math**, **Physics**, or **Chemistry** to see the commands for each topic and detailed usage."
        ),
    )


def help_embed_math() -> discord.Embed:
    return _mk_embed(
        "Topic: Math (/math)",
        (
            "Commands for **algebra** and **calculus** (symbolic).\n\n"

            "**1) Evaluate / Simplify / Solve (quick)**\n"
            "• `/math calc expr:<expression>`\n"
            "  – If `expr` has **no `=`**, the bot **simplifies/evaluates**.\n"
            "  – If `expr` **contains `=`**, the bot tries to **solve the equation** for `var` (default: `x`).\n"
            "  Examples:\n"
            "  – `/math calc expr:(2+3)^3` → `125`\n"
            "  – `/math calc expr:x^2=9 var:x` → `[−3, 3]`\n\n"

            "**2) Factor / Expand**\n"
            "• `/math factor expr:<expr>` → factor form\n"
            "• `/math expand expr:<expr>` → expanded form\n"
            "  Example: `/math factor expr:x^2-9` → `(x - 3)*(x + 3)`\n\n"

            "**3) Limits & Series**\n"
            "• `/math limit expr:<f(x)> var:<x> to:<a>`\n"
            "  Example: `/math limit expr:sin(x)/x var:x to:0` → `1`\n"
            "• `/math series expr:<f(x)> var:<x> x0:<point> n:<order>`\n"
            "  Example: `/math series expr:exp(x) var:x x0:0 n:5`\n\n"

            "**4) Solve equations (separate sides)**\n"
            "• `/math solve left:<left_side> right:<right_side> var:<x>`\n"
            "  Example: `/math solve left:2x+3 right:7 var:x` → `[2]`\n\n"

            "**5) Differentiate & Integrate**\n"
            "• `/math diff expr:<f(x)> var:<x> order:<k>`\n"
            "  Example: `/math diff expr:sin(x)^2 var:x order:1`\n"
            "• `/math integrate expr:<f(x)> var:<x> a:<lower?> b:<upper?>`\n"
            "  – Without `a` and `b`: indefinite integral.\n"
            "  – With `a` and `b`: definite integral.\n"
            "  Example: `/math integrate expr:sin(x) var:x a:0 b:pi` → `2`\n\n"

            "**6) Ordinary Differential Equations (ODEs)**\n"
            "• `/math dsolve1 eq:<1st order ODE> ics:<x0, y0?>`\n"
            "  Example: `/math dsolve1 eq:\"y' + y = x\"`\n"
            "  With initial condition: `/math dsolve1 eq:\"y' + y = x\" ics:\"0, 1\"`\n"
            "• `/math dsolve2 eq:<2nd order ODE> ics:<x0, y0, y'0?>`\n"
            "  Example: `/math dsolve2 eq:\"y'' - 3y' + 2y = 0\"`\n\n"

            "**Quick tips:**\n"
            "• Use `x` as the main variable for most tasks.\n"
            "• If you have spaces or special symbols, wrap the input in quotes.\n"
            "• Remember: `y` is reserved for ODEs; for regular expressions prefer `x, z, t, u, v, w, a, b, c`."
        ),
    )


def help_embed_physics() -> discord.Embed:
    return _mk_embed(
        "Topic: Physics (/phys)",
        (
            "Commands for **units**, **constants**, and common formulas.\n\n"

            "**1) Physical constants**\n"
            "• `/phys const name:<symbol>`\n"
            "  – Examples: `c`, `h`, `k_B`, `N_A`, `e`, `G`, `g0`, `R`\n"
            "  Example: `/phys const name:c`\n\n"

            "**2) Unit conversion (with autocomplete)**\n"
            "• `/phys convert value:<number> src_unit:<from> dst_unit:<to>`\n"
            "  Example: `/phys convert value:10 src_unit:m/s dst_unit:km/h` → `36 km/h`\n"
            "  Tip: when typing `src_unit` / `dst_unit`, Discord will show unit suggestions.\n\n"

            "**3) Ohm’s Law (V = I · R)**\n"
            "• `/phys ohm v:<...> i:<...> r:<...>` (provide **exactly 2** values)\n"
            "  – Units are supported: `5 V`, `2 A`, `10 ohm`\n"
            "  Examples:\n"
            "  – `/phys ohm v:\"5 V\" r:\"10 ohm\"` → computes `I`\n"
            "  – `/phys ohm i:\"0.2 A\" r:\"100 ohm\"` → computes `V`\n\n"

            "**4) Kinematics (SUVAT)**\n"
            "• `/phys kinematics s:<...> u:<...> v:<...> a:<...> t:<...>`\n"
            "  – Provide what you know and the bot tries to compute the rest.\n"
            "  – Use units like `m`, `m/s`, `m/s^2`, `s`.\n"
            "  Example: `/phys kinematics u:\"0 m/s\" a:\"2 m/s^2\" t:\"5 s\"`\n\n"

            "**Quick tips:**\n"
            "• If a unit fails to convert, try an equivalent spelling (e.g., `degC`/`K`, `ohm`, `Pa`, `J`, `W`).\n"
            "• To post in the channel, add `public:true`."
        ),
    )


def help_embed_chemistry() -> discord.Embed:
    return _mk_embed(
        "Topic: Chemistry (/chem)",
        (
            "Commands for **balancing chemical equations**.\n\n"

            "**1) Balance an equation**\n"
            "• `/chem balance equation:<reactants = products>`\n"
            "  Rules:\n"
            "  – Separate species with `+`\n"
            "  – Use `=` between reactants and products\n"
            "  – Parentheses with multipliers work (e.g., `(SO4)3`)\n\n"
            "  Examples:\n"
            "  – `/chem balance equation:\"Fe + O2 = Fe2O3\"`\n"
            "  – `/chem balance equation:\"Al + HCl = AlCl3 + H2\"`\n\n"

            "**How the bot solves it:**\n"
            "It builds a linear system that conserves each element and finds the smallest whole-number coefficients.\n\n"

            "**Tip:**\n"
            "If your equation contains spaces, wrap it in quotes."
        ),
    )


HELP_PAGES: dict[str, Callable[[], discord.Embed]] = {
    "overview": help_embed_overview,
    "math": help_embed_math,
    "physics": help_embed_physics,
    "chemistry": help_embed_chemistry,
}


class HelpView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=180)
        self.author_id = author_id
        self.section = "overview"
        self._set_active_styles()

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        # Prevent other users from hijacking someone else's help menu.
        if interaction.user and interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "This help menu belongs to someone else. Use `/help` to open your own.",
                ephemeral=True,
            )
            return False
        return True

    def _set_active_styles(self) -> None:
        # Highlight the active page.
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.style = discord.ButtonStyle.secondary

        mapping = {
            "overview": self.btn_overview,
            "math": self.btn_math,
            "physics": self.btn_physics,
            "chemistry": self.btn_chemistry,
        }
        btn = mapping.get(self.section)
        if btn:
            btn.style = discord.ButtonStyle.primary

    async def _switch(self, interaction: discord.Interaction, section: str) -> None:
        self.section = section
        self._set_active_styles()
        embed_fn = HELP_PAGES.get(section, help_embed_overview)
        await interaction.response.edit_message(embed=embed_fn(), view=self)

    @discord.ui.button(label="Overview", style=discord.ButtonStyle.primary)
    async def btn_overview(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._switch(interaction, "overview")

    @discord.ui.button(label="Math", style=discord.ButtonStyle.secondary)
    async def btn_math(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._switch(interaction, "math")

    @discord.ui.button(label="Physics", style=discord.ButtonStyle.secondary)
    async def btn_physics(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._switch(interaction, "physics")

    @discord.ui.button(label="Chemistry", style=discord.ButtonStyle.secondary)
    async def btn_chemistry(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._switch(interaction, "chemistry")


class HelpCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="help", description="Bot guide (Math, Physics, Chemistry)")
    @app_commands.describe(public="Post in the channel? (default: private)")
    async def help_cmd(self, interaction: discord.Interaction, public: bool = False):
        embed = help_embed_overview()
        view = HelpView(author_id=interaction.user.id)
        await send_reply(interaction, embed=embed, view=view, public=public)


async def setup(bot: commands.Bot):
    await bot.add_cog(HelpCog(bot))

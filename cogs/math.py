# math.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from sympy import (
    Matrix, simplify, factor as sp_factor, expand as sp_expand,
    limit as sp_limit, series as sp_series, Symbol, expand_trig
)
from utils.safe_sympy import (
    parse_expr_safe, solve_expr_or_equation, solve_eq_safe, diff_safe, integrate_safe,
    dsolve_first_order, dsolve_second_order
)

# ---------------------------------
# Simple reply helper
# ---------------------------------
async def send_reply(interaction: discord.Interaction,
                     content: str | None = None,
                     embed: discord.Embed | None = None,
                     public: bool = False):
    """
    If public=True, send a public message; otherwise, send ephemeral (private).
    """
    ephemeral = not bool(public)
    if interaction.response.is_done():
        await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)

class MathCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    math = app_commands.Group(name="math", description="Math tools")

    # ------------------------
    # /math calc <expr>
    # ------------------------
    @math.command(name="calc", description="Evaluate expression or solve equation if it contains '='")
    @app_commands.describe(expr="E.g., (2+3)^3 or x^2=9", var="Variable to solve for (if equation)", public="Public response?")
    async def math_calc(self, interaction: discord.Interaction,
                        expr: str, var: str = "x", public: bool = False):
        try:
            val = solve_expr_or_equation(expr, var=var)
            await send_reply(interaction, content=f"`{val}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /math factor / expand
    # ------------------------
    @math.command(name="factor", description="Factor an expression")
    async def math_factor(self, interaction: discord.Interaction, expr: str, public: bool = False):
        try:
            e = parse_expr_safe(expr)
            await send_reply(interaction, content=f"`{sp_factor(e)}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    @math.command(name="expand", description="Expand an expression")
    async def math_expand(self, interaction: discord.Interaction, expr: str, public: bool = False):
        try:
            e = parse_expr_safe(expr)
            await send_reply(interaction, content=f"`{sp_expand(e)}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /math limit
    # ------------------------
    @math.command(name="limit", description="Limit of f(x) as x->a")
    @app_commands.describe(expr="E.g., sin(x)/x", var="E.g., x", to="E.g., 0 or oo", public="Public response?")
    async def math_limit(self, interaction: discord.Interaction, expr: str, var: str, to: str, public: bool = False):
        try:
            e = parse_expr_safe(expr)
            x = Symbol(var)
            a = parse_expr_safe(to)
            val = sp_limit(e, x, a)
            await send_reply(interaction, content=f"`{val}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /math series
    # ------------------------
    @math.command(name="series", description="Taylor series of f(x) at x0 up to order n")
    @app_commands.describe(expr="E.g., exp(x)", var="E.g., x", x0="E.g., 0", n="E.g., 5", public="Public response?")
    async def math_series(self, interaction: discord.Interaction, expr: str, var: str, x0: str, n: int, public: bool = False):
        try:
            e = parse_expr_safe(expr)
            x = Symbol(var)
            a = parse_expr_safe(x0)
            ser = sp_series(e, x, a, n+1).removeO()
            await send_reply(interaction, content=f"`{ser}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /math solve
    # ------------------------
    @math.command(name="solve", description="Solve equation: left = right")
    async def math_solve(self, interaction: discord.Interaction, left: str, right: str, var: str = "x", public: bool = False):
        try:
            sol = solve_eq_safe(left, right, var=var)
            await send_reply(interaction, content=f"`{sol}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /math diff / integrate
    # ------------------------
    @math.command(name="diff", description="Differentiate f(x) with order k")
    async def math_diff(self, interaction: discord.Interaction, expr: str, var: str = "x", order: int = 1, public: bool = False):
        try:
            val = diff_safe(expr, var=var, order=order)
            # Present in expanded trigonometric form for readability.
            val = simplify(expand_trig(val))
            await send_reply(interaction, content=f"`{val}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    @math.command(name="integrate", description="Integrate f(x); definite integral if limits are given")
    @app_commands.describe(a="lower limit (optional)", b="upper limit (optional)")
    async def math_integrate(self, interaction: discord.Interaction, expr: str, var: str = "x", a: str | None = None, b: str | None = None, public: bool = False):
        try:
            val = integrate_safe(expr, var=var, a=a, b=b)
            await send_reply(interaction, content=f"`{val}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /math dsolve1 / dsolve2
    # ------------------------
    @math.command(name="dsolve1", description="Solve a 1st-order ODE. Example: y' + y = x")
    @app_commands.describe(eq="E.g., y' + y = x", ics='Initial condition "x0, y0" (optional)', public="Public response?")
    async def math_dsolve1(self, interaction: discord.Interaction, eq: str, ics: str | None = None, public: bool = False):
        try:
            sol = dsolve_first_order(eq, ics=ics)
            await send_reply(interaction, content=f"`{sol}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Could not solve — {e}", public=False)

    @math.command(name="dsolve2", description="Solve a 2nd-order ODE. Example: y'' - 3y' + 2y = 0")
    @app_commands.describe(eq="E.g., y'' - 3y' + 2y = 0", ics='Initial conditions "x0, y0, y\'0" (optional)', public="Public response?")
    async def math_dsolve2(self, interaction: discord.Interaction, eq: str, ics: str | None = None, public: bool = False):
        try:
            sol = dsolve_second_order(eq, ics=ics)
            await send_reply(interaction, content=f"`{sol}`", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Could not solve — {e}", public=False)

    # ------------------------
    # Context Menu: "Compute with /math"
    # ------------------------
    async def _ctx_compute_callback(self, interaction: discord.Interaction, message: discord.Message):
        try:
            expr = message.content.strip()
            val = simplify(parse_expr_safe(expr))
            await send_reply(interaction, content=f"`{val}`", public=False)
        except Exception as e:
            await send_reply(interaction, content=f"Could not evaluate: {e}", public=False)

    @commands.Cog.listener()
    async def on_ready(self):
        # Register context menu only once
        if not hasattr(self, "_ctx_registered"):
            self._ctx_registered = True
            ctx = app_commands.ContextMenu(name="Compute with /math", callback=self._ctx_compute_callback)
            self.bot.tree.add_command(ctx)

async def setup(bot: commands.Bot):
    await bot.add_cog(MathCog(bot))

# physics.py
from __future__ import annotations
import discord
from discord.ext import commands
from discord import app_commands
from pint import UnitRegistry
from utils.safe_sympy import CONSTANTS

# ---------------------------------
# Simple reply helper
# ---------------------------------
async def send_reply(interaction: discord.Interaction,
                     content: str | None = None,
                     embed: discord.Embed | None = None,
                     public: bool = False):
    ephemeral = not bool(public)
    if interaction.response.is_done():
        await interaction.followup.send(content=content, embed=embed, ephemeral=ephemeral)
    else:
        await interaction.response.send_message(content=content, embed=embed, ephemeral=ephemeral)

# Unit registry (pint)
_UR = UnitRegistry()
_Q = _UR.Quantity

# Broad unit autocomplete (up to 20 suggestions)
async def unit_autocomplete(_, current: str):
    q = (current or "").lower()
    try:
        names = [name for name in _UR._units.keys() if q in name.lower()]
    except Exception:
        # minimal fallback
        names = ["m", "km", "s", "h", "kg", "N", "J", "Pa", "W", "V", "A", "ohm", "m/s", "km/h", "m/s^2", "K", "degC", "L", "atm", "mol"]
        names = [n for n in names if q in n.lower()]
    names.sort()
    names = names[:20]
    return [app_commands.Choice(name=n, value=n) for n in names]

class PhysicsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    phys = app_commands.Group(name="phys", description="Physics tools")

    # ------------------------
    # /phys const
    # ------------------------
    @phys.command(name="const", description="Show a physical constant by symbol")
    @app_commands.describe(name="E.g., c, h, k_B, N_A...", public="Public response?")
    async def phys_const(self, interaction: discord.Interaction, name: str, public: bool = False):
        k = name.strip()
        if k not in CONSTANTS:
            await send_reply(interaction, content="Constant not found.", public=False)
            return
        desc, val, unit = CONSTANTS[k]
        embed = discord.Embed(title=f"Constant: {k}", description=desc)
        embed.add_field(name="Value", value=f"`{val}`")
        embed.add_field(name="Unit", value=f"`{unit}`")
        await send_reply(interaction, embed=embed, public=public)

    # ------------------------
    # /phys convert
    # ------------------------
    @phys.command(name="convert", description="Convert a quantity between units")
    @app_commands.describe(value="E.g., 10", src_unit="E.g., m/s", dst_unit="E.g., km/h", public="Public response?")
    @app_commands.autocomplete(src_unit=unit_autocomplete, dst_unit=unit_autocomplete)
    async def phys_convert(self, interaction: discord.Interaction,
                           value: float,
                           src_unit: str,
                           dst_unit: str,
                           public: bool = False):
        try:
            q = _Q(value, src_unit).to(dst_unit)
            await send_reply(interaction, content=f"`{value} {src_unit}` = **{q:~P}**", public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid conversion — {e}", public=False)

    # ------------------------
    # /phys ohm  (V = I * R) — provide exactly two
    # ------------------------
    @phys.command(name="ohm", description="Ohm's Law: V = I * R (provide exactly two)")
    @app_commands.describe(v="Voltage (e.g., 5 V)", i="Current (e.g., 2 A)", r="Resistance (e.g., 10 ohm)", public="Public response?")
    async def phys_ohm(self, interaction: discord.Interaction,
                       v: str | None = None, i: str | None = None, r: str | None = None,
                       public: bool = False):
        try:
            given = [x is not None and x.strip() != "" for x in (v, i, r)]
            if sum(given) != 2:
                await send_reply(interaction, content="Provide exactly TWO among V, I, R.", public=False)
                return

            V = _Q(v) if v else None
            I = _Q(i) if i else None
            R = _Q(r) if r else None

            if V is None:
                V = I * R
            elif I is None:
                I = V / R
            else:
                R = V / I

            embed = discord.Embed(title="Ohm's Law")
            embed.add_field(name="V", value=f"`{V:~P}`")
            embed.add_field(name="I", value=f"`{I:~P}`")
            embed.add_field(name="R", value=f"`{R:~P}`")
            await send_reply(interaction, embed=embed, public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

    # ------------------------
    # /phys kinematics (SUVAT)
    # ------------------------
    @phys.command(name="kinematics", description="Kinematics (SUVAT): provide 3 to compute the others")
    @app_commands.describe(
        s="Displacement (e.g., 10 m)",
        u="Initial velocity (e.g., 2 m/s)",
        v="Final velocity (e.g., 6 m/s)",
        a="Acceleration (e.g., 1 m/s^2)",
        t="Time (e.g., 4 s)",
        public="Public response?"
    )
    async def phys_kinematics(self, interaction: discord.Interaction,
                              s: str | None = None, u: str | None = None, v: str | None = None,
                              a: str | None = None, t: str | None = None,
                              public: bool = False):
        """
        Equations:
          v = u + a t
          s = u t + 1/2 a t^2
          v^2 = u^2 + 2 a s
        Strategy: fill in via common combinations.
        """
        try:
            q = {"s": _Q(s) if s else None,
                 "u": _Q(u) if u else None,
                 "v": _Q(v) if v else None,
                 "a": _Q(a) if a else None,
                 "t": _Q(t) if t else None}

            # 1) v = u + a t
            if q["v"] is None and q["u"] is not None and q["a"] is not None and q["t"] is not None:
                q["v"] = q["u"] + q["a"] * q["t"]
            if q["u"] is None and q["v"] is not None and q["a"] is not None and q["t"] is not None:
                q["u"] = q["v"] - q["a"] * q["t"]
            if q["a"] is None and q["v"] is not None and q["u"] is not None and q["t"] is not None:
                q["a"] = (q["v"] - q["u"]) / q["t"]
            if q["t"] is None and q["a"] is not None and q["v"] is not None and q["u"] is not None:
                q["t"] = (q["v"] - q["u"]) / q["a"]

            # 2) s = u t + (1/2) a t^2
            if q["s"] is None and q["u"] is not None and q["t"] is not None and q["a"] is not None:
                q["s"] = q["u"] * q["t"] + 0.5 * q["a"] * (q["t"] ** 2)

            # 3) v^2 = u^2 + 2 a s
            if q["s"] is None and q["v"] is not None and q["u"] is not None and q["a"] is not None:
                q["s"] = (q["v"] ** 2 - q["u"] ** 2) / (2 * q["a"])
            if q["v"] is None and q["u"] is not None and q["a"] is not None and q["s"] is not None:
                q["v"] = ((q["u"] ** 2 + 2 * q["a"] * q["s"]) ** 0.5).to(q["u"].units)

            embed = discord.Embed(title="Kinematics (SUVAT)")
            for label in ("s", "u", "v", "a", "t"):
                val = q[label]
                embed.add_field(name=label, value=(f"`{val:~P}`" if val is not None else "—"), inline=True)

            await send_reply(interaction, embed=embed, public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Invalid input — {e}", public=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(PhysicsCog(bot))

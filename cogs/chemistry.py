# chemistry.py
from __future__ import annotations
import re
import discord
from discord.ext import commands
from discord import app_commands
import sympy as sp

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

# ===========================================
# STOICHIOMETRIC BALANCING (Linear Algebra)
# ===========================================

_elem_pat = re.compile(r"([A-Z][a-z]?)(\d*)")
_group_pat = re.compile(r"\(([^()]+)\)(\d+)")

def _expand_groups(formula: str) -> str:
    """
    Expand groups like (SO4)3 -> S3O12
    """
    while True:
        m = _group_pat.search(formula)
        if not m:
            return formula
        inside, mult = m.group(1), int(m.group(2))
        counts = _count_atoms_basic(inside)
        expanded = "".join(f"{el}{cnt*mult if cnt*mult!=1 else ''}" for el, cnt in counts.items())
        formula = formula[:m.start()] + expanded + formula[m.end():]

def _count_atoms_basic(formula: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for el, num in _elem_pat.findall(formula):
        n = int(num) if num else 1
        counts[el] = counts.get(el, 0) + n
    return counts

def parse_formula(formula: str) -> dict[str, int]:
    f = _expand_groups(formula)
    return _count_atoms_basic(f)

def parse_side(side: str) -> list[tuple[str, dict[str,int]]]:
    """
    "Fe + O2" -> [("Fe", {"Fe":1}), ("O2", {"O":2})]
    """
    terms = [t.strip() for t in side.split("+")]
    out = []
    for t in terms:
        out.append((t, parse_formula(t)))
    return out

def collect_elements(terms: list[tuple[str, dict[str,int]]]) -> list[str]:
    els = set()
    for _, d in terms:
        els |= set(d.keys())
    return sorted(els)

def build_matrix(lhs_terms, rhs_terms):
    """
    Build A x = 0 for element conservation.
    Left-hand side positive, right-hand side negative.
    """
    elements = sorted(set(collect_elements(lhs_terms)) | set(collect_elements(rhs_terms)))
    cols = len(lhs_terms) + len(rhs_terms)
    A = sp.zeros(len(elements), cols)
    for r, el in enumerate(elements):
        # LHS
        for c, (_, d) in enumerate(lhs_terms):
            A[r, c] = d.get(el, 0)
        # RHS
        offset = len(lhs_terms)
        for c, (_, d) in enumerate(rhs_terms):
            A[r, offset + c] = -d.get(el, 0)
    return A

def nullspace_integer(A: sp.Matrix) -> list[int]:
    ns = A.nullspace()
    if not ns:
        raise ValueError("No non-trivial solution.")
    vec = ns[0]
    # make integer via least common multiple of denominators
    lcm = sp.ilcm(*[sp.denom(x) for x in vec])
    vec = (vec * lcm).applyfunc(sp.simplify)
    # make positive (by convention)
    sign = 1
    for x in vec:
        if x != 0:
            sign = int(sp.sign(x))
            break
    vec = vec * sign
    # reduce by gcd
    gcd = int(sp.igcd(*[abs(int(x)) for x in vec]))
    vec = [int(x)//gcd for x in vec]
    return vec

def balance_equation(equation: str) -> tuple[list[int], list[str], list[str]]:
    """
    "Fe + O2 = Fe2O3" -> minimal integer coefficients
    """
    left, right = [s.strip() for s in equation.split("=")]
    lhs_terms = parse_side(left)
    rhs_terms = parse_side(right)
    A = build_matrix(lhs_terms, rhs_terms)
    coeffs = nullspace_integer(A)
    nL = len(lhs_terms)
    lhs_coeffs = coeffs[:nL]
    rhs_coeffs = coeffs[nL:]
    lhs_names = [name for name, _ in lhs_terms]
    rhs_names = [name for name, _ in rhs_terms]
    return (lhs_coeffs + rhs_coeffs, lhs_names, rhs_names)

def format_balanced(lhs_coeffs, lhs_names, rhs_coeffs, rhs_names) -> str:
    def fmt(c, n): return (f"{c} " if c != 1 else "") + n
    left = " + ".join(fmt(c, n) for c, n in zip(lhs_coeffs, lhs_names))
    right = " + ".join(fmt(c, n) for c, n in zip(rhs_coeffs, rhs_names))
    return left + " = " + right

class ChemistryCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    chem = app_commands.Group(name="chem", description="Chemistry tools")

    @chem.command(name="balance", description="Balance a chemical equation. E.g., Fe + O2 = Fe2O3")
    @app_commands.describe(equation="E.g., Fe + O2 = Fe2O3", public="Public response?")
    async def chem_balance(self, interaction: discord.Interaction, equation: str, public: bool = False):
        try:
            if "=" not in equation:
                await send_reply(interaction, content="Use the format: reactants = products", public=False)
                return
            coeffs, lhs_names, rhs_names = balance_equation(equation)
            nL = len(lhs_names)
            lhs_coeffs = coeffs[:nL]
            rhs_coeffs = coeffs[nL:]
            balanced = format_balanced(lhs_coeffs, lhs_names, rhs_coeffs, rhs_names)
            embed = discord.Embed(title="Balanced Equation", description=f"`{balanced}`")
            await send_reply(interaction, embed=embed, public=public)
        except Exception as e:
            await send_reply(interaction, content=f"Could not balance — {e}", public=False)

async def setup(bot: commands.Bot):
    await bot.add_cog(ChemistryCog(bot))

# safe_sympy.py
from __future__ import annotations
import re
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr as _parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
    function_exponentiation,
)

# ===============================
#   SAFE PARSER FOR EXPRESSIONS
# ===============================

# Deliberately DO NOT include 'y' as a free symbol to avoid conflicts with ODEs (y(x)).
# Common free symbols for algebra/calculus:
_symbols = {ch: sp.Symbol(ch) for ch in "xztuvwabc"}  # no 'y' here

_ALLOWED = {
    **_symbols,
    "pi": sp.pi,
    "E": sp.E,
    "I": sp.I,
    # Common math functions
    "sin": sp.sin, "cos": sp.cos, "tan": sp.tan,
    "asin": sp.asin, "acos": sp.acos, "atan": sp.atan,
    "sinh": sp.sinh, "cosh": sp.cosh, "tanh": sp.tanh,
    "exp": sp.exp, "log": sp.log, "ln": sp.log, "sqrt": sp.sqrt,
    "abs": sp.Abs, "floor": sp.floor, "ceiling": sp.ceiling,
    "sign": sp.sign, "re": sp.re, "im": sp.im,
}

_TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,                 # allow ^ as power
    function_exponentiation,
)

def _strip_outer_quotes(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s

def parse_expr_safe(s: str) -> sp.Expr:
    """
    Expression parser with restricted local dict.
    - Allows implicit multiplication
    - Converts ^ to **
    - DOES NOT allow 'y' as a free symbol (reserved for y(x) in ODEs)
    """
    s = _strip_outer_quotes(s)
    return _parse_expr(s, local_dict=_ALLOWED, transformations=_TRANSFORMS)

# =====================================
#   HELPERS FOR EQUATIONS / SOLVING
# =====================================

def solve_expr_or_equation(s: str, var: str = "x"):
    """
    If 's' contains '=', solve the equation (left = right) for 'var'.
    Otherwise, return the simplified expression.
    """
    s = _strip_outer_quotes(s)
    if "=" in s:
        left, right = s.split("=", 1)
        eq = sp.Eq(parse_expr_safe(left), parse_expr_safe(right))
        sol = sp.solve(eq, sp.Symbol(var))
        return sol
    else:
        return sp.simplify(parse_expr_safe(s))

def solve_eq_safe(left: str, right: str, var: str = "x"):
    eq = sp.Eq(parse_expr_safe(left), parse_expr_safe(right))
    return sp.solve(eq, sp.Symbol(var))

def diff_safe(expr: str, var: str = "x", order: int = 1):
    e = parse_expr_safe(expr)
    x = sp.Symbol(var)
    return sp.simplify(sp.diff(e, (x, order)))

def integrate_safe(expr: str, var: str = "x", a: str | None = None, b: str | None = None):
    e = parse_expr_safe(expr)
    x = sp.Symbol(var)
    if a is not None and b is not None:
        A = parse_expr_safe(a)
        B = parse_expr_safe(b)
        return sp.simplify(sp.integrate(e, (x, A, B)))
    return sp.simplify(sp.integrate(e, x))

# =====================================
#      ODE SUPPORT (1st and 2nd order)
# =====================================

def _prepare_ode_equation_text(eq: str, dep: str = "y", indep: str = "x") -> str:
    """
    Convert input like:
      y' + y = x
      y'' - 3y' + 2y = 0
    into something SymPy understands, using F(x) for y,
    and Derivative(F(x), x) / Derivative(F(x), x, x) for y' / y''.

    Robust to spaces and different prime characters. Avoids relying on \b after the apostrophe.
    """
    eq = _strip_outer_quotes(eq)
    eq = re.sub(r"\s+", " ", eq).strip()

    # Accept common prime variants
    prime = r"[\'’′]"  # ASCII ' , typographic ’, or prime ′

    # Replace y'' BEFORE y'
    eq = re.sub(rf"(?<!\w){dep}\s*{prime}{prime}(?!\w)", "Derivative(F(x), x, x)", eq)
    eq = re.sub(rf"(?<!\w){dep}\s*{prime}(?!\w)",       "Derivative(F(x), x)",     eq)

    # Replace standalone y with F(x)
    eq = re.sub(rf"(?<!\w){dep}(?!\w)", "F(x)", eq)

    # Force independent variable to 'x'
    if indep != "x":
        eq = re.sub(rf"(?<!\w){indep}(?!\w)", "x", eq)

    # If no '=', interpret as "= 0"
    if "=" not in eq:
        eq = f"{eq} = 0"

    return eq

def _parse_ode_to_eq(eq: str, dep: str = "y", indep: str = "x"):
    """
    Build a SymPy Eq(lhs, rhs) with F(x) as the unknown function.
    """
    eq = _prepare_ode_equation_text(eq, dep, indep)
    left, right = eq.split("=", 1)
    x = sp.Symbol("x")
    F = sp.Function("F")
    local = {**_ALLOWED, "x": x, "F": F, "Derivative": sp.Derivative}
    lhs = _parse_expr(left.strip(), local_dict=local, transformations=_TRANSFORMS)
    rhs = _parse_expr(right.strip(), local_dict=local, transformations=_TRANSFORMS)
    return sp.Eq(lhs, rhs), x, F(x)

def dsolve_first_order(eq: str, dep: str = "y", indep: str = "x", ics: str | None = None):
    """
    Solve a 1st-order ODE given as a string (supports y, y', x).
    ics (optional): "x0, y0"
    """
    E, x, y = _parse_ode_to_eq(eq, dep, indep)
    ic = None
    if ics:
        parts = [p.strip() for p in _strip_outer_quotes(ics).split(",")]
        if len(parts) == 2:
            x0, y0 = float(parts[0]), float(parts[1])
            ic = {y.subs(x, x0): y0}
    return sp.simplify(sp.dsolve(E, ics=ic))

def dsolve_second_order(eq: str, dep: str = "y", indep: str = "x", ics: str | None = None):
    """
    Solve a 2nd-order ODE given as a string (supports y, y', y'', x).
    ics (optional): "x0, y0, y'0"
    """
    E, x, y = _parse_ode_to_eq(eq, dep, indep)
    ic = None
    if ics:
        parts = [p.strip() for p in _strip_outer_quotes(ics).split(",")]
        if len(parts) == 3:
            x0, y0, ydot0 = float(parts[0]), float(parts[1]), float(parts[2])
            ic = {y.subs(x, x0): y0, sp.diff(y, x).subs(x, x0): ydot0}
    return sp.simplify(sp.dsolve(E, ics=ic))

# =====================================
#        USEFUL PHYSICAL CONSTANTS
# =====================================

CONSTANTS = {
    "c":  ("Speed of light",        299_792_458,            "m/s"),
    "h":  ("Planck constant",       6.62607015e-34,         "J*s"),
    "k_B":("Boltzmann constant",    1.380649e-23,           "J/K"),
    "N_A":("Avogadro constant",     6.02214076e23,          "1/mol"),
    "e":  ("Elementary charge",     1.602176634e-19,        "C"),
    "G":  ("Gravitational constant",6.67430e-11,            "m^3/(kg*s^2)"),
    "g0": ("Standard gravity",      9.80665,                "m/s^2"),
    "R":  ("Ideal gas constant",    8.314462618,            "J/(mol*K)"),
}

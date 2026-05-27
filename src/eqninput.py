from sympy.parsing.latex import parse_latex
from sympy import UnevaluatedExpr
from sympy.abc import r

BACKEND = "antlr"
STRICT = False

def parse_polar(eq1: string, eq2: string):
    expr1 = parse_latex(eq1, strict=STRICT, backend=BACKEND)
    expr2 = parse_latex(eq2, strict=STRICT, backend=BACKEND)

    return [expr1, expr2];

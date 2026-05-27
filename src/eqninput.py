from sympy.parsing.latex import parse_latex
from sympy.abc import theta

BACKEND = "antlr"
STRICT = False

def parse_polar(eqs):
    res = []
    err = []
    for eq in eqs:
        try:
            res.append(parse_latex(eq, strict=STRICT, backend=BACKEND))
            err.append(None)
        except Exception as e:
            res.append(None)
            err.append(str(e))
    return (res, err)

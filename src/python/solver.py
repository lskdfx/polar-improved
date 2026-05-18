from sympy import pi, solveset, nsolve, Eq, Interval, FiniteSet, N
from sympy.abc import theta

from time import monotonic

STRATEGY = "solveset"

def solveset_polar(exprs, domain, solutions):
    eqn = Eq(exprs[0], exprs[1])

    standard = solveset(eqn, theta, domain=domain)
    if isinstance(standard, FiniteSet):
        for theta_sym in standard:
            theta_float = N(theta_sym, 5)
            r = exprs[0].evalf(subs={theta: theta_sym}, n=5)
            solutions.append({ "solution": "standard", "theta": theta_float, "r": r })

def solve_polar_intersections(exprs):
    domain = Interval(0, 2*pi)
    solutions = []
    
    solve_before = monotonic();
    if STRATEGY == "solveset":
        solveset_polar(exprs, domain, solutions);
    else:
        raise Exception("invalid strategy");
    solve_after = monotonic();
    print(f"[solver] time {solve_after-solve_before} (strategy {STRATEGY})")

    zero1 = solveset(Eq(exprs[0], 0), theta, domain=domain)
    zero2 = solveset(Eq(exprs[1], 0), theta, domain=domain)

    if isinstance(zero1, FiniteSet) and isinstance(zero2, FiniteSet) and len(zero1) > 0 and len(zero2) > 0:
        solutions.append({ "solution": "origin" });

    return solutions

from sympy import pi, solveset, nsolve, Eq, Interval, FiniteSet, N, lambdify
from sympy.abc import theta
from scipy.optimize import fsolve
import numpy as np

from time import monotonic

STRATEGY = "fsolve"
PRECISION = 9

def solveset_polar(exprs, domain, solutions):
    eqn = Eq(exprs[0], exprs[1])

    solves = solveset(eqn, theta, domain=domain)
    if isinstance(solves, FiniteSet):
        for theta_sym in solves:
            theta_float = N(theta_sym, PRECISION)
            r = exprs[0].evalf(subs={theta: theta_sym}, n=PRECISION)
            solutions.append({ "solution": "standard", "theta": theta_float, "r": r })

def fsolve_polar(exprs, domain, solutions):
    eqn = lambdify(theta, (exprs[0]) - (exprs[1]), modules=["numpy"])

    if not isinstance(domain, Interval):
        raise Exception("invalid domain");

    d_start = float(domain.start)
    d_end = float(domain.end)
    guesses = np.linspace(d_start, d_end, num=1000, dtype=float)
    solves = fsolve(eqn, guesses);

    solves = solves[(solves >= d_start) & (solves <= d_end)];
    solves = np.unique(np.round(solves, decimals=PRECISION));

    for theta_nf in solves:
        theta_f = float(theta_nf)
        r = exprs[0].evalf(subs={theta: theta_f}, n=PRECISION)
        solutions.append({ "solution": "standard", "theta": theta_f, "r": r })

def solve_polar_intersections(exprs):
    domain = Interval(0, 2*pi)
    solutions = []
    
    solve_before = monotonic();
    if STRATEGY == "solveset":
        solveset_polar(exprs, domain, solutions);
    elif STRATEGY == "fsolve":
        fsolve_polar(exprs, domain, solutions);
    else:
        raise Exception("invalid strategy");
    solve_after = monotonic();
    print(f"[solver] time {solve_after-solve_before} (strategy {STRATEGY})")

    zero1 = solveset(Eq(exprs[0], 0), theta, domain=domain)
    zero2 = solveset(Eq(exprs[1], 0), theta, domain=domain)

    if isinstance(zero1, FiniteSet) and isinstance(zero2, FiniteSet) and len(zero1) > 0 and len(zero2) > 0:
        solutions.append({ "solution": "origin" });

    return solutions

def transform_solution(solution):
    if solution["solution"] == "standard" and solution["r"] < 0:
        solution["theta"] += np.pi;
        solution["r"] *= -1;
    return solution;

def polar_get_info(expr):
    solutions = solve_polar_intersections(expr);

    func1 = lambdify(theta, expr[0], modules="numpy");
    func2 = lambdify(theta, expr[1], modules="numpy");

    space = np.linspace(-2*np.pi, 2*np.pi, 1000);

    range1 = func1(space);
    range2 = func2(space);

    # apply negative transformation. matplotlib doesn't do this?
    space1 = space + (range1 < 0) * np.pi;
    space2 = space + (range2 < 0) * np.pi;
    range1 = np.abs(range1);
    range2 = np.abs(range2);

    return { "solutions": [transform_solution(solution) for solution in solutions], "expr1": [space1, range1], "expr2": [space2, range2] };

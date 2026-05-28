from sympy import pi, Interval, solveset, Eq, FiniteSet, N, lambdify
from sympy.abc import theta
from scipy.optimize import fsolve
import numpy as np
from math import ceil

from time import monotonic

STRATEGY = "fsolve"
PRECISION = 5
POINTS_PER_ONE = 100

def domain_linspace(domain):
    if not isinstance(domain, Interval):
        raise Exception("invalid domain");

    start = float(domain.start);
    end = float(domain.end);
    d_range = end - start
    points = ceil(d_range * POINTS_PER_ONE)
    return [np.linspace(start, end, num=points, dtype=float), start, end]

def solveset_polar(exprs, domain, solutions):
    eqn = Eq(exprs[0], exprs[1])

    solves = solveset(eqn, theta, domain=domain)
    if isinstance(solves, FiniteSet):
        for theta_sym in solves:
            theta_float = float(N(theta_sym, PRECISION))
            r = float(exprs[0].evalf(subs={theta: theta_sym}, n=PRECISION))
            solutions.append({ "solution": "standard", "theta": theta_float, "r": r })

def fsolve_polar(exprs, domain, solutions):
    eqn = lambdify(theta, (exprs[0]) - (exprs[1]), modules=["numpy"])

    guesses, d_start, d_end = domain_linspace(domain)
    solves = fsolve(eqn, guesses);

    solves = solves[(solves >= d_start) & (solves <= d_end)];
    solves = np.unique(np.round(solves, decimals=PRECISION));

    for theta_nf in solves:
        theta_f = float(theta_nf)
        r = float(exprs[0].evalf(subs={theta: theta_f}, n=PRECISION))
        solutions.append({ "solution": "standard", "theta": theta_f, "r": r })

def solve_polar_intersections(exprs, domain):
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
        fzero1 = []
        fzero2 = []
        for zero in zero1:
            fzero1.append(float(N(zero, PRECISION)));
        for zero in zero2:
            fzero2.append(float(N(zero, PRECISION)));
        solutions.append({ "solution": "origin", "expr1": fzero1, "expr2": fzero2 });

    return solutions

def polar_get_info(expr, domain):
    solutions = solve_polar_intersections(expr, domain);

    func1 = lambdify(theta, expr[0], modules="numpy");
    func2 = lambdify(theta, expr[1], modules="numpy");

    space, _, _ = domain_linspace(domain);

    range1 = func1(space);
    range2 = func2(space);

    # apply negative transformation. matplotlib doesn't do this?
    t_space1 = space + (range1 < 0) * np.pi;
    t_space2 = space + (range2 < 0) * np.pi;
    t_range1 = np.abs(range1);
    t_range2 = np.abs(range2);

    def transform_solution(solution):
        if solution["solution"] == "standard" and solution["r"] < 0:
            solution["transformed"] = True;
            solution["old_theta"] = solution["theta"];
            solution["old_r"] = solution["r"];
            solution["theta"] += np.pi;
            solution["r"] *= -1;
        else:
            solution["transformed"] = False
        return solution;

    return { "solutions": [transform_solution(solution) for solution in solutions], "expr1": [t_space1, t_range1], "expr2": [t_space2, t_range2], "raw": [space, range1, range2] };

from sympy import pi, Interval, solveset, Eq, FiniteSet, N, lambdify
from sympy.abc import theta
from scipy.optimize import fsolve
import numpy as np
from math import ceil

from time import monotonic

STRATEGY = "fsolve"
PRECISION = 9
POINTS_PER_ONE = 100


def domain_linspace(domain):
    if not isinstance(domain, Interval):
        raise Exception("invalid domain")

    start = float(domain.start)
    end = float(domain.end)
    d_range = end - start
    points = ceil(d_range * POINTS_PER_ONE)
    return [np.linspace(start, end, num=points, dtype=float), start, end]


def solveset_polar(exprs, domain, solutions):
    eqn = Eq(exprs[0], exprs[1])

    solves = solveset(eqn, theta, domain=domain)
    if isinstance(solves, FiniteSet):
        for theta_sym in solves:
            theta_float = N(theta_sym, PRECISION)
            r = exprs[0].evalf(subs={theta: theta_sym}, n=PRECISION)
            solutions.append({"solution": "standard", "theta": theta_float, "r": r})


def fsolve_polar(exprs, domain, solutions):
    eqn = lambdify(theta, (exprs[0]) - (exprs[1]), modules=["numpy"])

    guesses, d_start, d_end = domain_linspace(domain)
    solves = fsolve(eqn, guesses)

    solves = solves[(solves >= d_start) & (solves <= d_end)]
    solves = np.unique(np.round(solves, decimals=PRECISION))

    for theta_nf in solves:
        theta_f = float(theta_nf)
        r = exprs[0].evalf(subs={theta: theta_f}, n=PRECISION)
        solutions.append({"solution": "standard", "theta": theta_f, "r": r})


def solve_polar_intersections(exprs, domain):
    solutions = []

    solve_before = monotonic()
    if STRATEGY == "solveset":
        solveset_polar(exprs, domain, solutions)
    elif STRATEGY == "fsolve":
        fsolve_polar(exprs, domain, solutions)
    else:
        raise Exception("invalid strategy")
    solve_after = monotonic()
    print(f"[solver] time {solve_after - solve_before} (strategy {STRATEGY})")

    zero1 = solveset(Eq(exprs[0], 0), theta, domain=domain)
    zero2 = solveset(Eq(exprs[1], 0), theta, domain=domain)

    if (
        isinstance(zero1, FiniteSet)
        and isinstance(zero2, FiniteSet)
        and len(zero1) > 0
        and len(zero2) > 0
    ):
        solutions.append({"solution": "origin"})

    return solutions


def solve_all_intersections(exprs, domain):
    n = len(exprs)
    results = {}
    for i in range(n):
        for j in range(i + 1, n):
            expr_pair = [exprs[i], exprs[j]]
            sol = solve_polar_intersections(expr_pair, domain)
            results[(i, j)] = [transform_solution(s) for s in sol]
    return results


def transform_solution(solution):
    if solution["solution"] == "standard" and solution["r"] < 0:
        solution["transformed"] = True
        solution["old_theta"] = solution["theta"]
        solution["old_r"] = solution["r"]
        solution["theta"] += np.pi
        solution["r"] *= -1
    else:
        solution["transformed"] = False
    return solution


def polar_get_info(exprs, domain):
    funcs = []
    ranges = []
    spaces = []
    curves = []
    solutions = solve_all_intersections(exprs, domain)
    space, _, _ = domain_linspace(domain)

    for i in range(len(exprs)):
        funcs.append(lambdify(theta, exprs[i], modules="numpy"))
        ranges.append(funcs[i](space))
        spaces.append(space + (ranges[i] < 0) * np.pi)
        ranges[i] = np.abs(ranges[i])

    n = len(exprs)

    for i in range(n):
        curves.append(
            {
                "label": f"f{i + 1}",
                "theta": spaces[i],
                "r": ranges[i],
            }
        )
    sols = []
    for sol in solutions.values():
        sols.extend(sol)
    return {
        "solutions": sols,
        "curves": curves,
    }

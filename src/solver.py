from sympy import pi, Interval, solveset, Eq, FiniteSet, N, lambdify, integrate, Symbol
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
    solves = np.sort(solves)
    
    extras = np.abs(eqn(solves))
    solves = solves[extras < 1e-6]
    
    if len(solves) > 1:
        mask = np.concatenate([[True], np.diff(solves) > 1e-4])
        solves = solves[mask]
    
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
    if n > 6:
        return {}
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
        solution["theta"] %= 2 * np.pi
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

def get_unique_domain(expr, full_domain):
    if float(full_domain.end) - float(full_domain.start) <= np.pi + 1e-6:
        return full_domain, False
    f = lambdify(theta, expr, modules='numpy')
    test_points = np.linspace(0, np.pi, 200)
    for t in test_points:
        r_t = f(t)
        r_tp = f(t + np.pi)
        if r_t >= 0 and r_tp >= 0:
            return full_domain, False
        if abs(r_t + r_tp) > 1e-6 * (abs(r_t) + 1):
            return full_domain, False
    for t in test_points:
        if f(t) < -1e-6:
            return full_domain, False  
    return full_domain, True

def solve_region_areas(exprs, domain, curves, solutions):
    regions = []
    if len(exprs) != 2:
        return []
    theta_values = [float(domain.left), float(domain.right)]
    for expr in exprs:
        zeros = solveset(Eq(expr, 0), theta, domain=domain)
        if isinstance(zeros, FiniteSet):
            for z in zeros:
                theta_values.append(float(N(z)))
    for sol in solutions:
        if sol["solution"] == "standard":
            theta_values.append(sol["theta"])
    
    theta_values = sorted(set(theta_values))
    unique = [0]
    for t in theta_values:
        if t - unique[-1] > 1e-3:
            unique.append(t)
    theta_values = unique
    
    print("Unique thetas:", len(theta_values))
    retracing = [get_unique_domain(expr, domain)[1] for expr in exprs]
    f0 = lambdify(theta, exprs[0], modules='numpy')
    f1 = lambdify(theta, exprs[1], modules='numpy')
     
    for i in range(len(theta_values) - 1):
        theta_left = theta_values[i]
        theta_right = theta_values[i+1]
        theta_mid = (theta_left + theta_right) / 2
        r0_signed = float(f0(theta_mid))
        r1_signed = float(f1(theta_mid))
        r0 = abs(r0_signed)
        r1 = abs(r1_signed)
        if abs(theta_left - theta_right) <= 1e-9:
            continue
        if r0 < r1:
            inner = 0
            outer = 1
            outer_signed = r1_signed
            outer_retraces = retracing[1]
            
        else:
            inner = 1
            outer = 0
            outer_signed = r0_signed
            outer_retraces = retracing[0]
        inner_signed = r0_signed if inner == 0 else r1_signed
        inner_retraces = retracing[inner]
        if outer_retraces and outer_signed < 0:
            if inner_retraces and inner_signed <0:
                continue
            if abs(inner_signed) < 1e-9:
                continue
        # origin to first function
        regions.append({
            "id": len(regions),
            "theta1": theta_left,
            "theta2": theta_right,
            "r_inner_expr": 0,
            "r_outer_expr": exprs[inner],
            "inner_idx": -1,
            "outer_idx": inner,
            "area": float(integrate((exprs[inner]**2)/2, (theta, theta_left, theta_right))),
            "label": f"Origin → f{inner+1}",
        })
        #first function to second
        regions.append({
            "id": len(regions),
            "theta1": theta_left,
            "theta2": theta_right,
            "r_inner_expr": exprs[inner],
            "r_outer_expr": exprs[outer],
            "inner_idx": inner,
            "outer_idx": outer,
            "area": float(integrate(((exprs[outer]**2)-(exprs[inner]**2))/2, (theta, theta_left, theta_right))),
            "label": f"f{inner+1} → f{outer+1}",
        })
    return regions

def region_on_click(exprs, theta, r, regions):
    if len(exprs) != 2:
        return None
    for region in regions:
        if not (region["theta1"] <= theta <= region["theta2"]):
            continue
        r_inner = 0 if region["inner_idx"] == -1 else float(lambdify(theta, region["r_inner_expr"])(theta))
        r_outer = float(lambdify(theta, region["r_outer_expr"])(theta))
        if r_inner <= r <= r_outer:
            return region
    return None

def compute_frames_animation(region, curves):
    theta_start = region["theta1"]
    theta_end = region["theta2"]
    frames = []
    for i in range(1, 31):
        frac = i/30
        theta_current = theta_start + frac * (theta_end - theta_start)
        theta_grid = np.linspace(theta_start, theta_current, 50)
        outer_r = np.interp(theta_grid, curves[region["outer_idx"]]["theta"], curves[region["outer_idx"]]["r"])
        inner_r = np.zeros(50) if region["inner_idx"] == -1 else np.interp(theta_grid, curves[region["inner_idx"]]["theta"], curves[region["inner_idx"]]["r"])
        list_theta = np.concatenate([theta_grid, theta_grid[::-1]])
        list_r = np.concatenate([outer_r, inner_r[::-1]])
        frames.append({"theta": list_theta.tolist(), "r": list_r.tolist()})
    return frames

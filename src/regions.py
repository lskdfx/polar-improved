import numpy as np
from sympy import solveset, Eq, FiniteSet, N, lambdify, integrate
from sympy.abc import theta as sym_theta


def get_unique_domain(expr, full_domain):
    if float(full_domain.end) - float(full_domain.start) <= np.pi + 1e-6:
        return full_domain, False
    f = lambdify(sym_theta, expr, modules="numpy")
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
        zeros = solveset(Eq(expr, 0), sym_theta, domain=domain)
        if isinstance(zeros, FiniteSet):
            for z in zeros:
                theta_values.append(float(N(z)))
    for sol in solutions:
        if sol["solution"] == "standard":
            theta_values.append(float(sol["theta"]))

    theta_values = sorted(set(theta_values))
    unique = [theta_values[0]]
    for t in theta_values[1:]:
        if t - unique[-1] > 1e-3:
            unique.append(t)
    theta_values = unique

    print(f"[regions] unique thetas: {len(theta_values)}")
    retracing = [get_unique_domain(expr, domain)[1] for expr in exprs]
    f0 = lambdify(sym_theta, exprs[0], modules="numpy")
    f1 = lambdify(sym_theta, exprs[1], modules="numpy")

    for i in range(len(theta_values) - 1):
        theta_left = theta_values[i]
        theta_right = theta_values[i + 1]
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
            if inner_retraces and inner_signed < 0:
                continue
            if abs(inner_signed) < 1e-9:
                continue
        # origin to inner curve
        regions.append({
            "id": len(regions),
            "theta1": theta_left,
            "theta2": theta_right,
            "r_inner_expr": 0,
            "r_outer_expr": exprs[inner],
            "inner_idx": -1,
            "outer_idx": inner,
            "area": float(integrate((exprs[inner] ** 2) / 2, (sym_theta, theta_left, theta_right))),
            "label": f"Origin → f{inner + 1}",
        })
        # inner curve to outer curve
        regions.append({
            "id": len(regions),
            "theta1": theta_left,
            "theta2": theta_right,
            "r_inner_expr": exprs[inner],
            "r_outer_expr": exprs[outer],
            "inner_idx": inner,
            "outer_idx": outer,
            "area": float(integrate(((exprs[outer] ** 2) - (exprs[inner] ** 2)) / 2, (sym_theta, theta_left, theta_right))),
            "label": f"f{inner + 1} → f{outer + 1}",
        })
    return regions


def region_on_click(exprs, theta_val, r_val, regions):
    if len(exprs) != 2:
        return None
    for region in regions:
        if not (region["theta1"] <= theta_val <= region["theta2"]):
            continue
        if region["inner_idx"] == -1:
            r_inner = 0.0
        else:
            r_inner = float(lambdify(sym_theta, region["r_inner_expr"], modules="numpy")(theta_val))
        r_outer = float(lambdify(sym_theta, region["r_outer_expr"], modules="numpy")(theta_val))
        if r_inner <= r_val <= r_outer:
            return region
    return None


def compute_frames_animation(region, curves):
    theta_start = region["theta1"]
    theta_end = region["theta2"]
    frames = []
    for i in range(1, 31):
        frac = i / 30
        theta_current = theta_start + frac * (theta_end - theta_start)
        theta_grid = np.linspace(theta_start, theta_current, 50)
        outer_r = np.interp(theta_grid, curves[region["outer_idx"]]["theta"], curves[region["outer_idx"]]["r"])
        inner_r = (
            np.zeros(50)
            if region["inner_idx"] == -1
            else np.interp(theta_grid, curves[region["inner_idx"]]["theta"], curves[region["inner_idx"]]["r"])
        )
        list_theta = np.concatenate([theta_grid, theta_grid[::-1]])
        list_r = np.concatenate([outer_r, inner_r[::-1]])
        frames.append({"theta": list_theta.tolist(), "r": list_r.tolist()})
    return frames


def sample_region_polygon(region, n=80):
    t1 = region["theta1"]
    t2 = region["theta2"]
    if t2 - t1 < 1e-9:
        return [], []
    tg = np.linspace(t1, t2, n)
    outer_f = lambdify(sym_theta, region["r_outer_expr"], modules="numpy")
    outer_signed = np.atleast_1d(np.asarray(outer_f(tg), dtype=float))
    if outer_signed.size == 1:
        outer_signed = np.full(n, outer_signed[0])

    mid_idx = n // 2
    outer_sign = 1 if outer_signed[mid_idx] >= 0 else -1

    if region["inner_idx"] == -1:
        inner_signed = np.zeros(n)
        inner_r = inner_signed
    else:
        inner_f = lambdify(sym_theta, region["r_inner_expr"], modules="numpy")
        inner_signed = np.atleast_1d(np.asarray(inner_f(tg), dtype=float))
        if inner_signed.size == 1:
            inner_signed = np.full(n, inner_signed[0])
        inner_r = np.where(np.sign(inner_signed) == outer_sign, np.abs(inner_signed), 0.0)

    outer_r = np.abs(outer_signed)

    plot_theta = tg + (0.0 if outer_sign >= 0 else np.pi)
    theta_poly = np.concatenate([plot_theta, plot_theta[::-1]])
    r_poly = np.concatenate([outer_r, inner_r[::-1]])
    return np.degrees(theta_poly).tolist(), r_poly.tolist()

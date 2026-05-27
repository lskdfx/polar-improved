from eqninput import parse_polar
from solver import polar_get_info, solve_region_areas, region_on_click, compute_frames_animation, get_unique_domain
from sympy import Interval, pi
import numpy as np
DOMAIN = Interval(0,2*pi)
def build_graph_data(latex_strings):
    exprs, errors = parse_polar(latex_strings)
    if all(e is None for e in exprs):
        return {"curves": [], "intersections": [], "regions": [], "errors": errors, "exprs": exprs}
    info = polar_get_info(exprs, DOMAIN)
    regions = solve_region_areas(exprs, DOMAIN, info["curves"], info["solutions"])
    warnings = []
    for i, expr in enumerate(exprs):
        _, retraces = get_unique_domain(expr, DOMAIN)
        if retraces:
            warnings.append(f"f{i+1} retraces itself over [0, 2π] — consider using domain [0, π] for correct areas")
    return {"curves": info["curves"], "intersections": info["solutions"], "regions": regions, "errors": errors, "exprs": exprs, "warnings": warnings}

if __name__ == "__main__":
    data = build_graph_data([r"\sin(\theta)", r"2\cos(3\theta)"])
    print("Curves:", len(data["curves"]))
    print("Intersections:", len(data["intersections"]))
    print("Regions:", len(data["regions"]))
    if data["regions"]:
        for r in data["regions"]:
            print(f"  {r['label']}: θ=[{r['theta1']:.3f}, {r['theta2']:.3f}], area={r['area']:.3f}")
    print("Errors:", [e for e in data["errors"] if e])

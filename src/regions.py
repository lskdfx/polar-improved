import numpy as np
from sympy import Interval

PRECISION = 5
DECIMAL_PRECISION = 1/(10**PRECISION);

def domain_start_end(domain):
    if not isinstance(domain, Interval):
        raise Exception("invalid domain");
    start = float(domain.start);
    end = float(domain.end);

    return [start, end];

def sample_precomputed(info, point):
    space = info["raw"][0];
    r1 = info["raw"][1];
    r2 = info["raw"][2];
    idx = np.searchsorted(space, point);
    idx = min(idx, len(space) - 1);
    return r1[idx], r2[idx];

def polar_find_regions(info, domain):
    d_start, d_end = domain_start_end(domain);
    
    boundaries = set();
    
    # domain start just in case a curve doesn't start at origin
    boundaries.add(d_start);
    boundaries.add(d_end);
    
    for solution in info["solutions"]:
        if solution["solution"] == "standard":
            # old_theta since this isn't for graphing
            t = solution["old_theta"] if solution["transformed"] else solution["theta"];
            boundaries.add(t);
        elif solution["solution"] == "origin":
            for t in solution["expr1"]:
                boundaries.add(t);
            for t in solution["expr2"]:
                boundaries.add(t);
    
    boundaries = sorted(boundaries);
    
    regions = []
    count = 0;
    two_pi = 2 * np.pi;
    for one, two in zip(boundaries, boundaries[1:]):
        r1, r2 = sample_precomputed(info, (one + two) / 2);

        if np.sign(r1) != np.sign(r2):
            continue; # opposite sides

        if two - one < DECIMAL_PRECISION:
            continue; # fp

        regions.append([one, two])
        count = count + 1;

    print(f"[regions] found {count} regions");

    return regions

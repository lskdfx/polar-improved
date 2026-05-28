import numpy as np
from sympy import Interval

PRECISION = 5
POINTS_PER_ONE = 100
DECIMAL_PRECISION = 1/(10**PRECISION);

def domain_start_end(domain):
    if not isinstance(domain, Interval):
        raise Exception("invalid domain");
    start = float(domain.start);
    end = float(domain.end);

    return [start, end];

def sample_precomputed(space, r1, r2, point):
    idx = np.searchsorted(space, point);
    idx = min(idx, len(space) - 1);
    return r1[idx], r2[idx];

def _in_set_tol(value, value_set, tol=1e-4):
    return any(abs(value - v) < tol for v in value_set)

def polar_find_regions(info, domain):
    d_start, d_end = domain_start_end(domain);
    space = info["raw"][0]; r1 = info["raw"][1]; r2 = info["raw"][2];

    r1_zeros = set();
    r2_zeros = set();
    boundaries = set();
    boundaries.add(d_start);
    boundaries.add(d_end);

    for solution in info["solutions"]:
        if solution["solution"] == "standard":
            t = solution["old_theta"] if solution["transformed"] else solution["theta"];
            boundaries.add(t);
        elif solution["solution"] == "origin":
            for t in solution["expr1"]:
                boundaries.add(t);
                r1_zeros.add(t);
            for t in solution["expr2"]:
                boundaries.add(t);
                r2_zeros.add(t);

    boundaries = sorted(boundaries);

    sub_intervals = [];
    for one, two in zip(boundaries, boundaries[1:]):
        if two - one < DECIMAL_PRECISION:
            continue;
        midpoint = (one + two) / 2;
        m1, m2 = sample_precomputed(space, r1, r2, midpoint);
        s1 = int(np.sign(m1));
        s2 = int(np.sign(m2));
        if s1 != 0 and s1 == s2:
            kind = "kept";
        else:
            kind = "skip";
        sub_intervals.append({
            "start": one, "end": two,
            "m1": m1, "m2": m2,
            "s1": s1, "s2": s2,
            "kind": kind,
        });

    def outer_of(sub):
        if abs(sub["m1"]) >= abs(sub["m2"]):
            return (1, sub["s1"]);
        return (2, sub["s1"]);

    merged = [];
    i = 0;
    while i < len(sub_intervals):
        if sub_intervals[i]["kind"] != "kept":
            i += 1;
            continue;
        start = sub_intervals[i]["start"];
        end = sub_intervals[i]["end"];
        outer_curve, outer_sign = outer_of(sub_intervals[i]);
        j = i;
        while j + 2 < len(sub_intervals):
            skip = sub_intervals[j + 1];
            nxt = sub_intervals[j + 2];
            if skip["kind"] != "skip" or nxt["kind"] != "kept":
                break;
            next_outer = outer_of(nxt);
            if next_outer != (outer_curve, outer_sign):
                break;
            inner_zeros = r2_zeros if outer_curve == 1 else r1_zeros;
            if not (_in_set_tol(skip["start"], inner_zeros) and _in_set_tol(skip["end"], inner_zeros)):
                break;
            end = nxt["end"];
            j += 2;
        merged.append([start, end]);
        i = j + 1;

    two_pi = 2 * np.pi;
    DEDUP_TOL = 1e-3;
    seen_ranges = [];
    regions = [];
    for start, end in merged:
        r1_start = float(np.interp(start, space, r1));
        r1_end = float(np.interp(end, space, r1));
        r2_start = float(np.interp(start, space, r2));
        r2_end = float(np.interp(end, space, r2));

        end_sign = 0;
        for v in (r1_start, r2_start, r1_end, r2_end):
            if abs(v) > 1e-8:
                end_sign = int(np.sign(v));
                break;
        if end_sign == 0:
            continue;

        if end_sign < 0:
            t_start = (start + np.pi) % two_pi;
            t_end = (end + np.pi) % two_pi;
        else:
            t_start = start % two_pi;
            t_end = end % two_pi;

        is_dup = False;
        for s, e in seen_ranges:
            if abs(s - t_start) < DEDUP_TOL and abs(e - t_end) < DEDUP_TOL:
                is_dup = True;
                break;
        if is_dup:
            continue;
        seen_ranges.append((t_start, t_end));
        regions.append([start, end]);

    print(f"[regions] found {len(regions)} regions");

    def transform_region(region_bounds):
        start, end = region_bounds;

        start_idx = np.searchsorted(space, start, side='right');
        end_idx = np.searchsorted(space, end, side='left');
        inner_space = space[start_idx:end_idx];
        inner_r1 = r1[start_idx:end_idx];
        inner_r2 = r2[start_idx:end_idx];

        start_r1 = float(np.interp(start, space, r1));
        end_r1 = float(np.interp(end, space, r1));
        start_r2 = float(np.interp(start, space, r2));
        end_r2 = float(np.interp(end, space, r2));

        r_space = np.concatenate([[start], inner_space, [end]]);
        r1_arr = np.concatenate([[start_r1], inner_r1, [end_r1]]);
        r2_arr = np.concatenate([[start_r2], inner_r2, [end_r2]]);

        end_sign = 0;
        for v in (start_r1, start_r2, end_r1, end_r2):
            if abs(v) > 1e-8:
                end_sign = int(np.sign(v));
                break;
        if end_sign == 0:
            end_sign = 1;

        def matches_side(arr):
            return np.all((np.sign(arr) == end_sign) | (np.abs(arr) < 1e-8));
        r1_consistent = matches_side(r1_arr);
        r2_consistent = matches_side(r2_arr);

        mid = len(r_space) // 2;
        if r1_consistent and r2_consistent:
            if abs(r1_arr[mid]) >= abs(r2_arr[mid]):
                outer_r, inner_r = r1_arr, r2_arr;
            else:
                outer_r, inner_r = r2_arr, r1_arr;
        elif r1_consistent:
            outer_r, inner_r = r1_arr, r2_arr;
        elif r2_consistent:
            outer_r, inner_r = r2_arr, r1_arr;
        else:
            outer_r, inner_r = r1_arr, r2_arr;

        physical_theta = r_space + (0 if end_sign > 0 else np.pi);
        r_top = np.abs(outer_r);
        same_side = (np.sign(inner_r) == end_sign);
        r_bottom = np.where(same_side, np.abs(inner_r), 0.0);

        return { "bounds": region_bounds, "top": [physical_theta, r_top], "bottom": [physical_theta, r_bottom] };

    return [transform_region(region) for region in regions]

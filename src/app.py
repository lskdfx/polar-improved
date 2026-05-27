import dash
from dash import (
    dcc,
    html,
    Input,
    Output,
    State,
    clientside_callback,
    ctx,
    no_update,
)
import plotly.graph_objects as go
from sympy import Interval, pi
import numpy as np
import dash_mathlive
from eqninput import parse_polar
from solver import (
    polar_get_info,
    solve_region_areas,
    get_unique_domain,
)

DOMAIN = Interval(0, 2 * pi)
N_INPUTS = 6
CURVE_COLORS = ["#2196F3", "#F44336", "#4CAF50", "#FF9800", "#9C27B0", "#00BCD4"]
FILL_COLORS = [
    "rgba(33,150,243,0.35)",
    "rgba(244,67,54,0.35)",
    "rgba(76,175,80,0.35)",
    "rgba(255,152,0,0.35)",
    "rgba(156,39,176,0.35)",
    "rgba(0,188,212,0.35)",
]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "Polar Grapher"


def _empty_figure():
    fig = go.Figure()
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showgrid=True, gridcolor="#000000"),
            angularaxis=dict(
                visible=True,
                showgrid=True,
                gridcolor="#eee",
                direction="counterclockwise",
            ),
            bgcolor="#fff",
        ),
        paper_bgcolor="#fff",
        margin=dict(l=20, r=20, t=30, b=20),
        showlegend=True,
        legend=dict(x=1.05, y=1),
        uirevision="polar-graph",
    )
    return fig


def make_input(i):
    return html.Div(
        [
            html.Label(
                f"r = f{i + 1}(θ)",
                style={"fontSize": "13px", "color": "#888", "marginBottom": "2px"},
            ),
            dash_mathlive.dash_mathlive(
                id=f"eq-{i}",
                value="",
            ),
        ],
        style={"marginBottom": "10px"},
    )


app.layout = html.Div(
    [
        # ── Title bar ──────────────────────────────────────────────────────────
        html.Div(
            [
                html.H2(
                    "Polar Equation Grapher",
                    style={"margin": 0, "fontWeight": 700, "fontSize": "20px"},
                ),
                html.Span(
                    "Interactive polar graphing calculator",
                    style={
                        "fontSize": "13px",
                        "color": "rgba(255,255,255,0.65)",
                        "marginLeft": "16px",
                    },
                ),
            ],
            style={
                "padding": "14px 24px",
                "background": "linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)",
                "color": "white",
                "display": "flex",
                "alignItems": "center",
                "boxShadow": "0 2px 8px rgba(0,0,0,0.12)",
                "zIndex": 1,
                "position": "relative",
            },
        ),
        html.Div(
            [
                # ── Left panel: inputs + domain + dropdown ─────────────────────────
                html.Div(
                    [
                        html.Div(
                            [make_input(i) for i in range(N_INPUTS)],
                            id="inputs-container",
                        ),
                        html.Hr(style={"margin": "16px 0", "borderColor": "#e8e8e8"}),
                        # Domain controls
                        html.Div(
                            [
                                html.Div(
                                    "θ domain (radians):",
                                    style={
                                        "fontSize": "13px",
                                        "color": "#555",
                                        "fontWeight": 600,
                                        "marginBottom": "8px",
                                    },
                                ),
                                html.Div(
                                    [
                                        html.Span(
                                            "[",
                                            style={"color": "#999", "fontSize": "15px"},
                                        ),
                                        dcc.Input(
                                            id="domain-start",
                                            type="number",
                                            value=0,
                                            step=0.01,
                                            debounce=True,
                                            style={
                                                "width": "94px",
                                                "padding": "4px 8px",
                                                "border": "1px solid #ccc",
                                                "borderRadius": "4px",
                                                "fontSize": "13px",
                                                "textAlign": "center",
                                                "outline": "none",
                                                "background": "#fff",
                                            },
                                        ),
                                        html.Span(
                                            ",",
                                            style={
                                                "color": "#999",
                                                "fontSize": "15px",
                                                "margin": "0 2px",
                                            },
                                        ),
                                        dcc.Input(
                                            id="domain-end",
                                            type="number",
                                            value=round(2 * np.pi, 6),
                                            step=0.01,
                                            debounce=True,
                                            style={
                                                "width": "94px",
                                                "padding": "4px 8px",
                                                "border": "1px solid #ccc",
                                                "borderRadius": "4px",
                                                "fontSize": "13px",
                                                "textAlign": "center",
                                                "outline": "none",
                                                "background": "#fff",
                                            },
                                        ),
                                        html.Span(
                                            "]",
                                            style={"color": "#999", "fontSize": "15px"},
                                        ),
                                    ],
                                    style={
                                        "display": "flex",
                                        "alignItems": "center",
                                        "gap": "4px",
                                    },
                                ),
                            ],
                            style={"marginBottom": "16px"},
                        ),
                        html.Hr(style={"margin": "0 0 12px", "borderColor": "#e8e8e8"}),
                        html.Div(
                            id="warnings-box",
                            style={
                                "fontSize": "12px",
                                "color": "#d32f2f",
                                "marginBottom": "8px",
                                "minHeight": "16px",
                            },
                        ),
                        html.Label(
                            "Fill a region:",
                            style={
                                "fontSize": "13px",
                                "color": "#555",
                                "fontWeight": 600,
                            },
                        ),
                        dcc.Dropdown(
                            id="region-dropdown",
                            options=[],
                            placeholder="Select a region…",
                            style={"marginTop": "6px", "marginBottom": "12px"},
                            clearable=True,
                        ),
                        html.Button(
                            "Clear all fills",
                            id="clear-btn",
                            n_clicks=0,
                            style={
                                "width": "100%",
                                "padding": "8px 16px",
                                "borderRadius": "6px",
                                "border": "none",
                                "background": "#e53935",
                                "color": "white",
                                "cursor": "pointer",
                                "fontWeight": 600,
                                "fontSize": "14px",
                            },
                        ),
                    ],
                    style={
                        "width": "300px",
                        "minWidth": "260px",
                        "padding": "20px",
                        "borderRight": "1px solid #e8e8e8",
                        "overflowY": "auto",
                        "background": "#ffffff",
                        "boxShadow": "2px 0 8px rgba(0,0,0,0.04)",
                    },
                ),
                # ── Graph ──────────────────────────────────────────────────────────
                html.Div(
                    [
                        dcc.Graph(
                            id="polar-graph",
                            style={"height": "100%", "width": "100%"},
                            config={"displayModeBar": False},
                            figure=_empty_figure(),
                        ),
                    ],
                    style={
                        "flex": 1,
                        "minHeight": "500px",
                        "padding": "12px",
                        "background": "#fafafa",
                    },
                ),
            ],
            style={"display": "flex", "flex": 1, "overflow": "hidden"},
        ),
        dcc.Store(id="debounced-inputs", data=[""] * N_INPUTS),
        dcc.Store(id="graph-data", data=None),
        dcc.Store(id="fills-store", data={}),
        dcc.Store(id="error-flags", data=[]),
        dcc.Store(id="domain-store", data={"start": 0, "end": round(2 * np.pi, 6)}),
    ],
    style={
        "display": "flex",
        "flexDirection": "column",
        "height": "100vh",
        "fontFamily": "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
        "overflow": "hidden",
        "background": "#f5f5f5",
    },
)


@app.callback(
    Output("domain-store", "data"),
    Input("domain-start", "value"),
    Input("domain-end", "value"),
    prevent_initial_call=True,
)
def update_domain(start, end):
    if start is None or end is None:
        return no_update
    start = float(start)
    end = float(end)
    # ensure valid interval
    if start > end:
        start, end = end, start
    if abs(end - start) < 1e-12:
        end = start + 0.1
    return {"start": start, "end": end}


app.clientside_callback(
    Output("debounced-inputs", "data"),
    [Input(f"eq-{i}", "value") for i in range(N_INPUTS)],
    prevent_initial_call=True,
)


def _split_curve(theta, r):
    theta = np.asarray(theta, dtype=float)
    r = np.asarray(r, dtype=float)
    diffs = np.diff(theta)
    splits = np.where(np.abs(diffs) > 2.0)[0] + 1
    if len(splits) == 0:
        return [(theta, r)]
    return list(zip(np.split(theta, splits), np.split(r, splits)))


def _sample_curve(theta, r, t_target, tol=1e-2):
    theta = np.asarray(theta, dtype=float)
    r = np.asarray(r, dtype=float)
    t_target = np.atleast_1d(np.asarray(t_target, dtype=float))
    segments = _split_curve(theta, r)
    result = np.full_like(t_target, np.nan)
    for seg_t, seg_r in segments:
        is_wrapped = seg_t.max() > 2 * np.pi + 1e-6
        if is_wrapped:
            t_mapped = t_target + np.pi
            mask = (t_mapped >= seg_t[0] - tol) & (t_mapped <= seg_t[-1] + tol)
            if np.any(mask):
                free = mask & np.isnan(result)
                if np.any(free):
                    result[free] = np.interp(t_mapped[free], seg_t, seg_r)
        else:
            mask = (t_target >= seg_t[0] - tol) & (t_target <= seg_t[-1] + tol)
            if np.any(mask):
                free = mask & np.isnan(result)
                if np.any(free):
                    result[free] = np.interp(t_target[free], seg_t, seg_r)
    return result


def _make_serialisable(regions):
    out = []
    for r in regions:
        out.append(
            {k: v for k, v in r.items() if k not in ("r_inner_expr", "r_outer_expr")}
        )
    return out


def _make_domain(domain):
    from sympy import Interval as SympyInterval

    if domain is None:
        return DOMAIN
    start = float(domain["start"])
    end = float(domain["end"])
    if start >= end:
        end = start + 0.1
    return SympyInterval(start, end)


def build_graph_data(latex_strings, domain=None):
    domain = _make_domain(domain)
    latex_strings = [s or "" for s in latex_strings]
    active = [s for s in latex_strings if s.strip()]
    if not active:
        return None

    exprs, errors = parse_polar(latex_strings)
    active_exprs = [e for e in exprs if e is not None]

    curves_data = []
    regions_data = []
    solutions_data = []
    warnings = []

    if len(active_exprs) >= 1:
        info = polar_get_info(active_exprs, domain)
        curves_data = []
        for c in info["curves"]:
            theta = c["theta"]
            r = c["r"]
            theta = np.atleast_1d(np.asarray(theta, dtype=float))
            r = np.atleast_1d(np.asarray(r, dtype=float))
            if len(r) == 1 and len(theta) > 1:
                r = np.full_like(theta, r[0])
            if len(theta) == 1 and len(r) > 1:
                theta = np.full_like(r, theta[0])
            curves_data.append(
                {
                    "label": c["label"],
                    "theta": theta.tolist(),
                    "r": r.tolist(),
                }
            )
        solutions_data = [
            s for s in info["solutions"] if s.get("solution") == "standard"
        ]
        # convert sympy floats to plain floats
        for s in solutions_data:
            s["theta"] = float(s["theta"])
            s["r"] = float(s["r"])
            for k in ("old_theta", "old_r"):
                if k in s and s[k] is not None:
                    s[k] = float(s[k])

    if len(active_exprs) == 2:
        info = polar_get_info(active_exprs, domain)
        regions = solve_region_areas(
            active_exprs, domain, info["curves"], info["solutions"]
        )
        regions_data = _make_serialisable(regions)
        for i, expr in enumerate(active_exprs):
            _, retraces = get_unique_domain(expr, domain)
            if retraces:
                warnings.append(
                    f"f{i + 1} retraces itself over [{domain.start:.3f}, {domain.end:.3f}] — consider half-domain"
                )

    return {
        "curves": curves_data,
        "solutions": solutions_data,
        "regions": regions_data,
        "errors": errors,
        "warnings": warnings,
    }


def _build_base_figure(graph_data):
    fig = _empty_figure()
    if not graph_data:
        return fig

    for i, curve in enumerate(graph_data["curves"]):
        color = CURVE_COLORS[i % len(CURVE_COLORS)]
        fig.add_trace(
            go.Scatterpolar(
                r=curve["r"],
                theta=np.degrees(curve["theta"]).tolist(),
                mode="lines",
                line=dict(color=color, width=2),
                name=curve["label"],
            )
        )

    for sol in graph_data.get("solutions", []):
        fig.add_trace(
            go.Scatterpolar(
                r=[float(sol["r"])],
                theta=[float(np.degrees(sol["theta"]))],
                mode="markers",
                marker=dict(color="black", size=7, symbol="circle"),
                name="intersection",
                showlegend=False,
            )
        )

    max_r = 1.0
    for curve in graph_data.get("curves", []):
        if curve.get("r"):
            max_r = max(max_r, max(curve["r"]))
    grid_max = max_r * 1.5
    n_theta = 72
    n_r = 30
    thetas_deg = np.linspace(0, 360, n_theta)
    rs = np.linspace(0, grid_max, n_r)
    T, R = np.meshgrid(thetas_deg, rs)
    fig.add_trace(
        go.Scatterpolar(
            r=R.flatten(),
            theta=T.flatten(),
            mode="markers",
            marker=dict(size=0.1, color="rgba(0,0,0,0)", opacity=0),
            showlegend=False,
            hoverinfo="skip",
            name="click-grid",
        )
    )

    return fig


def _validate_region(region, curve_data_list):
    """Check region θ-bounds are covered by at least one segment of each curve."""
    t1, t2 = region["theta1"], region["theta2"]
    tol = 1e-2
    for idx in [region["inner_idx"], region["outer_idx"]]:
        if idx == -1:
            continue
        c = curve_data_list[idx]
        segments = _split_curve(np.array(c["theta"]), np.array(c["r"]))
        covered = False
        for seg_t, _ in segments:
            is_wrapped = seg_t.max() > 2 * np.pi + 1e-6
            if is_wrapped:
                if t1 + np.pi >= seg_t[0] - tol and t2 + np.pi <= seg_t[-1] + tol:
                    covered = True
                    break
            else:
                if t1 >= seg_t[0] - tol and t2 <= seg_t[-1] + tol:
                    covered = True
                    break
        if not covered:
            return False
    return True


def _region_polygon(region, curves):
    t1, t2 = region["theta1"], region["theta2"]
    n = 80
    tgrid = np.linspace(t1, t2, n)

    outer_idx = region["outer_idx"]
    inner_idx = region["inner_idx"]

    outer_curve = curves[outer_idx]
    outer_r = _sample_curve(outer_curve["theta"], outer_curve["r"], tgrid)
    if np.any(np.isnan(outer_r)):
        return [], []

    if inner_idx == -1:
        inner_r = np.zeros(n)
    else:
        inner_curve = curves[inner_idx]
        inner_r = _sample_curve(inner_curve["theta"], inner_curve["r"], tgrid)
        if np.any(np.isnan(inner_r)):
            return [], []

    if np.any(inner_r > outer_r + 1e-4):
        return [], []

    theta_poly = np.concatenate([tgrid, tgrid[::-1]])
    r_poly = np.concatenate([outer_r, inner_r[::-1]])
    return np.degrees(theta_poly).tolist(), r_poly.tolist()


@app.callback(
    Output("graph-data", "data"),
    Output("region-dropdown", "options"),
    Output("warnings-box", "children"),
    Input("debounced-inputs", "data"),
    Input("domain-store", "data"),
    prevent_initial_call=True,
)
def update_graph_data(latex_list, domain):
    data = build_graph_data(latex_list, domain)
    if data is None:
        return None, [], []

    valid_regions = []
    for reg in data["regions"]:
        if reg["area"] <= 1e-6:
            continue
        if not _validate_region(reg, data["curves"]):
            continue
        valid_regions.append(reg)

    data["regions"] = valid_regions

    options = []
    for reg in valid_regions:
        label = f"{reg['label']}  θ=[{reg['theta1']:.3f}, {reg['theta2']:.3f}]  A={reg['area']:.4f}"
        options.append({"label": label, "value": reg["id"]})

    warning_els = [html.Div(w) for w in data.get("warnings", [])]
    return data, options, warning_els


@app.callback(
    Output("polar-graph", "figure"),
    Input("graph-data", "data"),
    Input("fills-store", "data"),
)
def render_figure(graph_data, fills):
    fig = _build_base_figure(graph_data)
    if not graph_data:
        return fig

    max_r = 1.0
    for curve in graph_data.get("curves", []):
        if curve.get("r"):
            max_r = max(max_r, max(curve["r"]))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, max_r * 1.3])))

    if not fills:
        return fig

    for fill_id, fill in fills.items():
        fig.add_trace(
            go.Scatterpolar(
                r=fill["r"],
                theta=fill["theta_deg"],
                fill="toself",
                fillcolor=fill["color"],
                line=dict(color="rgba(0,0,0,0)", width=0),
                mode="lines",
                name=fill["label"],
                showlegend=True,
                hoverinfo="name",
            )
        )
    return fig


@app.callback(
    Output("fills-store", "data", allow_duplicate=True),
    Input("polar-graph", "clickData"),
    State("graph-data", "data"),
    State("fills-store", "data"),
    prevent_initial_call=True,
)
def handle_click(click_data, graph_data, fills):
    if not click_data or not graph_data:
        return no_update

    point = click_data["points"][0]
    theta_deg = point.get("theta", 0)
    r_val = point.get("r", 0)
    theta_rad = float(np.radians(theta_deg))
    r_val = float(r_val)

    regions = graph_data.get("regions", [])
    curves = graph_data.get("curves", [])
    if not regions or not curves:
        return no_update

    if r_val < 0.02:
        return no_update

    clicked = None
    for reg in regions:
        if reg["area"] <= 1e-6:
            continue
        if not (reg["theta1"] <= theta_rad <= reg["theta2"]):
            continue
        outer_c = curves[reg["outer_idx"]]
        outer_r = float(_sample_curve(outer_c["theta"], outer_c["r"], theta_rad)[0])
        inner_r = (
            0.0
            if reg["inner_idx"] == -1
            else float(
                _sample_curve(
                    curves[reg["inner_idx"]]["theta"],
                    curves[reg["inner_idx"]]["r"],
                    theta_rad,
                )[0]
            )
        )
        tol = 0.02
        if inner_r - tol <= r_val <= outer_r + tol:
            clicked = reg
            break

    if clicked is None:
        return no_update

    rid = str(clicked["id"])
    fills = dict(fills or {})

    if rid in fills:
        del fills[rid]
        return fills

    theta_deg, r_poly = _region_polygon(clicked, curves)
    if not theta_deg:
        return no_update
    color = FILL_COLORS[clicked["outer_idx"] % len(FILL_COLORS)]
    label = f"{clicked['label']} A={clicked['area']:.4f}"

    fills[rid] = {"theta_deg": theta_deg, "r": r_poly, "color": color, "label": label}
    return fills


@app.callback(
    Output("fills-store", "data", allow_duplicate=True),
    Input("clear-btn", "n_clicks"),
    Input("debounced-inputs", "data"),
    Input("domain-store", "data"),
    State("fills-store", "data"),
    prevent_initial_call=True,
)
def manage_fills(clear_clicks, debounced_inputs, domain, fills):
    triggered = ctx.triggered_id
    fills = fills or {}

    if triggered == "debounced-inputs":
        return {}

    if triggered == "domain-store":
        return {}

    if triggered == "clear-btn":
        return {}

    return no_update


@app.callback(
    Output("fills-store", "data", allow_duplicate=True),
    Input("region-dropdown", "value"),
    State("graph-data", "data"),
    State("fills-store", "data"),
    prevent_initial_call=True,
)
def dropdown_fill(region_id, graph_data, fills):
    if region_id is None or not graph_data:
        return no_update

    fills = dict(fills or {})
    rid = str(region_id)

    if rid in fills:
        # Toggle off
        del fills[rid]
        return fills

    regions = graph_data.get("regions", [])
    region = next((r for r in regions if r["id"] == region_id), None)
    if region is None:
        return no_update

    curves = graph_data["curves"]
    np_curves = [{"theta": np.array(c["theta"]), "r": np.array(c["r"])} for c in curves]
    theta_deg, r_poly = _region_polygon(region, np_curves)
    if not theta_deg:
        return no_update
    color_idx = region["outer_idx"] % len(FILL_COLORS)
    label = f"{region['label']} A={region['area']:.4f}"

    fills[rid] = {
        "theta_deg": theta_deg,
        "r": r_poly,
        "color": FILL_COLORS[color_idx],
        "label": label,
    }
    return fills


if __name__ == "__main__":
    app.run(debug=True, port=8050)

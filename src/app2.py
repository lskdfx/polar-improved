from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
from dash_mathlive import dash_mathlive

GRAPH_BG="#eff1f5"
GRAPH_PLOT_BG="#e6e9ef"
GRAPH_TEXT_FG="#4c4f69"
GRAPH_AXIS_FG="#8c8fa1"

def blank_polar():
    fig = go.Figure();
    fig.update_layout(
        autosize=True,
#        paper_bgcolor=GRAPH_BG,
#        plot_bgcolor=GRAPH_PLOT_BG,
#        font={ "color": GRAPH_TEXT_FG },
#        polar={
#            "bgcolor": GRAPH_BG,
#            "radialaxis": {
#                "visible": True,
#                "color": GRAPH_TEXT_FG,
#                "gridcolor": GRAPH_AXIS_FG,
#                "linecolor": GRAPH_AXIS_FG,
#            },
#            "angularaxis": {
#                "color": GRAPH_TEXT_FG,
#                "gridcolor": GRAPH_AXIS_FG,
#                "linecolor": GRAPH_AXIS_FG,
#            }
#        }
    );
    return fig;

def mathlive_input(input_id, value=""):
    return dash_mathlive(id=f"math-field-{input_id}", value=value, debounce=1000);

app = Dash()
app.layout = [
    html.Div(children=[
        html.Div(children="Polar Grapher")
    ], className="header"),
    html.Div(children=[
        html.Div(children=dcc.Graph(id="graph", figure=blank_polar(), responsive=True), className="graph"),
        html.Div(children=[
            html.Div(children="Equations"),
            mathlive_input(1, value=r"\sin(\theta)"),
            mathlive_input(2, value=r"0"),
            html.Div(children="Domain"),
            mathlive_input(3, value="0"),
            mathlive_input(4, value="2\pi")
        ], className="eqninput")
    ], className="body")
];

@callback(
    Output("graph", "figure"),
    Input("math-field-1", "value"),
    Input("math-field-2", "value"),
    Input("math-field-3", "value"),
    Input("math-field-4", "value"),
)
def update(eqn1, eqn2, domain_start, domain_end):
    fig = blank_polar();
    fig.add_trace(go.Scatterpolar(r=[], theta=[], showlegend=False))

    try:
        from eqninput import parse_polar
        from sympy.parsing.latex import parse_latex
        from solver import polar_get_info
        from regions import solve_region_areas, sample_region_polygon
        from sympy import Interval, Symbol, pi
        import numpy as np

        expr = parse_polar(eqn1, eqn2);
        print(expr);
        pi_subs = {Symbol("pi"): pi}
        start_sym = parse_latex(domain_start or "0", strict=False, backend="antlr").subs(pi_subs)
        end_sym = parse_latex(domain_end or r"2\pi", strict=False, backend="antlr").subs(pi_subs)
        domain = Interval(start_sym, end_sym)
        print(f"[domain] {domain}")

        info = polar_get_info(expr, domain);

        fig.add_trace(go.Scatterpolar(r=info["expr1"][1], theta=np.degrees(info["expr1"][0]), mode="lines", name=str(expr[0])));
        fig.add_trace(go.Scatterpolar(r=info["expr2"][1], theta=np.degrees(info["expr2"][0]), mode="lines", name=str(expr[1])));

        for solution in info["solutions"]:
            if solution["solution"] == "standard":
                fig.add_trace(go.Scatterpolar(
                    r=[solution["r"]],
                    theta=[np.degrees(solution["theta"])],
                    mode="markers",
                    showlegend=False
                ))
            elif solution["solution"] == "origin":
                fig.add_trace(go.Scatterpolar(
                    r=[0],
                    theta=[0],
                    mode="markers",
                    showlegend=False
                ))

        curves = [
            {"label": "f1", "theta": info["expr1"][0], "r": info["expr1"][1]},
            {"label": "f2", "theta": info["expr2"][0], "r": info["expr2"][1]},
        ]
        regions = solve_region_areas(expr, domain, curves, info["solutions"])

        for region in regions:
            if region["area"] < 1e-6:
                continue
            theta_deg, r_poly = sample_region_polygon(region)
            if not theta_deg:
                continue
            fig.add_trace(go.Scatterpolar(
                r=r_poly,
                theta=theta_deg,
                fill="toself",
                line={"width": 0},
                name=f"{region['label']}  A={region['area']:.4f}",
            ))

    except Exception as err:
        import traceback
        print(f"failed!");
        print(err);
        traceback.print_exc();
        pass

    return fig;

app.run(debug=True);

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
    return dash_mathlive(id=f"math-field-{input_id}", value=value);

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
            mathlive_input(2, value=r"2\cos(3\theta)"),
        ], className="eqninput")
    ], className="body")
];

@callback(Output("graph", "figure"), Input("math-field-1", "value"), Input("math-field-2", "value"))
def update(eqn1, eqn2):
    fig = blank_polar();
    fig.add_trace(go.Scatterpolar(r=[], theta=[], showlegend=False))

    try:
        from eqninput import parse_polar 
        from solver import polar_get_info
        from regions import polar_find_regions
        from sympy import Interval, pi
        import numpy as np

        expr = parse_polar(eqn1, eqn2);
        print(expr);
        domain = Interval(0, pi)

        info = polar_get_info(expr, domain);
        regions = polar_find_regions(info, domain);

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

        for region in regions:
            theta_top = np.degrees(region["top"][0])
            r_top = region["top"][1]
            theta_bottom = np.degrees(region["bottom"][0])
            r_bottom = region["bottom"][1]

            # common theta space to keep polygon winding good ?
            theta_common = np.union1d(theta_top, theta_bottom)
            r_top_interp = np.interp(theta_common, theta_top, r_top)
            r_bottom_interp = np.interp(theta_common, theta_bottom, r_bottom)
            r_zero = np.zeros_like(r_bottom_interp)

            # top to bottom
            fig.add_trace(go.Scatterpolar(
                r=np.concatenate([r_top_interp, r_bottom_interp[::-1]]).tolist(),
                theta=np.concatenate([theta_common, theta_common[::-1]]).tolist(),
                fill="toself",
                line={"width": 0}
            ))

            # bottom to 0
            fig.add_trace(go.Scatterpolar(
                r=np.concatenate([r_bottom_interp, r_zero]).tolist(),
                theta=np.concatenate([theta_common, theta_common[::-1]]).tolist(),
                fill="toself",
                line={"width": 0}
            ))

    except Exception as err:
        import traceback
        print(f"failed!");
        print(err);
        traceback.print_exc();
        pass

    return fig;

app.run(debug=True);

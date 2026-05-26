import dash_mathlive
from dash import Dash, callback, html, Input, Output

app = Dash(__name__)

app.layout = html.Div([
    dash_mathlive.dash_mathlive(
        id='input',
        value='my-value',
    ),
    html.Div(id='output')
])


@callback(Output('output', 'children'), Input('input', 'value'))
def display_output(value):
    return 'You have entered {}'.format(value)


if __name__ == '__main__':
    app.run(debug=True)

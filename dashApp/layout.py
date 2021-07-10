import dash_core_components as dcc
import dash_html_components as html

layout_main = html.Div(
    html.Div([
        html.H4('Live Chart'),
        html.Div(id='live-update-text'),
        html.Div(id='click-update-text'),
        dcc.Graph(id='live-update-graph'),
        html.Button('Record', id='btn-record', n_clicks=0),
        html.Div(id='container-button-timestamp'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ], style={'text-align':'center'})
)
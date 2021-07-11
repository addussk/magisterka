import dash_core_components as dcc
import dash_html_components as html
from dashApp.templates import *

layout_main = html.Div(
    id="big-app-conteiner",
    children=[
        build_banner(),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=50, # start at batch 50
            disabled = True,
        ),
        html.Div(
            id="app-container",
            children=[
                build_tabs(),
                # Main app
                html.Div(id="app-content"),
            ],
        ),
        dcc.Store(id="n-interval-stage", data=50),
        # html.H4('Live Chart'),
        # html.Div(id='live-update-text'),
        # html.Div(id='click-update-text'),
        # dcc.Graph(id='live-update-graph'),
        # html.Button('Record', id='btn-record', n_clicks=0),
        # html.Div(id='container-button-timestamp'),
        
    ], style={'text-align':'center'}
)



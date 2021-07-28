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
            #n_intervals=50, # start at batch 50
            #disabled = True,
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
    ], style={'text-align':'center'}
)



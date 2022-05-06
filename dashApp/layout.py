from dash import dcc, html
from dashApp.templates import *
from dash_extensions import Keyboard
import dash_daq as daq

layout_main = html.Div(
    id="big-app-container",
    children=[
        html.Div(
            id='input-panel',
            children=[
                build_banner(),
                build_mode_btns(),
                build_set_panel(),
                build_chart_panel(),
            ]
        ),

        html.Div(
            id='output-panel',
            className="row",
            children=[
                html.H1("Status: OFF", ),
                html.Div(
                    id="indicators_container",
                    children=[
                        html.Div(
                            className="row",
                            children=generate_output_indicators(),
                        )
                        
                    ],
                ),
                html.Div(
                    id="temperature_panel",
                    className="row",
                    children=[
                        html.H1("Temperature:", className='row'),
                        generate_temp_indicator(),  
                    ],
                ),
            ],
        ),

        
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
        html.Div(
            id="dialogBox",
            className="modal",
            children=[
                html.Div(
                    id="dialog_container",
                    className="modal-content",
                    children=[                        
                        html.Button("X", id="exit_btn", className="close"),
                        html.H1("Are you confirm?"),
                        html.Button("Confirm", id="confirm_btn", className="confirm"),
                    ],
                )
            ],
        ),
        html.Div(
            id="dialogBox_tab2",
            className="modal",
            children=[
                html.Div(
                    id="dialog_container_tab2",
                    className="modal-content",
                    children=[                        
                        html.Button("X", id="exit_btn_tab2", className="close"),
                        html.H1("Are you confirm?"),
                        html.Button("Confirm", id="confirm_btn_tab2", className="confirm"),
                    ],
                )
            ],
        ),
        html.Div([Keyboard(id="keyboard"), html.Div(id="output")]),
        html.Div(id="hide_part", children=[daq.BooleanSwitch(id='isDiagWindShow', on=False)],  style={'display':'none'}),
        html.Div(id="hide_part_tab2", children=[daq.BooleanSwitch(id='isDiagWindShow_tab2', on=False)],  style={'display':'none'}),
        dcc.Store(id="value-setter-store", data=init_value_setter_store()),
        dcc.Store(id="n-interval-stage", data=50),
    ],
)



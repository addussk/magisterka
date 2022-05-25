from dash import dcc, html
from dashApp.templates import *
from dash_extensions import Keyboard
import dash_daq as daq

DICT_DEFAULT_CFG = {
    "cur_track_meas_setting": {
            "turn_on": False,
            "start_freq":90,
            "stop_freq":110,
            "power":36,
            "freq_step":1,
            "time_step":10,
        }
    }

layout_main = html.Div(
    id="big-app-container",
    children=[
        # Po refactoringu:
        # Przetrzymuje dane od pierwszego zaladowania strony do czasu wyczysczenia
        dcc.Store(id='start-btn-color', storage_type='local', data=fill_style()),
        dcc.Store(id='mode-btn-hg', storage_type='local', data=""),
        dcc.Store(id='freq-input-val', storage_type='local', data=0),
        dcc.Store(id='power-input-val', storage_type='local', data=0),
        dcc.Store(id="n-interval-stage", data=50),
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
                html.H1("Status: OFF", id="status-header"),
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

        html.Div(
            id="dialog-form-p-tracking",
            className="dialog_container",
            children=track_meas_tab(DICT_DEFAULT_CFG),
            style={
                'display':'none',
            }
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
    ],
)



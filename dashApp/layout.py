from dash import dcc, html
from dashApp.templates import *
from dash_extensions import Keyboard
import dash_daq as daq

DICT_DEFAULT_CFG = {
    "cur_fix_meas_setting": {
            "turn_on": False,
            "start_freq": 5000000,
            "power":10,
            "time_step":1,
    },
    "cur_track_meas_setting": {
            "turn_on": False,
            "start_freq":90,
            "stop_freq":110,
            "power_min":1,
            "power_max":13,
            "time_step":1,
    },
    "cur_sweep_meas_setting": {
            "turn_on": False,
            "start_freq":90,
            "stop_freq":110,
            "power_min":1,
            "power_max":13,
            "time_step":1,
        },
    }

layout_main = html.Div(
    id="big-app-container",
    children=[
        # Po refactoringu:
        # Przetrzymuje dane od pierwszego zaladowania strony do czasu wyczysczenia
        dcc.Store(id='btns-color', storage_type='local', data=fill_style()),
        dcc.Store(id='mode-btn-hg', storage_type='local', data=""),
        dcc.Store(id='freq-input-val', storage_type='local', data=0),
        dcc.Store(id='power-input-val', storage_type='local', data=0),
        dcc.Store(id="n-interval-stage", data=50),
        dcc.Store(id="cfg-mode-store", data=init_config_storage()),

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
            style={"display":"block"},
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
            id="graph-cfg-panel",
            className="row",
            style={"display":"none"},
            children=[
                html.H1("Graph config"),
                html.Div(
                    id="graph-cfg-container",
                    children=generate_graph_cfg_controls(),
                ),
            ]
        ),

        html.Div(
            id="dialog-form-fix",
            className="dialog_container",
            children=fix_meas_tab(DICT_DEFAULT_CFG),
            style={
                'display':'none',
            }
        ),

        html.Div(
            id="dialog-form-t-tracking",
            className="dialog_container",
            children=t_tracking_tab(),
            style={
                'display':'none',
            }
        ),

        html.Div(
            id="dialog-form-p-tracking",
            className="dialog_container",
            children=track_meas_tab(DICT_DEFAULT_CFG),
            style={
                'display':'none',
            }
        ),

        html.Div(
            id="dialog-form-pf-tracking",
            className="dialog_container",
            children=pf_meas_tab(DICT_DEFAULT_CFG),
            style={
                'display':'none',
            }
        ),

        html.Div(
            id="hidden-div",
            style={'display':'none'}
        ),

        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            #n_intervals=50, # start at batch 50
            #disabled = True,
        ),
    ],       
)



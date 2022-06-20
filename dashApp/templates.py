from dash import html, dcc
import dash_daq as daq
import plotly.graph_objs as go
from dashApp.extensions import db
from statemachine import DataBase
from dashApp.models import  MeasurementInfo

Global_DataBase = DataBase(db)

# Dict dla drop list do wybierania trybow pomiaru(tab meas setts)
DROP_LIST_MEAS_MODE = {
    'Fixed Frequency': 0,
    'Tracking': 1,
    'Sweeping': 2,
}
# Dict dla drop list do wybierania typow kalibracji(tab meas setts)
DROP_LIST_CALIB = {
    'Attenuator': 0,
}

suffix_row = "_row"
suffix_button_id = "_buttonss"
suffix_sparkline_graph = "_sparkline_graph"
suffix_date = "_date"

# struktura konfigurujaca obiekt DarkThemeProvider(uzyty w  quick panel) 
theme = {
    'dark': True,
    'detail': '#fa0606',
    'primary': '#00EA64',
    'secondary': '#fa0606',
}

# id : label content
OUTPUT_INDICATORS = {
    'O_PWR':"Output PWR:,[W]",
    'Refl_PWR': "Reflected PWR:,[W]",
    'SWR': "SWR:,[W]",
    'Freq': "Frequency:,[GHz]",
    'PA_V': "PA Voltage:,[V]",
    'PA_C': "PA Current:,[A]",
    'PA_T': "PA Temperature:,[C]",
}

def generate_output_indicators():
    retArr = []
    for el_id, el_cont in OUTPUT_INDICATORS.items():
        string_val, unit= el_cont.split(',')
        one_row = html.Div(
            id=el_id,
            children=[
                # Napis reprezentujacy nazwe dla kazdego wskaznika
                html.Label(string_val, className="left"),
                # Napis reprezentujacy jednostke dla kazdego wskaznika
                html.Label(unit, className="right"),
                # Napis reprezentujacy wartosc odczytana przez sensor
                html.Label("0", id=el_id+"value", className="right space-2px"),
            ])
        retArr.append(one_row)
    return retArr

def generate_temp_indicator():
    return  html.Div(
                id="thermometer-card",
                children=[
                    daq.Thermometer(
                        id="thermometer-indicator",
                        min=0,
                        max=105,
                        value=50, # should be update in runtime
                        showCurrentValue=True,
                        units="C",
                        color="#f71606",
                        style={ }
                    )
                ]
            )  
    
def init_config_storage():
    # Initialize store data - will be implemented
    ret = {
        "cur_fix_meas_setting": {
            "turn_on": False,
            "start_freq": 1,
            "power":36,
            "time_step":10,
        },
        "cur_track_meas_setting": {
            "turn_on": False,
            "start_freq":90,
            "stop_freq":110,
            "power_min":1,
            "power_max":13,
            "time_step":10,
        },
        "cur_sweep_meas_setting": {
            "turn_on": False,
            "start_freq":90,
            "stop_freq":110,
            "power":36,
            "freq_step":1,
            "time_step":10,
        }
    }
    
    return ret

def fill_style():
    retDic = {
        'start-btn-style': {
            'backgroundColor':'#065b0a9d',
        },
        'stop-btn-style': {
            'backgroundColor':'#f10202',
        }
    }
    return retDic

def build_banner():
    return html.Div(
        id="header",
        className="row",
        children=[
            html.Div(
                id="baner-logo",
                className="column",
                children=[
                    html.Img(id="logo", src='/dashboard/assets/logoPW.png' ),
                ]
            ),
            html.Div(
                id="baner-text",
                className="column",
                children=[
                    html.H2("REAKTOR CHEMICZNY"),
                ]
            ),
        ],
    )
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Praca Magisterska"),
                    html.H6("Adrian Kruczak"),
                ],
            ),
            html.Div(
                id="banner-logo",
                children=[
                    html.A(
                        html.Button(
                            id="btn_repo", children="LINK TO SOURCE CODE", n_clicks=0,
                        ),
                        href="https://github.com/addussk/magisterka",
                    ),
                    html.A(
                        html.Img(id="logo", src='/dashboard/assets/logoPW.png' ),
                    ),
                ],
            ),
        ],
    )

def build_mode_btns():
    return html.Div(
        id="header-modes",
        className="row",
        children=[
            html.Div(
                className="column",
                children=[
                    html.H2("Mode:")
                ],
            ),
            html.Div(
                className="column mode-btn",
                children=[
                    html.Button("Manual", id="manual-mode-btn", className="button"),
                ],
            ),
            html.Div(
                className="column mode-btn",
                children=[
                    html.Button("P-Tracking", id="p-track-mode-btn", className="button"),
                ],
            ),
            html.Div(
                className="column mode-btn",
                children=[
                    html.Button("PF-Tracking", id="pf-track-mode-btn", className="button"),
                ],
            ),
        ]
    )

def build_set_panel():
    return html.Div(
        id="setting-panel",
        className="row",
        children=[
            html.Div(
                className='left column-set lab_btns',
                children=[
                    html.Div(
                        children=[
                            html.P("Frequency: "),
                        ],
                        style={'height':'50%'},
                    ),

                    html.Div(
                        children=[
                            html.Div(
                                className='column',
                                children=[
                                    html.Button("+", id="freq-inc-btn", className="button padding-zero"),
                                ], style={'width':'50%'}
                            ),
                            html.Div(
                                className='column',
                                children=[
                                    html.Button("-", id="freq-dec-btn", className="button padding-zero"),
                                ], style={'width':'50%'}
                            ),
                        ],
                        style={'height':'50%', 'marginLeft': '2%'}
                    ),
                ],
            ),

            html.Div(
                className="column input_div",
                children=[
                    dcc.Input(id="freq_input", className="numeric_input", type="number", placeholder="MHz", debounce=True, min=0)
                ],
            ),

            html.Div(
                className='left column-set lab_btns',
                children=[ 
                    html.Div(
                        children=[
                            html.P("Power Level: "),
                        ],
                        style={'height':'50%'},
                    ),

                    html.Div(
                        children=[
                            html.Div(
                                className='column',
                                children=[
                                    html.Button("+", id="power-inc-btn", className="button padding-zero"),
                                ], style={'width':'50%'}
                            ),
                            html.Div(
                                className='column',
                                children=[
                                    html.Button("-", id="power-dec-btn", className="button padding-zero"),
                                ], style={'width':'50%'}
                            ),
                        ],
                        style={'height':'50%', 'marginLeft': '2%'}
                    ),
                ], 
            ),

            html.Div(
                className="input_div column",
                children=[
                    dcc.Input(id="power_input", className="numeric_input", type="number", placeholder="dBm", debounce=True, min=0, max=15)
                ],
            ),
        ]
    )

def build_chart_panel():
    return html.Div(
        id="chart-panel",
        children=[
            html.Div(
                id='chart-container',
                children=[
                    dcc.Graph(
                        id="control-chart-live",
                        figure=go.Figure(
                            {
                                "data": [
                                    {
                                        "x": [1,2,3,4,5],
                                        "y": [1,2,3,4,5],
                                        "mode": "lines+markers",
                                    }
                                ],
                                "layout": {
                                    "paper_bgcolor": "rgba(0,0,0,0)",
                                    "plot_bgcolor": "rgba(0,0,0,0)",
                                    "xaxis": dict(
                                        showline=False, showgrid=False, zeroline=False
                                    ),
                                    "yaxis": dict(
                                        showgrid=False, showline=False, zeroline=False
                                    ),
                                    "autosize": True,
                                },
                            }
                        ),
                    ),
                ],
            ),
            html.Div(
                id="stop-btn-container",
                className="column",
                children=[
                    html.Button("Start!", id="start-btn", className="button"),
                    html.Br(),
                    html.Button("Stop!", id="stop-btn", className="button",),
                ]
            ),
        ],
    )

def build_value_setter_line(line_num, label, col3, class_name=""):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className='first_diag_col left'),
            html.Div(col3, className='sec_diag_col left'),
        ],
        className="row-diag-window {}".format(class_name),
        style={'color':'#c8f10f'}
    )
 
def track_meas_tab(state_value):
    return [
        html.Div(
            id='value-setter-panel-track-header',
            children=[
                html.Label('Parameter', className='left header-first-col'),
                html.Label('Value', className='left header-sec-col'),
            ],
            className="header-form",
            style={'color':'#c8f10f'}
        ),
        
        build_value_setter_line(
            "value-setter-panel-track-start-freq",
            "Start Freq:",
            dcc.Input(
                id="start-freq-input", value=state_value["cur_track_meas_setting"]["start_freq"],  className="setting-input", max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-track-stop-freq",
            "Stop Freq:",
            dcc.Input(
                id="stop-freq-input", value=state_value["cur_track_meas_setting"]["stop_freq"], className="setting-input", max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-track-power",
            "Power Min:",
            dcc.Input(
                id="power-track-input", value=state_value["cur_track_meas_setting"]["power_min"], className="setting-input", max=13
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-freq-step",
            "Power Max:",
            dcc.Input(
                id="freq-step-input", value=state_value["cur_track_meas_setting"]["power_max"], className="setting-input", max=13
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-track-time-step",
            "Time step:",
            dcc.Input(
                id="time-step-track-input", value=state_value["cur_track_meas_setting"]["time_step"], className="setting-input", max=9999999
            ),
        ),

        html.Div(
            className="button-container",
            children=[
                html.Button("Accept", id="accept-btn-p", className="button form-button"),
            ],
        )
    ]

def fix_meas_tab(state_value):
    return [
        html.Div(
            id='value-setter-panel-fix-header',
            children=[
                html.Label('Parameter', className='left header-first-col'),
                html.Label('Value', className='left header-sec-col'),
            ],
            className="header-form",
            style={'color':'#c8f10f'}
        ),
        
        build_value_setter_line(
            "value-setter-panel-fix-freq",
            "Frequency:",
            dcc.Input(
                id="fixed-freq-input", value=state_value["cur_fix_meas_setting"]["start_freq"], className="setting-input"
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-fix-power",
            "Power:",
            dcc.Input(
                id="power-fix-input", value=state_value["cur_fix_meas_setting"]["power"], className="setting-input", max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-fix-time-step",
            "Time step:",
            dcc.Input(
                id="time-step-fix-input", value=state_value["cur_fix_meas_setting"]["time_step"], className="setting-input", max=9999999
            ),
        ),
        html.Div(
            className="button-container",
            children=[
                html.Button("Accept", id="accept-btn-fix", className="button form-button"),
            ],
        )
    ]

def pf_meas_tab(state_value):
    return [
        html.Div(
            id='value-setter-panel-pf-header',
            children=[
                html.Label('Parameter', className='left header-first-col'),
                html.Label('Value', className='left header-sec-col'),
            ],
            className="header-form",
            style={'color':'#c8f10f'}
        ),
        
        build_value_setter_line(
            "value-setter-panel-pf-start-freq",
            "Start Freq:",
            dcc.Input(
                id="pf-start-freq-input", value=state_value["cur_sweep_meas_setting"]["start_freq"],  className="setting-input", max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-pf-stop-freq",
            "Stop Freq:",
            dcc.Input(
                id="pf-stop-freq-input", value=state_value["cur_sweep_meas_setting"]["stop_freq"], className="setting-input", max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-pf-pwr-min",
            "Power Min:",
            dcc.Input(
                id="pf-power-min-input", value=state_value["cur_sweep_meas_setting"]["power_min"], className="setting-input", max=13
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-pf-pwr-max",
            "Power Max:",
            dcc.Input(
                id="pf-freq-step-input", value=state_value["cur_sweep_meas_setting"]["power_max"], className="setting-input", max=13
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-pf-time-step",
            "Time step:",
            dcc.Input(
                id="pf-time-step-input", value=state_value["cur_sweep_meas_setting"]["time_step"], className="setting-input", max=9999999
            ),
        ),

        html.Div(
            className="button-container",
            children=[
                html.Button("Accept", id="accept-btn-pf", className="button form-button"),
            ],
        )
    ]
from dash import html, dcc, dash_table
import dash_daq as daq
import plotly.graph_objs as go
from dashApp.extensions import db
from statemachine import DataBase
from dashApp.models import  MeasurementInfo
from drivers import OUTPUT_INDICATORS 
from MeasurementSession import TIME_KEY, FWD_KEY, RFL_KEY, MHZ_KEY, T0_KEY, T1_KEY, T2_KEY, T3_KEY, T4_KEY, TAVG_KEY, TREQ_KEY, TINTERNAL_KEY, VOLTAGE_KEY, CURRENT_KEY

Global_DataBase = DataBase(db)


graph_traces = [
    {
        "key": FWD_KEY,
        "label": "Forward Pwr dBm",
        "defaultState": True,
        "color": "#FF006E"      # ręczne zarządzanie kolorami linii, aby nie zmieniały się przy włączaniu/wyłączaniu krzywych
    },
    {
        "key": RFL_KEY,
        "label": "Reflected Pwr dBm",
        "defaultState": True,
        "color": "#3A86FF"
    },
    {
        "key": MHZ_KEY,
        "label": "Frequency MHz",
        "defaultState": False,
        "color": "#FEFAE0"
    },
    {
        "key": T0_KEY,
        "label": "Tube temp 0",
        "defaultState": False,
        "color": "#BABB74"
    },
    {
        "key": T1_KEY,
        "label": "Tube temp 1",
        "defaultState": False,
        "color": "#D2C06F"
    },
    {
        "key": T2_KEY,
        "label": "Tube temp 2",
        "defaultState": False,
        "color": "#DEC26D"
    },
    {
        "key": T3_KEY,
        "label": "Tube temp 3",
        "defaultState": False,
        "color": "#E9C46A"
    },
    {
        "key": T4_KEY,
        "label": "Tube temp 4",
        "defaultState": False,
        "color": "#EFB366"
    },
    {
        "key": TAVG_KEY,
        "label": "Tube Tavg",
        "defaultState": False,
        "color": "#E76F51"
    },
    {
        "key": TREQ_KEY,
        "label": "Tube req. temp",
        "defaultState": True,
        "color": "#c83f1e"
    },
    {
        "key": TINTERNAL_KEY,
        "label": "PA Temp",
        "defaultState": True,
        "color": "#7AC980"
    },
    {
        "key": VOLTAGE_KEY,
        "label": "PA Volts",
        "defaultState": True,
        "color": "#275C62"
    },
    {
        "key": CURRENT_KEY,
        "label": "PA Amps",
        "defaultState": True,
        "color": "#2A9D8F"
    },
]


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
    retArr.append(html.Div(
        id="uwave",
        children=[
           html.Label("uwave module:", className="left"),
           html.Label("---", id="uwave_status_txt", className="right")
        ]))
    return retArr

def generate_temp_indicator():
    temp_sensor_size = 20
    led_style = {"margin":"-6px"}
    return  html.Div(
                id="thermometer-card",
                style={},
                children=[
                    daq.Thermometer(
                        id="thermometer-indicator",
                        label="Averaged temperature:",
                        min=0,
                        max=105,
                        value=50, # should be update in runtime
                        showCurrentValue=True,
                        units="C",
                        color="#4adc65",
                        height=150,
                        style={"width":"50%"}
                    ),
                    html.Div(
                        style={"width":"50%", "float": "right"},
                        children = [
                            daq.LEDDisplay(
                                id='mlx-sensor-0',
                                value="12.3",
                                size=temp_sensor_size,
                                backgroundColor="#1e2130",
                                color="#4adc65",
                                style=led_style
                            ),
                            daq.LEDDisplay(
                                id='mlx-sensor-1',
                                value="12.3",
                                size=temp_sensor_size,
                                backgroundColor="#1e2130",
                                color="#4adc65",
                                style=led_style
                            ),
                            daq.LEDDisplay(
                                id='mlx-sensor-2',
                                value="12.3",
                                size=temp_sensor_size,
                                backgroundColor="#1e2130",
                                color="#4adc65",
                                style=led_style
                            ),
                            daq.LEDDisplay(
                                id='mlx-sensor-3',
                                value="12.3",
                                size=temp_sensor_size,
                                backgroundColor="#1e2130",
                                color="#4adc65",
                                style=led_style
                            ),
                            daq.LEDDisplay(
                                id='mlx-sensor-4',
                                value="12.3",
                                size=temp_sensor_size,
                                backgroundColor="#1e2130",
                                color="#4adc65",
                                className='dark-theme-control',
                                style=led_style
                            ),
                            
                            
                        ]
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
            "time_step":1,
        },
        "cur_track_meas_setting": {
            "turn_on": False,
            "start_freq":5600,
            "stop_freq":5900,
            "power":36,
            "freq_step":1,
            "time_step":1,
        },
        "cur_sweep_meas_setting": {
            "turn_on": False,
            "start_freq":5600,
            "stop_freq":5900,
            "power":36,
            "freq_step":1,
            "time_step":1,
        },
        "cur_temp_tracking_settings": {
            "turn_on": False,
            "time_step": 1,
        
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
        id="banner",
        children=[
            html.Img(id="logo", src='/dashboard/assets/logo_irtm.png', style={'width':'80px', 'height':'110px', 'float':'left', 'margin-top':'9px', 'margin-right':'9px'} ),
            html.H2("Intelligent RF Power Source"),
        ]
    )
 

# do wykasowania wkrotce
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
                style={"display":"none"}
            ),
            html.Div(
                className="column mode-btn",
                children=[
                    html.Button("Temp-tracking", id="t-track-mode-btn", className="button"),
                ],
            ),
            html.Div(
                className="column mode-btn",
                children=[
                    html.Button("PF-Tracking", id="pf-track-mode-btn", className="button"),
                ],
                style={"display":"none"}
            ),
        ]
    )

def build_mode_panel():
    return html.Div(
        id="header-modes",
        children=[
            html.Button("Mode: (select)", id="mode-select-btn", className="button")
        ]
    )
    
def build_config():
    return html.Div(
        id="header-config",
        children=[
            html.Button("Open mode controls", id="config-open-btn"),
            html.Label("Timer:"),
            daq.LEDDisplay(id="led-timer", value="00:00", backgroundColor="#1e2130", color="#4adc65")
        
        ]
    
    )
    
def dialog_mode_selector():
    return [
        html.H2("Mode selector"),
        dcc.RadioItems([
            {'label': 'Manual mode', 'value': 'manual'},
            {'label': 'Temperature tracking mode', 'value': 't-tracking'},
            {'label': 'Load scanning mode', 'value': 'scanning'}
        ],
        style={'text-align':'left'}),
        
        html.Button("Close", id="dialog-mode-selector-close-btn", className="button", style={"font-size":"2rem"})
    
    
    
    ]

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
                            html.P("Frequency [MHz]: "),
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
                            html.P("Attenuator [dB]: "),
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
                    html.Button("Graph config", id="graph-cfg-btn", className="button"),
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

def tt_table(data=()):
    return dash_table.DataTable(
        id="t-tracking-table", 
        columns=([
            {"id":"tt-seconds", "name":"Time [sec.]", "format":{"locale":{"symbol":["", "s."]}}},
            {"id":"tt-temperature", "name":"Temperature [°C]", "format":{"locale":{"symbol":["", "°C"]}}}
        ]),
        data=data,
        style_header={
            "backgroundColor":'rgb(30, 30, 30)',
            "color":"white"
        },
        style_data={
            "backgroundColor":'rgb(50, 50, 50)',
            "color":"white"            
        },
        editable=True,
        row_deletable=True
    )


def t_tracking_tab():
    return [
        html.Div(
            id='t-tracking-cfg-header',
            children=[
                html.Label('Temperature curve definition', className='left'),
            ],
            className="header-form",
            style={'color':'#c8f10f'}
        ),        

        html.Button('Add row', id='tt-add-row-btn', className="right", n_clicks=0),
        html.Br(),
        html.Div(
            id="tt-table-div", 
            children=[tt_table()]),

        html.Div(
            className="button-container",
            children=[
                html.Button("Accept", id="accept-btn-t", className="button form-button"),
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

def generate_graph_cfg_controls():
    controls = list()
    for gt in graph_traces:
        ctrl = daq.BooleanSwitch(
            id={
                "type": "graph-trace-switch",
                "key": gt["key"],
            },
            color=gt["color"],
            on=gt["defaultState"],
            label={"label":gt["label"], "style":{"width":"50%", "margin-bottom":"10px"} },
            labelPosition="right"
        )
        controls.append(ctrl)
    return controls


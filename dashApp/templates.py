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
                html.Label("0", id=el_id+"value", className="right"),
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
            "frequency": 1,
            "power":36,
            "time_step":10,
        },
        "cur_track_meas_setting": {
            "turn_on": False,
            "start_freq":90,
            "stop_freq":110,
            "power":36,
            "freq_step":1,
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
            html.Div(
                id="baner-btn",
                className="column",
                children=[
                    html.Button("Start!", id="start-btn", className="button"),
                ]
            )
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

def build_value_setter_line(line_num, label, col3):
    row_style = {
        'color':'#c8f10f',
        'fontSize': '1.5rem',
    }

    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className='first_diag_col left'),
            html.Div(col3, className='sec_diag_col left'),
        ],
        className="row-diag-window",
        style=row_style
    )
 
def track_meas_tab(state_value):
    return [
        build_value_setter_line(
            "value-setter-panel-track-header",
            "Parameter",
            "Value",
        ), 
        
        build_value_setter_line(
            "value-setter-panel-track-start-freq",
            "Start Freq:",
            daq.NumericInput(
                id="start_freq_input", value=100,  className="setting-input", size=200, max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-track-stop-freq",
            "Stop Freq:",
            daq.NumericInput(
                id="stop_freq_input", value=state_value["cur_track_meas_setting"]["stop_freq"], className="setting-input", size=200, max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-track-power",
            "Power:",
            daq.NumericInput(
                id="power_track_input", value=state_value["cur_track_meas_setting"]["power"], className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-freq-step",
            "Freq Step:",
            daq.NumericInput(
                id="freq_step_input", value=state_value["cur_track_meas_setting"]["freq_step"], className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-track-time-step",
            "Time step:",
            daq.NumericInput(
                id="time_step_track_input", value=state_value["cur_track_meas_setting"]["time_step"], className="setting-input", size=200, max=9999999
            ),
        ),

        html.Div(
            className="button-container",
            children=[
                html.Button("Accept", id="accept-btn-p-track", className="button"),
            ],
        )
    ]

def fix_meas_tab(state_value):
    return [
        build_value_setter_line(
            "value-setter-panel-fix-header",
            "Parameter",
            "Set new value",
        ), 
        
        build_value_setter_line(
            "value-setter-panel-fix-freq",
            "Frequency:",
            daq.NumericInput(
                id="fixed_freq_input", value=state_value["cur_fix_meas_setting"]["frequency"], className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-fix-power",
            "Power:",
            daq.NumericInput(
                id="power_fix_input", value=state_value["cur_fix_meas_setting"]["power"], className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-fix-time-step",
            "Time step:",
            daq.NumericInput(
                id="time_step_fix_input", value=state_value["cur_fix_meas_setting"]["time_step"], className="setting-input", size=200, max=9999999
            ),
        ),
        html.Div(
            className="button-container",
            children=[
                html.Button("Accept", id="accept-btn-fix", className="button"),
            ],
        )
    ]
    
# Build header
def generate_metric_row(id, style, col1, col2, col3):
    if style is None:
        style = {"height": "8rem", "width": "100%"}

    return html.Div(
        id=id,
        className="row metric-row",
        style=style,
        children=[
            html.Div(
                id=col1["id"],
                className="one column",
                style={"margin-right": "2.5rem", "minWidth": "50px"},
                children=col1["children"],
            ),
            html.Div(
                id=col2["id"],
                style={"textAlign": "center"},
                className="two column",
                children=col2["children"],
            ),
            html.Div(
                id=col3["id"],
                style={"height": "100%"},
                className="four columns",
                children=col3["children"],
            ),
        ],
    )

def generate_metric_list_header():
    return generate_metric_row(
        "metric_header",
        {"height": "3rem", "margin": "1rem 0", "textAlign": "center"},
        {"id": "m_header_1", "children": html.Div("Name")},
        {"id": "m_header_2", "children": html.Div("Date")},
        {"id": "m_header_3", "children": html.Div("Sparkline")},
    )

def generate_metric_row_helper(row_info):
    x_axis = list()
    y_axis = list()
    results_table = Global_DataBase.read_filtered_table(row_info.get_time_scope())

    for record in results_table:
        x_axis.append(record.get_meas_pwr())
        y_axis.append(len(x_axis))

    return generate_metric_row (
        ("row_" + str(row_info.get_id())),
        None,
        # kolumna z nazwa
        {
            "id": ("div_button_" + str(row_info.get_id())),
            "className": "metric-row-button-text",
            "children": html.Button(
                id=(str(row_info.get_id()) + suffix_button_id),
                className="metric-row-button",
                children=row_info.get_name(),
                # title pojawia sie po najechaniu na przycisk
                title="Click to visualize live SPC chart",
                n_clicks=0,
            ),
        },
        # kolumna z data
        {"id": (str(row_info.get_id()) + suffix_date), "children": (row_info.get_time_scope()[0].date())},
        # kolumna z wykresem
        {
            "id": str(row_info.get_id()) + "_sparkline",
            "children": dcc.Graph(
                id=(str(row_info.get_id()) + suffix_sparkline_graph),
                style={"width": "100%", "height": "95%"},
                config={
                    "staticPlot": False,
                    "editable": False,
                    "displayModeBar": False,
                },
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": y_axis,
                                "y": x_axis,
                                "mode": "lines+markers",
                                "name": row_info.get_name(),
                                "line": {"color": "#f4d44d"},
                            }
                        ],
                        "layout": {
                            "uirevision": True,
                            "margin": dict(l=0, r=0, t=4, b=4, pad=0),
                            "xaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "yaxis": dict(
                                showline=False,
                                showgrid=False,
                                zeroline=False,
                                showticklabels=False,
                            ),
                            "paper_bgcolor": "rgba(0,0,0,0)",
                            "plot_bgcolor": "rgba(0,0,0,0)",
                        },
                    }
                ),
            ),
        },)

def build_tabs():
    return html.Div(
        id="tabs",
        className="tabs",
        children=[
            dcc.Tabs(
                id="app-tabs",
                value="tab2",
                className="custom-tabs",
                children=[
                    dcc.Tab(
                        id="Specs-tab",
                        label="Measurements Settings",
                        value="tab1",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                    dcc.Tab(
                        id="Control-chart-tab",
                        label="Live Chart Measurements",
                        value="tab2",
                        className="custom-tab",
                        selected_className="custom-tab--selected",
                    ),
                ],
            )
        ],
    )

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)

def build_value_setter_line(line_num, label, col3):
    row_style = {
        'color':'#c8f10f',
        'fontSize': '1.5rem',
    }

    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className='first_diag_col left'),
            html.Div(col3, className='sec_diag_col left'),
        ],
        className="row-diag-window",
        style=row_style
    )
    
def build_tab_1():
    return [
        # Zawartosc tab 1
        html.Div(
            id="settings-menu",
            children=[
                # Kolumna po lewej 7/12 szer, panel zawierajacy elementy z nastawa urzadzen
                html.Div(
                    id="meas-sett-panel",
                    className="seven columns",
                    children=[
                        # Div zawierajacy drop down list do wyboru trybu pomiaru
                        html.Div(
                            id="metric-select-menu",
                            # className='five columns',
                            children=[
                                html.Label(id="metric-select-title", children="Select Measurement Mode"),
                                html.Br(),
                                dcc.Dropdown(
                                    id="metric-select-dropdown",
                                    options=list(
                                        {"label": mode, "value": DROP_LIST_MEAS_MODE[mode]} for mode in DROP_LIST_MEAS_MODE
                                    ),
                                    value=0,
                                ),
                            ],
                        ),
                        # Div zawierajacy elementy do ustawiania parametrow dla wybranego trybu, tworzone dynamicznie za pomoca callbackow
                        html.Div(
                            id="value-setter-menu",
                            # className='six columns',
                            children=[
                                html.Div(id="value-setter-panel"),
                                html.Br(),
                                html.Div(
                                    id="button-div",
                                    children=[
                                        html.Button("Set new setup", id="value-setter-set-btn"),
                                        html.Button(
                                            "Stop measurement",
                                            id="value-setter-view-btn",
                                        ),
                                    ]
                                ),
                                html.Div(
                                    id="value-setter-view-output", className="output-datatable"
                                ),
                            ]
                        )
                    
                    ]
                ),
            ],
        ),
    ]

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
                    html.Button("Stop!", id="stop-btn", className="button",),
                ]
            ),
        ],
    )

def build_bottom_panel():
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Table with all chapters
            html.Div(
                id="metric-summary-session",
                className="eight columns",
                children=[
                    generate_section_banner("Measurements list: "),
                    html.Div(
                        id="metric-div",
                        children=[
                            generate_metric_list_header(),
                            html.Div(
                                id="metric-rows",
                                children=[
                                    generate_metric_row_helper(el) for el in Global_DataBase.read_record_all(MeasurementInfo)
                                ],
                            ),
                        ],
                    )
                ],
            ),
            # Temperature indicator
            html.Div(
                id="temp-indicator",
                className="four columns",
                children=[
                    generate_section_banner("Current temperature (Celsius)"),
                    generate_indicator(),
                ],
            ),
        ],
    )




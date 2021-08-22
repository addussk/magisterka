from typing import Sized
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from dash_html_components.P import P
import plotly.graph_objs as go


meas_modes = {
    "Fixed Frequency": 0,
    'Tracking': 1,
    'Sweeping': 2,
}

def init_value_setter_store():
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

def build_banner():
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

def build_value_setter_line(line_num, label, value, col3):
    return html.Div(
        id=line_num,
        children=[
            html.Label(label, className="four columns"),
            html.Label(value, className="four columns"),
            html.Div(col3, className="four columns"),
        ],
        className="row",
    )
    
# do zaimplementowania
def build_tab_1():
    return [
        #Manually select metrics
        html.Div(
            id="set-specs-intro-container",
            # className="twelve columns",
            children=html.P(
                "Choose measurement mode and set parameters"
            )
        ),
        html.Div(
            id="settings-menu",
            children=[
                html.Div(
                    id="metric-select-menu",
                    # className='five columns',
                    children=[
                        html.Label(id="metric-select-title", children="Select Measurement Mode"),
                        html.Br(),
                        dcc.Dropdown(
                            id="metric-select-dropdown",
                            options=list(
                                {"label": mode, "value": meas_modes[mode]} for mode in meas_modes
                            ),
                            value=0,
                        ),
                    ],
                ),
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
        )

    ]

def generate_indicator():
    return html.Div(
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
                style={
                }
            )
        ]
    )

def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("User ID"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value="999",
                        color="#c8f10f",
                        backgroundColor="#1e2130",
                        size=50,
                    ),
                ],
            ),
            html.Div(
                id="card-2",
                children=[
                    html.P("Time to the end of the measurement"),
                    daq.Gauge(
                        id="progress-gauge",
                        max=100,
                        min=0,
                        showCurrentValue=True,  # default size 200 pixel
                    ),
                ],
            ),
            html.Div(
                id="utility-card",
                children=[daq.StopButton(id="pwr-on-off-buton",  buttonText='TURN ON', size=160, n_clicks=0)],
            ),
        ],
    )

def build_chart_panel():
    return html.Div(
        id="control-chart-container",
        className="twelve columns",
        children=[
            generate_section_banner("Live Measurement Chart"),
            dcc.Graph(
                id="control-chart-live",
                figure=go.Figure(
                    {
                        "data": [
                            {
                                "x": [],
                                "y": [],
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
    )

def build_bottom_panel():
    return html.Div(
        id="top-section-container",
        className="row",
        children=[
            # Table with all chapters
            html.Div(
                id="all-charts-tab",
                className="eight columns",
                children=[
                    generate_section_banner("All measurement: "),
                    html.Div(
                        id="all-charts-div",
                        children=[
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

def fix_meas_tab(state_value):
    return [
        build_value_setter_line(
            "value-setter-panel-fm-header",
            "Parameter",
            "Last Value",
            "Set new value",
        ), 
        
        build_value_setter_line(
            "value-setter-panel-fm-freq",
            "Frequency [MHz]:",
            state_value["cur_fix_meas_setting"]["frequency"],
            daq.NumericInput(
                id="fixed_freq_input", value=100, className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-fm-power",
            "Power [dBm]:",
            state_value["cur_fix_meas_setting"]["power"],
            daq.NumericInput(
                id="power_fm_input", value=10, className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-fm-time-step",
            "Time for one step [s]:",
            state_value["cur_fix_meas_setting"]["time_step"],
            daq.NumericInput(
                id="time_step_fm_input", value=5, className="setting-input", size=200, max=9999999
            ),
        )
    ]

def track_meas_tab(state_value):
    return [
        build_value_setter_line(
            "value-setter-panel-track-header",
            "Parameter",
            "Last Value",
            "Set new value",
        ), 
        
        build_value_setter_line(
            "value-setter-panel-track-start-freq",
            "Start Frequency [MHz]:",
            state_value["cur_track_meas_setting"]["start_freq"],
            daq.NumericInput(
                id="start_freq_input", value=100, className="setting-input", size=200, max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-track-stop-freq",
            "Stop Frequency [MHz]:",
            state_value["cur_track_meas_setting"]["stop_freq"],
            daq.NumericInput(
                id="stop_freq_input", value=100, className="setting-input", size=200, max=9999999
            ),
        ),

        build_value_setter_line(
            "value-setter-panel-track-power",
            "Power [dBm]:",
            state_value["cur_track_meas_setting"]["power"],
            daq.NumericInput(
                id="power_track_input", value=10, className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-freq-step",
            "Frequency Step[MHz]:",
            state_value["cur_track_meas_setting"]["freq_step"],
            daq.NumericInput(
                id="freq_step_input", value=5, className="setting-input", size=200, max=9999999
            ),
        ), 
        build_value_setter_line(
            "value-setter-panel-track-time-step",
            "Time for one step [s]:",
            state_value["cur_track_meas_setting"]["time_step"],
            daq.NumericInput(
                id="time_step_track_input", value=5, className="setting-input", size=200, max=9999999
            ),
        )
    ]

from typing import Sized
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
from dash_html_components.P import P
import plotly.graph_objs as go


meas_modes = {
    'fixed_value': 0,
    'tracking': 1,
    'sweeping': 2,
}

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
                                html.Button("Update", id="value-setter-set-btn"),
                                html.Button(
                                    "View current setup",
                                    id="value-setter-view-btn",
                                    # n_clicks=0,
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
                children=[daq.StopButton(id="stop-button", size=160, n_clicks=0)],
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
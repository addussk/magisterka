import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import plotly.graph_objs as go


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
def generate_temp_chart():
    return None

# do zaimplementowania
def build_tab_1():
    return None

def build_quick_stats_panel():
    return html.Div(
        id="quick-stats",
        className="row",
        children=[
            html.Div(
                id="card-1",
                children=[
                    html.P("Operator ID"),
                    daq.LEDDisplay(
                        id="operator-led",
                        value="999",
                        color="#92e0d3",
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
            
        ],
    )

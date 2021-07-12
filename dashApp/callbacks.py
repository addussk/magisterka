from dashApp.models import Frequency, Temperature
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import dash_html_components as html
import plotly.graph_objs as go
from dashApp.templates import build_tab_1, build_quick_stats_panel, build_chart_panel, build_bottom_panel

dataFreq = { 
    'Freq': [],
    'Time': [],
    'TurnOn': False,
}

def register_callbacks(dashapp):
    from dashApp.extensions import db
        
    # Multiple components can update everytime interval gets fired.
    @dashapp.callback(Output('control-chart-live', 'figure'),
                Input('interval-component', 'n_intervals'))
    def update_graph_live(n):

        # get all users in database
        frequency_measurement = db.session.query(Frequency).order_by(Frequency.time_of_measurement.desc()).limit(50).all()
        last_measurement = db.session.query(Frequency).order_by(Frequency.id.desc()).first()
        if last_measurement.get()[1] != dataFreq['Time']:
            temp_y = [ el.get()[0] for el in frequency_measurement]
            temp_x = [ el.get()[1] for el in frequency_measurement]
            dataFreq['Time'] = temp_x[-1]

        fig={
                "data": [
                    {
                        "x": temp_x,
                        "y": temp_y,
                        "mode": "lines+markers",
                        'type': 'scatter'
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


        return fig

    @dashapp.callback(
    Output('thermometer-indicator', 'value'),
    [Input('interval-component', 'n_intervals')]
    )
    def update_therm_col(val):
        last_measurement = db.session.query(Temperature).order_by(Temperature.id.desc()).first()

        return int(last_measurement.get_temperature())

    @dashapp.callback(
        [Output("app-content", "children"), Output("interval-component", "n_intervals")],
        [Input("app-tabs", "value")],
        [State("n-interval-stage", "data")],
    )
    def render_tab_content(tab_switch, stopped_interval):
        if tab_switch == "tab1":
            return build_tab_1(), stopped_interval
        return (
            html.Div(
                id="status-container",
                children=[
                    build_quick_stats_panel(),
                    html.Div(
                        id="graphs-container",
                        children=[build_chart_panel(), build_bottom_panel() ],
                    ),
                ],
            ),
            stopped_interval,
        )
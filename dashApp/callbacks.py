from dashApp.models import Frequency
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import dash_html_components as html
import plotly
from dashApp.templates import build_tab_1, build_quick_stats_panel, build_chart_panel, build_bottom_panel

dataFreq = { 
    'Freq': [],
    'Time': [],
    'TurnOn': False,
}

def register_callbacks(dashapp):
    from dashApp.extensions import db
    
    @dashapp.callback(Output('live-update-text', 'children'),
                  Input('interval-component', 'n_intervals'))
    def update_metrics(n):
        curr_time = dt.now().strftime("%H:%M:%S")
        curr_date = dt.now().strftime("%m:%d:%Y")
        style = {'padding': '5px', 'fontSize': '16px'}

        return [
            html.Span('Date: {}'.format(curr_date), style=style),
            html.Span('Time: {}'.format(curr_time), style=style),
        ]
        
        # Multiple components can update everytime interval gets fired.
    @dashapp.callback(Output('live-update-graph', 'figure'),
                Input('interval-component', 'n_intervals'))
    def update_graph_live(n):
        
        # Create the graph with subplots
        fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
        
        fig['layout']['margin'] = {
            'l': 30, 'r': 10, 'b': 30, 't': 10
        }
        
        # get all users in database
        users = db.session.query(Frequency).order_by(Frequency.time_of_measurement.desc()).limit(50).all()
        last_user = db.session.query(Frequency).order_by(Frequency.id.desc()).first()
        if last_user.get()[1] != dataFreq['Time']:
            temp_y = [ el.get()[0] for el in users]
            temp_x = [ el.get()[1] for el in users]
            dataFreq['Time'] = temp_y[-1]

        fig.append_trace({
            'x': temp_x,
            'y': temp_y,
            'text': dataFreq['Time'],
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)

        return fig

    
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
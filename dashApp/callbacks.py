from dash.dependencies import Input, Output
from datetime import datetime as dt
import dash_html_components as html
import cpuinfo
import psutil
import plotly


dataFreq = { 
    'Freq': [],
    'Time': [],
    'TurnOn': False,
}

def register_callbacks(dashapp):

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
        
        time = dt.now()
        
        if dataFreq['TurnOn']:
            dataFreq['Freq'].append(psutil.cpu_percent())
            dataFreq['Time'].append(time)
        
        # Create the graph with subplots
        fig = plotly.tools.make_subplots(rows=1, cols=1, vertical_spacing=0.2)
        
        fig['layout']['margin'] = {
            'l': 30, 'r': 10, 'b': 30, 't': 10
        }

        fig.append_trace({
            'x': dataFreq['Time'],
            'y': dataFreq['Freq'],
            'text': dataFreq['Time'],
            'mode': 'lines+markers',
            'type': 'scatter'
        }, 1, 1)

        return fig

    @dashapp.callback(Output('container-button-timestamp', 'children'),
                Input('btn-record', 'n_clicks'))
    def displayClick(btn1):
        dataFreq['TurnOn'] = not dataFreq['TurnOn']

        if dataFreq['TurnOn']:
            return "Recording"
        else: return "Click to recording!"
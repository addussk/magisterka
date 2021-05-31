import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from numpy import True_
import plotly
from dash.dependencies import Input, Output

dataFreq = { 
    'Freq': [],
    'Time': [],
    'TurnOn': False,
}


#needed to read freq of CPU
import cpuinfo
import psutil

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = html.Div(
    html.Div([
        html.H4('Live Chart'),
        html.Div(id='live-update-text'),
        html.Div(id='click-update-text'),
        dcc.Graph(id='live-update-graph'),
        html.Button('Record', id='btn-record', n_clicks=0),
        html.Div(id='container-button-timestamp'),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ], style={'text-align':'center'})
)


@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def update_metrics(n):
    curr_time = datetime.datetime.now().strftime("%H:%M:%S")
    curr_date = datetime.datetime.now().strftime("%m:%d:%Y")
    style = {'padding': '5px', 'fontSize': '16px'}

    return [
        html.Span('Date: {}'.format(curr_date), style=style),
        html.Span('Time: {}'.format(curr_time), style=style),
    ]


# Multiple components can update everytime interval gets fired.
@app.callback(Output('live-update-graph', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_graph_live(n):
    
    time = datetime.datetime.now() - datetime.timedelta()
    
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

@app.callback(Output('container-button-timestamp', 'children'),
              Input('btn-record', 'n_clicks'))
def displayClick(btn1):
    dataFreq['TurnOn'] = not dataFreq['TurnOn']

    if dataFreq['TurnOn']:
        return "Recording"
    else: return "Click to recording!"
    
if __name__ == '__main__':
    app.run_server(debug=True)
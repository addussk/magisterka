from dashApp.models import Frequency, Temperature, Ustawienia
from dash.dependencies import Input, Output, State
from datetime import datetime as dt
import dash_html_components as html
import plotly.graph_objs as go
from dashApp.templates import *
from dashApp.extensions import db
from database import *

dataFreq = { 
    'Freq': [],
    'Time': [],
    'TurnOn': 1,
}

def write_to_db(data):
    Ustawienia(meas_mode=0, start_freq=data[0], stop_freq=0, power=data[1], time_stemp=data[2])
    db.session.add(Ustawienia(meas_mode=0, start_freq=data[0], stop_freq=0, power=data[1], time_stemp=data[2]))
    db.session.commit()

def save_param(param):
    print("Ustawienia pomiaru do zapisania: {}".format(param))
    write_to_db(param)

def register_callbacks(dashapp):
    fixed_freq_input = daq.NumericInput(
        id="fixed_freq_input", value=100, className="setting-input", size=200, max=9999999
    )
    # Multiple components can update everytime interval gets fired.
    @dashapp.callback(
        Output('control-chart-live', 'figure'),
        Input('interval-component', 'n_intervals'))
    def update_graph_live(n):
        # get all users in database
        frequency_measurement = db.session.query(Frequency).order_by(Frequency.time_of_measurement.desc()).limit(20).all()
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
    
    @dashapp.callback(
        Output("value-setter-panel", "children"),
        Input("metric-select-dropdown", "value"),
        State("value-setter-store", "data"),
    )
    def build_value_setter_panel(dd_sel_mode, state_value):
        if dd_sel_mode is None:
            return  html.Div( 
                id="inputs_fix_meas",
                children=fix_meas_tab(state_value),
                ) # by default
        if dd_sel_mode is meas_modes["Fixed Frequency"]:
            return  fix_meas_tab(state_value)
        elif dd_sel_mode is meas_modes["Tracking"]:
            return track_meas_tab(state_value)
        elif dd_sel_mode is meas_modes["Sweeping"]:
            raise NameError('Do zaimplementowania')
            
        else: raise NameError('Ivalid Mode')

    # @@@ Callbacks to update stored data via click @@@
    @dashapp.callback(
        [   Output("value-setter-store", "data"),
            Output("fixed_freq_input", "value"),
            Output("power_fm_input", "value"),
            Output("time_step_fm_input", "value"),
        ],
        [   
            Input("value-setter-set-btn", "n_clicks"),
            Input("value-setter-panel", "children")],
        [
            State("metric-select-dropdown", "value"),
            State("value-setter-store", "data")
        ]
    )   # set_bn ilosc klikniec, mode - wybrany tryb (0 fixed mode), store state
    def set_value_setter_store(set_btn, input, mode, store):
        res = []
        print(store)
        for x in input:
            x = x["props"]
            while type(x) == type([]) or type(x) == type({}):
                if type(x) == type([]):
                    for list_dict in x:
                        x = list_dict["props"]

                if "children" in x:
                    x = x["children"]
                if "props" in x:
                    x = x["props"]
                         
                if type(x) is type({}) and ("value" in x) :
                    res.append((x['id'], x['value']))
                    break
        print(res)

        save_param([1,10,100])

        if set_btn is None:
            return store, 100, 10, 5
        else:
            if mode == 0 or mode == 1:
                store["cur_fix_meas_setting"]["frequency"] = res[0][1]
                store["cur_fix_meas_setting"]["power"] = res[1][1]
                store["cur_fix_meas_setting"]["time_step"] = res[2][1]

                return store, res[0][1], res[1][1], res[2][1]
            elif mode == 2:
                raise NameError("Need to be implemented")
                store["cur_sweep_meas_setting"] = 1919
            else:
                raise NameError("Updating store error")
            return store, 100, 10, 5
    
    @dashapp.callback(
        Output( component_id='pwr-on-off-buton', component_property="buttonText"),
        Input('pwr-on-off-buton', 'n_clicks'),
        State( component_id='pwr-on-off-buton', component_property="buttonText"),
    )
    def update_output(n_click, btnText,):
        print("dupa")
        print(btnText)
        if btnText == "TURN ON":
            return "TURN OFF"
        elif btnText == "TURN OFF":
            return "TURN ON"
        else: raise Exception("Error with power button")
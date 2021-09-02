from dashApp.models import Frequency, FrontEndInfo, Temperature, Ustawienia
from dash.dependencies import Input, Output, State
import dash_html_components as html
from dashApp.templates import *
from dashApp.extensions import db
from database import *

dataFreq = { 
    'Freq': [],
    'Time': [],
    'TurnOn': 1,
}

def write_to_db_alchemy(data):
    Ustawienia(meas_mode=0, start_freq=data[0], stop_freq=0, power=data[1], time_stemp=data[2])
    db.session.add(Ustawienia(meas_mode=0, start_freq=data[0], stop_freq=0, power=data[1], time_stemp=data[2]))
    db.session.commit()

def save_param(param):
    print("Ustawienia pomiaru do zapisania: {}".format(param))
    if param[0] == 0:
        write_to_database(DATA_BASE, "mode", param[0])
        write_to_database(DATA_BASE, "start_freq", param[1][1])
        write_to_database(DATA_BASE, "power", param[2][1])
        write_to_database(DATA_BASE, "time_stamp", param[3][1])
        write_to_database(DATA_BASE, "meas_req", param[4])
    if param[0] == 1:
        write_to_database(DATA_BASE, "mode", param[0])
        write_to_database(DATA_BASE, "start_freq", param[1][1])
        write_to_database(DATA_BASE, "stop_freq", param[2][1])
        write_to_database(DATA_BASE, "power", param[3][1])
        write_to_database(DATA_BASE, "freq_step", param[4][1])
        write_to_database(DATA_BASE, "time_stamp", param[5][1])
        write_to_database(DATA_BASE, "meas_req", param[6])
    #write_to_db(param)

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
        Output("chart_scannig_container", "children"),
        Input('interval-component', 'n_intervals'),
    )
    def create_scanning_graph(n_interval):
        if read_from_database(DATA_BASE, "isScanAvalaible"):
            x_data = [ el[1] for el in SCANNING_RESULT]
            y_data = [ el[0] for el in SCANNING_RESULT]
            return dcc.Graph(
                        id='scanning-result-graph',
                        figure={
                            'data': [
                                {'x': x_data, 
                                'y': y_data, 
                                'type': 'lines+markers', },
                            ],
                            'layout': {
                                'title': 'Scanning results'
                            }
                        }
                    ),
        else: None # stworzyc gif loading jesli mode zostal wystawiony i pomiary sie dokonuje

    @dashapp.callback(
        Output("slider_min_pointer", "children"),
        Input("value-setter-set-btn", "n_clicks"),
    )
    def create_slider(clicked):
        if clicked:
            return [
                dcc.Slider( 
                    id="slider-drag",
                    min=2000,
                    max=3000,
                    step=1,
                    value=2500,
                ),
                html.Div(id='slider-drag-output', style={'margin-top': 20}),
            ]
        else:
            return None

    @dashapp.callback(
        Output('slider-drag-output', 'children'),
        [Input('slider-drag', 'drag_value'), Input('slider-drag', 'value')]
        )
    def display_value(drag_value, value):

        tmp_recent_slider_val = (db.session.query(FrontEndInfo).order_by(FrontEndInfo.id.desc()).first()).get_slider()

        if value != tmp_recent_slider_val:
            db.session.add(FrontEndInfo(slider_val=value))
            db.session.commit()

        return 'drag_value: {} | value: {}'.format(drag_value, value)

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
                id="default_input_area",
                children=None,
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
        Output("value-setter-store", "data"),
        [   
            Input("value-setter-set-btn", "n_clicks"),
            Input("value-setter-panel", "children")],
        [
            State("metric-select-dropdown", "value"),
            State("value-setter-store", "data"), 
        ]
    )   # set_bn ilosc klikniec, mode - wybrany tryb (0 fixed mode), store state
    def set_value_setter_store(set_btn, input, mode, store):
        res = [mode]
        status_measurement = read_from_database(DATA_BASE, "meas_req")

        # sprawdz czy mozna zaczac nowy pomiar
        if status_measurement in [None, MEASUREMENT_FREE]:
            # rozpakowanie htmla aby dotrzec do parametrow z formularza
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
            # ustawiamy status pomiarow na start
            res.append(MEASUREMENT_START)

            # zapisujemy do bazy danych, rozne od None zeby dochodzilo do zapisu po kliknieciu buttonu a nie przy inicjalizaci.
            if set_btn != None:
                save_param(res)

        # fragment odpowiedzialny za ustawianie wartosci w formularzu
        if set_btn is None:
            return store
        else:
            if mode == 0 or mode == 1:
                store["cur_fix_meas_setting"]["frequency"] = res[1][1]
                store["cur_fix_meas_setting"]["power"] = res[2][1]
                store["cur_fix_meas_setting"]["time_step"] = res[3][1]

                return store
            elif mode == 2:
                raise NameError("Need to be implemented")
                store["cur_sweep_meas_setting"] = 1919
            else:
                raise NameError("Updating store error")
    
    @dashapp.callback(
        Output( component_id='pwr-on-off-buton', component_property="buttonText"),
        Input('pwr-on-off-buton', 'n_clicks'),
        State( component_id='pwr-on-off-buton', component_property="buttonText"),
    )
    def update_pwr_supply_btn(n_click, btnText):
        if n_click:
            if btnText == "TURN ON":
                write_to_database(DATA_BASE, "tool_status", TURN_ON)
                return "TURN OFF"
            elif btnText == "TURN OFF":
                write_to_database(DATA_BASE, "tool_status", TURN_OFF)
                return "TURN ON"
            else: raise Exception("Error with power button")
        else:
            return btnText
    
    @dashapp.callback(
        Output( component_id="value-setter-view-btn", component_property="contextMenu"),
        Input("value-setter-view-btn", 'n_clicks'),
    )
    def stop_btn(n_click):
        if n_click:
            meas_status = read_from_database(DATA_BASE, "meas_req")
            if meas_status == MEASUREMENT_ONGOING:
                write_to_database(DATA_BASE, "meas_req", MEASUREMENT_STOP)
                return "True"
            else: "False"
        else: return "else"
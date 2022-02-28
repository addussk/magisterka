from statemachine import DataBase
from dashApp.models import FrontEndInfo, Temperature, MeasSettings, MeasurementInfo
from dash.dependencies import Input, Output, State
from dash import html
from dashApp.templates import *
from dashApp.extensions import db
from defines import *
import dash
import datetime

Global_DataBase = DataBase(db)

ATTENUATION_LIST = [0, 0.5, 1, 2, 4, 8, 16, 32] 

def generate_graph(axis_x, axis_y, name):
    all_fig = list()

    # tworzenie funkcji w zaleznosci od wielkosci listy axis_y
    # case dla przypadku gdy axis_y jest pojedyncza lista
    if type(axis_y[0]) == type([]):
        for el in axis_y:
            temp_dict = {
                "x" : axis_x,
                "y" : el,
                "mode": "lines+markers",
                'type': 'scatter',
                'name': name,
            }
            all_fig.append(temp_dict)
    # case dla listy list dla wartosci y, w przypadku gdy wiecej niz jeden checkbox zostanie zaklikany
    else:
        temp_dict = {
            "x" : axis_x,
            "y" : axis_y,
            "mode": "lines+markers",
            'type': 'scatter',
            'name': name,
        }
        all_fig.append(temp_dict)
    
    # ustawienia graphu
    fig={
                "data": [ el for el in all_fig ],
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

def register_callbacks(dashapp):

    @dashapp.callback(
        Output("isDiagWindShow", "on"),
        [
            Input("keyboard", "keydown"),
            Input("exit_btn", "n_clicks"),
            Input("confirm_btn", "n_clicks"),
            Input('value-setter-view-btn', 'n_clicks'),
        ], prevent_initial_call=True
    )
    def change_diagWind_state(keyb, ex_btn, conf_btn, stop_btn_tab1):
        ctx = dash.callback_context
        trigger_by = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_by in ["value-setter-view-btn"]:
            if (Global_DataBase.read_last_record(MeasSettings).get_state() == MEASUREMENT_ONGOING) and stop_btn_tab1:
                return True
            else: return False

        elif trigger_by == "keyboard":
            if keyb['key'].lower() == "enter":
                Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
                return False
            elif keyb['key'].lower() == "escape":
                return False

        elif trigger_by == "confirm_btn":
            Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
            return False

        elif trigger_by in ["exit_btn"]:
            return False

        else: return dash.no_update
    
    @dashapp.callback(
        Output("isDiagWindShow_tab2", "on"),
        [
            Input("keyboard", "keydown"),
            Input("exit_btn_tab2", "n_clicks"),
            Input("confirm_btn_tab2", "n_clicks"),
            Input('stopbutton-quick-stats', 'n_clicks'),
        ], prevent_initial_call=True
    )
    def change_diagWind_state_tab2(keyb, ex_btn, conf_btn, stop_btn_tab2):
        ctx = dash.callback_context
        trigger_by = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_by in ["stopbutton-quick-stats"]:
            if (Global_DataBase.read_last_record(MeasSettings).get_state() == MEASUREMENT_ONGOING) and stop_btn_tab2:
                return True
            else: return False

        elif trigger_by == "keyboard":
            if keyb['key'].lower() == "enter":
                Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
                return False
            elif keyb['key'].lower() == "escape":
                return False

        elif trigger_by == "confirm_btn_tab2":
            Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
            return False

        elif trigger_by in ["exit_btn_tab2"]:
            return False

        else: return dash.no_update
    
    # Funkcja wyswietlajaca okno warning dialog na oknie Meas settings
    @dashapp.callback(
        Output("dialogBox", "style"),
        Input("isDiagWindShow", "on"), prevent_initial_call=True
        )
    def keydown_tab1(isOn):
        return {"display": "block"} if isOn else {"display": "none"}

    # Funkcja wyswietlajaca okno warning dialog na oknie Live chart meas
    @dashapp.callback(
        Output("dialogBox_tab2", "style"), 
        Input("isDiagWindShow_tab2", "on"), prevent_initial_call=True
        )
    def keydown_tab2(isOn):
        return {"display": "block"} if isOn else {"display": "none"}
    
    inputs = [ Input('interval-component', 'n_intervals'),
            Input('trace_checklist', 'value'),]
    el_counter = 0
    print(len(Global_DataBase.read_record_all(MeasurementInfo)))
    for el in range(1,len(Global_DataBase.read_record_all(MeasurementInfo))+1):
        inputs.append(Input('{}_buttonss'.format(el), "n_clicks"),)
    print(inputs)
    
    # Wiele komponentów może się aktualizować za każdym razem, gdy zostanie uruchomiony interwał.
    @dashapp.callback(
        Output('control-chart-live', 'figure'),
        inputs,
        )
    def update_graph_live(n, checkbox_list, *args):
        x_ax = list()
        y_ax = list()

        # sprawdzic czy jest aktualnie pomiar
        meas_state = Global_DataBase.read_table(MeasSettings).get_state()

        if meas_state == MEASUREMENT_ONGOING:
            # jesli jest pomiar, wyswietlac dane na biezaco.
            for el in checkbox_list:
                time_scope_last_meas = Global_DataBase.read_last_record(MeasurementInfo).get_time_scope()
                frequency_measurement = Global_DataBase.read_filtered_table_live(time_scope_last_meas)
                
                x_ax = [ el.get_data_meas() for el in frequency_measurement]

                if el == "transmit_pwr":
                    y_ax.append([ el.get_trans_pwr() for el in frequency_measurement])

                elif el == "received_pwr":
                    y_ax.append([ el.get_meas_pwr() for el in frequency_measurement])

                elif el == "sys_temp":
                    # dodac odczyt temperatury i zapisanie do listy dict
                    pass
            return generate_graph( x_ax, y_ax, "stub")
        # jesli nie ma :
        else:
            ctx = dash.callback_context
            # jesli zostal wybrane pomiary z listy wyswietlic je
            if ctx.triggered:
                # Uzyskaj ostatnio wywołane id i prop_type
                splitted = ctx.triggered[0]["prop_id"].split(".")
                prop_type = splitted[1]

                if prop_type == "n_clicks":
                    prop_id = splitted[0]
                    meas_info = Global_DataBase.read_specific_row(MeasurementInfo, int(prop_id[0]))
                    results_table = Global_DataBase.read_filtered_table(meas_info.get_time_scope())
                    x_ax = [ el.get_data_meas() for el in results_table]

                    for check_box_el in checkbox_list:
                        if check_box_el == "transmit_pwr":
                            y_ax.append([ el.get_trans_pwr() for el in results_table])

                        elif check_box_el == "received_pwr":
                            y_ax.append([ el.get_meas_pwr() for el in results_table])

                        elif check_box_el == "sys_temp":
                            # dodac odczyt temperatury i zapisanie do listy dict
                            pass

                    return generate_graph( x_ax, y_ax, "stub")

                else: return dash.no_update

            # TBD: wyswietlic ostatni pomiar z listy    
            else: return dash.no_update


    @dashapp.callback(
        Output("chart_scannig_container", "children"),
        Input('interval-component', 'n_intervals'),
    )
    def create_scanning_graph(n_interval):

        if Global_DataBase.read_record(FrontEndInfo, "isScanAvalaible") == True:
            x_data = [ el[1] for el in SCANNING_RESULT]
            y_data = [ el[0] for el in SCANNING_RESULT]
            minimum_val = min(SCANNING_RESULT)
            meas_set = Global_DataBase.read_table(MeasSettings)
            measured_min = meas_set.get_minimum()
            
            return dcc.Graph(
                        id='scanning-result-graph',
                        figure={
                            'data': [
                                {'x': x_data, 
                                'y': y_data, 
                                'type': 'lines+markers', },
                                {'x': [minimum_val[1], minimum_val[1]], 
                                'y': [abs(minimum_val[0]), (-1)*abs(minimum_val[1])], 
                                'type': 'lines+markers', },
                                {'x': [measured_min[1], measured_min[1]], 
                                'y': [abs(minimum_val[0]), (-1)*abs(minimum_val[1])], 
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
        [
            Input("value-setter-set-btn", "n_clicks"),
            Input("value-setter-view-btn", "n_clicks"),
        ]
    )
    def create_slider(show_slider, hide_slider):
        ctx = dash.callback_context

        if not ctx.triggered:
            button_id = 'No clicks yet'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if button_id == "value-setter-set-btn":
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

        if value != Global_DataBase.read_recent_slider_val():
            Global_DataBase.update_setting(FrontEndInfo, FrontEndInfo.slider_val, value)

        return 'drag_value: {} | value: {}'.format(drag_value, value)

    @dashapp.callback(
        Output('thermometer-indicator', 'value'),
        [Input('interval-component', 'n_intervals')]
    )
    def update_therm_col(val):
        last_measurement = db.session.query(Temperature).order_by(Temperature.id.desc()).first()

        if last_measurement == None:
            pass
        else:
            return int(last_measurement.get_sys_temperature())

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
        [
            Output("value-setter-panel", "children"),
            Output("value-setter-panel", "style"),
        ],
        Input("metric-select-dropdown", "value"),
        State("value-setter-store", "data"),
    )
    def build_value_setter_panel(dd_sel_mode, state_value):
        style = {
            'display': 'flex',
            'flex-direction': 'column',
            'margin-top':'5rem',
        }

        if dd_sel_mode is None:
            return  [] ,style
        if dd_sel_mode is DROP_LIST_MEAS_MODE["Fixed Frequency"]:
            return  fix_meas_tab(state_value), style
        elif dd_sel_mode is DROP_LIST_MEAS_MODE["Tracking"]:
            return track_meas_tab(state_value), style
        elif dd_sel_mode is DROP_LIST_MEAS_MODE["Sweeping"]:
            raise NameError('Do zaimplementowania')
            
        else: raise NameError('Ivalid Mode')
    
    @dashapp.callback(
        Output('option-calib-panel', 'children'),
        Input('dropdownlist-calib-panel', 'value'),
    )
    def build_calibration_panel(choosen_elem_dropdownlist):
        
        if choosen_elem_dropdownlist == DROP_LIST_CALIB['Attenuator']:
            return html.Div(
                children=[
                    html.Label("Choose Attenuation: ",className="four columns", style={ 'font-size': '1.8rem', 'margin-left':'5%'}),
                    html.Div(
                        className="three columns",
                        children=[
                            dcc.Dropdown(
                                id="db-list-calib-panel",
                                options=list( {"label": str(dB_value) + " dB", "value": idx } for dB_value, idx in zip(ATTENUATION_LIST, range(len(ATTENUATION_LIST))) ),
                                value=0,
                            ),
                        ],
                        style={ 'float':"right", 'margin-right':'15%' },
                    )
                ],
                className='row',
                style={
                    'margin-top':'15%',
                },
            )

    @dashapp.callback(
        # tymczasowo tak zdefiniowany output
        Output('calib-set-btn', 'value'),
        [
            Input('calib-set-btn', 'n_clicks'),
            Input('db-list-calib-panel', 'value'),
        ],
    )
    def set_calib_btn(n_clicks, attVal):
        # callback context sluzy do sprawdzenia czy callback wywolany jest podczas inicjalizacji
        ctx = dash.callback_context
        
        # Akcja podejmowana tylko po wywolaniu przez klikniecie calibrate button
        if ctx.triggered[0]['prop_id'] == "calib-set-btn.n_clicks":
            # Zabezpieczenie by nie wykonac akcji podczas inicjalizacji strony
            if ctx.triggered[0]['value'] == None:
                return dash.no_update
            else:
                # wyslij informacje do serwera by przeprowadzic kalibracje urzadzenia
                Global_DataBase.update_calib_info(START_CALIBRATE, ATTENUATION_LIST[attVal])
                
                # TODO: wyswietl okienko z potwierdzeniem 
                return dash.no_update
        else: return dash.no_update

            
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
        state_measurement = Global_DataBase.read_table(MeasSettings)

        # sprawdz czy mozna zaczac nowy pomiar
        if state_measurement.get_state() in [None, MEASUREMENT_FREE]:
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
                Global_DataBase.configure_measurement(res)
                Global_DataBase.create_MeasurementInfo("badanie {}".format(set_btn), datetime.datetime.now())
        else:
            #TBD : komunikat ze trwa aktualnie pomiar
            pass

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
        Output('powerbutton', 'on'),
        Input('powerbutton', 'on')
    )
    def power_supply_btn(state):
        # callback context sluzy do sprawdzenia czy callback wywolany jest podczas inicjalizacji
        ctx = dash.callback_context

        if ctx.triggered[0]['value'] == None:
            # Odczytanie stanu zasilacza z maszyny stanow i ustawienie odpowiedniego stanu.
            record = Global_DataBase.read_last_record(FrontEndInfo).get_tool_status()
            return record
        else:
            tool_status = Global_DataBase.read_table(FrontEndInfo).get_tool_status()

            if tool_status:
                # zasilacz byl wlaczony
                Global_DataBase.update_setting(FrontEndInfo, FrontEndInfo.tool_status, False)
                return False
            elif tool_status == False:
                # zasilacz byl wylaczony
                Global_DataBase.update_setting(FrontEndInfo, FrontEndInfo.tool_status, True)
                return True
            else: raise Exception("Error with power button")

    @dashapp.callback(
        Output("measure-triggered", 'color'),
        Input("measure-triggered", 'color')
    )
    def update_meas_indic(input):
        retColor = None
        meas_state = Global_DataBase.read_table(MeasSettings).get_state()

        if meas_state == MEASUREMENT_ONGOING:
            retColor = "#1cfa089d"
        else:
            retColor="#fa2c089d"

        return retColor

    # Funkcja wlaczajaca lub wylaczajaca mozliwosc klikniecia stop btn
    @dashapp.callback(
        Output('stopbutton-quick-stats', "disabled"),
        Input("stopbutton-quick-stats", 'n_clicks'),
    )
    def stop_btn_diasbled_on_off(n_click):
        # read meas status from state machine
        meas_state = Global_DataBase.read_table(MeasSettings).get_state()
        if meas_state == MEASUREMENT_ONGOING:
            if n_click:
                return True
            # enable pressing button
            else:
                return False
        #  stop button cannot be pressed
        else: return True

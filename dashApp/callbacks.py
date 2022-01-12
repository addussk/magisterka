from statemachine import DataBase
from dashApp.models import FrontEndInfo, Temperature, MeasSettings, MeasurementInfo
from dash.dependencies import Input, Output, State
from dash import html
from dashApp.templates import *
from dashApp.extensions import db
from database import *
import dash
import datetime
import json

Global_DataBase = DataBase(db)

def generate_graph(axis_x, axis_y, name):
    fig={
                "data": [
                    {
                        "x" : axis_x,
                        "y" : axis_y,
                        "mode": "lines+markers",
                        'type': 'scatter',
                        'name': name,}
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
    # fig = go.Figure(data=[go.Scatter(x=axis_x, y=axis_y)])
    return fig

def register_callbacks(dashapp):

    @dashapp.callback(
        Output("isDiagWindShow", "on"),
        [
            Input("keyboard", "keydown"),
            Input("exit_btn", "n_clicks"),
            Input("confirm_btn", "n_clicks"),
            Input("dialog-btn", "n_clicks"),
        ], prevent_initial_call=True
    )
    def change_diagWind_state(keyb, ex_btn, conf_btn, dial_btn):
        ctx = dash.callback_context
        trigger_by = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_by == "dialog-btn":
            if dial_btn > 0:
                return True
            else: return False

        elif trigger_by == "keyboard":
            if keyb['key'].lower() == "enter":
                return False
                return {"display": "none"}
            elif keyb['key'].lower() == "escape":
                return False
                return {"display": "none"}

        elif trigger_by in ["exit_btn", "confirm_btn"]:
            return False
            return {"display": "none"}
        else: return dash.no_update
        
    
    @dashapp.callback(
        Output("dialogBox", "style"), 
        Input("isDiagWindShow", "on"), prevent_initial_call=True
        )
    def keydown(isOn):
        return {"display": "block"} if isOn else {"display": "none"}
    
    inputs = [ Input('interval-component', 'n_intervals'),
            Input('trace_checklist', 'value'),]
    el_counter = 0
    print(len(Global_DataBase.read_record_all(MeasurementInfo)))
    for el in range(1,len(Global_DataBase.read_record_all(MeasurementInfo))+1):
        inputs.append(Input('{}_buttonss'.format(el), "n_clicks"),)
    print(inputs)
    
    # Multiple components can update everytime interval gets fired.
    @dashapp.callback(
        Output('control-chart-live', 'figure'),
        inputs,
        )
    def update_graph_live(n, checkbox_list, *args):
        
        meas_state = Global_DataBase.read_table(MeasSettings).get_state()

        ctx = dash.callback_context
        if ctx.triggered:
            # Get most recently triggered id and prop_type
            splitted = ctx.triggered[0]["prop_id"].split(".")
            prop_id = splitted[0]
            prop_type = splitted[1]

            if prop_type == "n_clicks":
                meas_info = Global_DataBase.read_specific_row(MeasurementInfo, int(prop_id[0]))
                results_table = Global_DataBase.read_filtered_table(meas_info.get_time_scope())
   
                transmitted_pwr = [ el.get_trans_pwr() for el in results_table]
                data_meas = [ el.get_data_meas() for el in results_table]
                return generate_graph( data_meas, transmitted_pwr, "stub")

        if meas_state != MEASUREMENT_ONGOING:
            return dash.no_update

        time_scope_last_meas = Global_DataBase.read_last_record(MeasurementInfo).get_time_scope()
        frequency_measurement = Global_DataBase.read_filtered_table_live(time_scope_last_meas)
        freq = [ el.get_meas_freq() for el in frequency_measurement]
        transmitted_pwr = [ el.get_trans_pwr() for el in frequency_measurement]
        received_pwr = [ el.get_meas_pwr() for el in frequency_measurement]
        data_meas = [ el.get_data_meas() for el in frequency_measurement]

        fig_dict = dict()

        for el in checkbox_list:
            if el == "transmit_pwr":
                fig_dict[el] = {
                    "x" : data_meas,
                    "y" : transmitted_pwr,
                        "mode": "lines+markers",
                        'type': 'scatter',
                    'name': el,
                }
            elif el == "received_pwr":
                fig_dict[el] = {
                    "x" : data_meas,
                    "y" : received_pwr,
                    "mode": "lines+markers",
                    'type': 'scatter',
                    'name': el,
                }
            elif el == "sys_temp":
                # dodac odczyt temperatury i zapisanie do listy dict
                pass


        fig={
                "data": [ fig_dict[el] for el in fig_dict ],
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
        Output( component_id='pwr-on-off-buton', component_property="buttonText"),
        Input('pwr-on-off-buton', 'n_clicks'),
        State( component_id='pwr-on-off-buton', component_property="buttonText"),
    )
    def update_pwr_supply_btn(n_click, btnText):
        if n_click:
            if btnText == "TURN ON":
                Global_DataBase.update_setting(FrontEndInfo, FrontEndInfo.tool_status, True)
                return "TURN OFF"
            elif btnText == "TURN OFF":
                Global_DataBase.update_setting(FrontEndInfo, FrontEndInfo.tool_status, False)
                return "TURN ON"
            else: raise Exception("Error with power button")
        else:
            # initial state: dodac odczyt stanu dla zasilacza
            return btnText
    
    @dashapp.callback(
        Output( component_id="value-setter-view-btn", component_property="contextMenu"),
        Input("value-setter-view-btn", 'n_clicks'),
    )
    def stop_btn(n_click):
        if n_click:
            meas_state = Global_DataBase.read_table(MeasSettings).get_state()

            if meas_state == MEASUREMENT_ONGOING:
                Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
                return "True"
            else: "False"
        else: return "else"
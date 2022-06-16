from statemachine import DataBase
from dashApp.models import FrontEndInfo, Temperature, MeasSettings, MeasurementInfo
from dash.dependencies import Input, Output, State
from dash import html
from dashApp.templates import *
from dashApp.extensions import db
from defines import *
import dash
import datetime
from drivers import OUTPUT_INDICATORS_FNC

Global_DataBase = DataBase(db)

ATTENUATION_LIST = [0, 0.5, 1, 2, 4, 8, 16, 32]

FORM_INPUT_ID_ARR = ["fixed_freq_input", "power_fix_input"]

start_btn_off_style = {
    'backgroundColor': '#065b0a9d',
}

start_btn_on_style = {
    'backgroundColor': '#08f614',
}

mode_btns_on_style = {
    'border': 'solid 4px rgb(40, 243, 4)',
}

mode_btns_id = ['manual-mode-btn', 'p-track-mode-btn', 'pf-track-mode-btn']

MANUAL_MODE = 0
P_TRACKING_MODE = 1
PF_TRACKING_MODE = 2

UNIT_TO_INC_DEC = 1 # MHz

# Funkcja do wygenerowania elementu dcc.Graph
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

# Funkcja do rozpakowania div w ktorym jest umieszczony formularz
def unpack_html_element(form_to_unzip):
    retArr = []
    for x in form_to_unzip:
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
                retArr.append((x['id'], x['value']))
                break
    return retArr

def register_callbacks(dashapp):

    # Funkcja ustawiajaca kolor start btn oraz status headera
    @dashapp.callback(
        [
            Output('start-btn','style'),
            Output('status-header', 'children')
        ],
        [Input('start-btn-color', 'data'),],
    )
    def update_color(data):
        # W zaleznosci od koloru start btn zaktualizuj wartosc headera
        retHeader = "Status: OFF" if '#065b0a9d' == data['start-btn-style']['backgroundColor'] else "Status: ON"
        
        return [data['start-btn-style'], retHeader]

    @dashapp.callback(
        Output('start-btn-color', 'data'),
        [
            Input('stop-btn', 'n_clicks'),
            Input('start-btn', 'n_clicks'),
        ],
        [
            State('start-btn-color', 'data'),
            State('mode-btn-hg', 'data'),
            State("cfg-mode-store", "data"),
        ],
    )
    def start_stop_btn(n_clicks_stp, n_clicks_str, data, data_mode, cfg_mode):
        # callback context sluzy do sprawdzenia czy callback wywolany jest podczas inicjalizacji
        ctx = dash.callback_context
        # Odczytanie stanu czy pomiar jest dokonywany
        measurement_status = Global_DataBase.read_last_record(MeasSettings).get_state()

        # If obslugujacy callback przy zaladowaniu strony
        if ctx.triggered[0]['value'] == None:
            # jesli pomiar nie jest wystartowany, ustaw odpowiedni kolor
            if MEASUREMENT_FREE == measurement_status:
                data['start-btn-style'] = start_btn_off_style

            # case dla pomiaru ktory jest dokonywany, kolor ma wskazywac ze pomiar jest pobierany
            else:
                data['start-btn-style']=start_btn_on_style

        elif ctx.triggered[0]['prop_id'] == 'stop-btn.n_clicks':
            # Btn zostal wcisniety przez uzytkownika
            if MEASUREMENT_FREE == measurement_status:
                dash.no_update

            elif MEASUREMENT_ONGOING == measurement_status:
                # Zapis  do bazy danych zaczecie pomiaru
                Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
                data['start-btn-style'] = start_btn_off_style
                
        elif ctx.triggered[0]['prop_id'] == 'start-btn.n_clicks':
            cfg_to_store = []
            # Btn zostal wcisniety przez uzytkownika
            if MEASUREMENT_FREE == measurement_status:
                # Zapis  do bazy danych zaczecie pomiaru
                Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_START)
                data['start-btn-style'] = start_btn_on_style

                if mode_btns_id[MANUAL_MODE] == data_mode:
                    # dodanie mode 0 reprezentujacego tracking mode
                    cfg_to_store.append(0)
                    
                    for key, value in cfg_mode['cur_fix_meas_setting'].items():
                        if key != "turn_on":
                            cfg_to_store.append((key,value))
                    
                elif mode_btns_id[P_TRACKING_MODE] == data_mode:
                    # dodanie mode 1 reprezentujacego tracking mode
                    cfg_to_store.append(1)

                    for key, value in cfg_mode['cur_track_meas_setting'].items():
                        if key != "turn_on":
                            cfg_to_store.append((key,value))
                else:
                    raise Exception("Error in start_stop_btn fnc")

                cfg_to_store.append(MEASUREMENT_START)

                # zapisujemy do bazy danych configuracje dla wybranego trybu
                Global_DataBase.configure_measurement(cfg_to_store)
                Global_DataBase.create_MeasurementInfo("badanie {}".format(datetime.datetime.now()), datetime.datetime.now())

            else:
                #TODO: rozwazyc opcje dla manualu, nadpisanie parametru
                dash.no_update

        return data
    
    @dashapp.callback(
        [Output(mode_id, 'style' ) for mode_id in mode_btns_id],
        [Input('mode-btn-hg', 'data')],
    )
    def highlight_mode_btn(data):
        # default value dla: tryb bez zaznaczonego moda
        retArr = [{'border':'none'}, {'border':'none'}, {'border':'none'}]

        # W store przechowywana dana z nazwa btn ktory ma zostac podswietlony, sprawdzamy w tablicy pozycje i edytujemy dla niego styl w zwracanej wartosci
        retArr[mode_btns_id.index(data)] = mode_btns_on_style
        return retArr

    @dashapp.callback(
        Output('mode-btn-hg', 'data'),
        [Input(mode_id, 'n_clicks' ) for mode_id in mode_btns_id],
        [State('mode-btn-hg', 'data')],
    )
    def mode_btn(manual, p_track, pf_track, data):
        ctx = dash.callback_context

        # Odczytanie stanu czy pomiar jest dokonywany
        measurement_status = Global_DataBase.read_last_record(MeasSettings).get_state()
        
        # Init seq
        if ctx.triggered[0]['value'] == None:
            if MEASUREMENT_FREE == measurement_status:
                data = mode_btns_id[MANUAL_MODE]
            else:
                meas_mode = Global_DataBase.read_last_record(MeasSettings).get_mode()
                if MANUAL_MODE == meas_mode:
                    data = mode_btns_id[MANUAL_MODE]
                elif P_TRACKING_MODE == meas_mode:
                   data = mode_btns_id[P_TRACKING_MODE]
                elif PF_TRACKING_MODE == meas_mode:
                    data = mode_btns_id[PF_TRACKING_MODE]
                else:
                    raise Exception("Wrong measurement mode")
        # Seq po wcisnieciu przycisku mode
        else:
            if ctx.triggered[0]['prop_id'] == 'manual-mode-btn.n_clicks':
                data = mode_btns_id[MANUAL_MODE]
            elif ctx.triggered[0]['prop_id'] == 'p-track-mode-btn.n_clicks':
                data = mode_btns_id[P_TRACKING_MODE]
            elif ctx.triggered[0]['prop_id'] == 'pf-track-mode-btn.n_clicks':
                data = mode_btns_id[PF_TRACKING_MODE]
            else:
                raise Exception("Fail in mode_btn fnc")
  
        return data
     
    # Funkcja obslugujace przyciski do ustawiania czestotliwosci
    @dashapp.callback(
        [
            Output('freq_input', 'value'),
            Output('freq-input-val', 'data'),
        ],
        [
            Input('freq-inc-btn', 'n_clicks'),
            Input('freq-dec-btn', 'n_clicks'),
        ],
        [State('freq-input-val', 'data'),],
    )
    def inc_dec_freq(inc_freq_clicked, dec_freq_clicked, current_freq):
        triggered_by = dash.callback_context.triggered[0]['prop_id']
        retValue = current_freq

        # Init seq
        if dash.callback_context.triggered[0]['value'] == None:
            pass
        # Service seq
        else:
            if triggered_by == 'freq-inc-btn.n_clicks':
                retValue = current_freq + UNIT_TO_INC_DEC
            elif triggered_by == 'freq-dec-btn.n_clicks':
                retValue = current_freq - UNIT_TO_INC_DEC
            else:
                raise Exception("Error in inc_dec_freq fnc")
        return [int(retValue), int(retValue)]

    # Funkcja obslugujace przyciski do ustawiania mocy
    @dashapp.callback(
        [
            Output('power_input', 'value'),
            Output('power-input-val', 'data'),
        ],
        [
            Input('power-inc-btn', 'n_clicks'),
            Input('power-dec-btn', 'n_clicks'),
        ],
        [
            State('power-input-val', 'data'),
        ],
    )
    def inc_dec_power(inc_pwr_clicked, dec_pwr_clicked, current_pwr):
        triggered_by = dash.callback_context.triggered[0]['prop_id']
        retValue = current_pwr

        # Init seq
        if dash.callback_context.triggered[0]['value'] == None:
            pass
        # Service seq
        else:
            if triggered_by == 'power-inc-btn.n_clicks':
                retValue = current_pwr + UNIT_TO_INC_DEC
            elif triggered_by == 'power-dec-btn.n_clicks':
                retValue = current_pwr - UNIT_TO_INC_DEC
            else:
                raise Exception("Error in inc_dec_pwr fnc")
        return [int(retValue), int(retValue)]

    # Funkcja odpowiedzialna za odczyt pomiaru temperatury z BD i wyswietleniu na kontrolce
    @dashapp.callback(
        Output('thermometer-indicator', 'value'),
        [Input('interval-component', 'n_intervals')],
    )
    def update_therm_col(val):
        last_measurement = db.session.query(Temperature).order_by(Temperature.id.desc()).first()

        if last_measurement == None:
            pass
        else:
            return int(last_measurement.get_sys_temperature())

    # Callback obslugujacy odczyt kazdego z sensorow za pomoca tablicy zawierajacej wskaznik na funkcje do ich odczytu
    @dashapp.callback(
        [Output((label_indicator_id+"value"), 'children') for label_indicator_id in OUTPUT_INDICATORS.keys()],
        [Input('interval-component', 'n_intervals'),]
    )
    def update_sensors_output(refresh):
        retArr = []

        for indicator in OUTPUT_INDICATORS.keys():
            retArr.append(OUTPUT_INDICATORS_FNC[indicator]())

        if len(retArr) == len(OUTPUT_INDICATORS.keys()):
            return retArr
        else: raise Exception("Wrong length of array in update_sensors_output cb")

    # Callback wyswietlajacy formularz dla danego typu
    @dashapp.callback(
        [
            Output('dialog-form-fix', 'style'),
            Output('dialog-form-p-tracking', 'style'),
            Output('dialog-form-pf-tracking', 'style'),
        ],
        [
            Input('manual-mode-btn', 'n_clicks' ),
            Input('p-track-mode-btn', 'n_clicks' ),
            Input('pf-track-mode-btn', 'n_clicks' ),
            Input('accept-btn-fix', 'n_clicks'),
            Input('accept-btn-p-track', 'n_clicks'),
        ],
    )
    def diag_box_on_off(fix_btn, p_btn, pf_btn, accept_btn_f, accept_btn_p_tr):
        style = [ dash.no_update, dash.no_update, dash.no_update ]

        triggered_by = dash.callback_context.triggered[0]['prop_id']

        if triggered_by == 'manual-mode-btn.n_clicks':
            style = [ {'display':'block'}, dash.no_update, dash.no_update ]
        elif triggered_by == 'p-track-mode-btn.n_clicks':
            style = [ dash.no_update, {'display':'block'}, dash.no_update ]
        elif triggered_by == 'pf-track-mode-btn.n_clicks':
            style = [ dash.no_update, dash.no_update, {'display':'block'} ]
        else:
            style = [ {'display':'none'}, {'display':'none'}, {'display':'none'} ]

        return style
    
    @dashapp.callback(
        Output("cfg-mode-store", "data"),
        [
            Input('dialog-form-fix', 'children'),
            Input('dialog-form-p-tracking', 'children'),
            Input('dialog-form-pf-tracking', 'children'),
            Input('accept-btn-fix', 'n_clicks'),
            Input('accept-btn-p-track', 'n_clicks'),
        ],
        State("cfg-mode-store", "data"),
    )
    def store_measurment_settings(form_fix, form_p_track, form_pf_track, acc_btn_fix, acc_btn_p , cfg_mode):
        retVal, config_from_form = cfg_mode, []
        state_measurement = Global_DataBase.read_table(MeasSettings)
        triggered_by = dash.callback_context.triggered[0]

        if None == triggered_by['value']:
            retVal = dash.no_update
        else:
            # sprawdz czy mozna zaczac nowy pomiar
            if state_measurement.get_state() in [None, MEASUREMENT_FREE]:
                config_from_form = unpack_html_element(form_fix)
                if 'accept-btn-fix.n_clicks' == triggered_by['prop_id']:
                    temp_dict = {}

                    if triggered_by['prop_id'] == 'accept-btn-fix.n_clicks':
                        temp_dict.update({
                            "turn_on": True,
                            "frequency": config_from_form[0][1],
                            "power":config_from_form[1][1],
                            "time_step":config_from_form[2][1],})

                        cfg_mode['cur_fix_meas_setting'] = temp_dict

                    elif triggered_by['prop_id'] == 'accept-btn-p-track.n_clicks':
                        temp_dict.update({
                            "turn_on": True,
                            "start_freq": config_from_form[0][1],
                            "stop_freq":config_from_form[1][1],
                            "power_min":config_from_form[2][1],
                            "power_max":config_from_form[3][1],
                            "time_step":config_from_form[4][1],
                            })

                        cfg_mode['cur_track_meas_setting'] = temp_dict

                    # TODO: opcja dla sweeping mode
                    # elif triggered_by['prop_id'] == 'accept-btn-pf-track.n_clicks':
                        # cfg_mode['']
                    else:
                        raise Exception("Fail in store_measurment_settings fnc")

            else:
                # TODO : komunikat ze trwa aktualnie pomiar
                pass

        return retVal

    @dashapp.callback(
        [
            Output(el, 'value') for el in FORM_INPUT_ID_ARR
        ],
        [
            Input('freq_input', 'value'),
            Input('power_input', 'value'),
        ],
    )
    def update_freq_input_store(freq_in, pwr_in):
        return [freq_in, pwr_in]

    # Wiele komponentów może się aktualizować za każdym razem, gdy zostanie uruchomiony interwał.
    @dashapp.callback(
        Output('control-chart-live', 'figure'),
        Input('interval-component', 'n_intervals'),
        )
    def update_graph_live(n):
        x_ax, y_ax = list(), list()
        retFig = dash.no_update
        # sprawdzic czy jest aktualnie pomiar
        meas_state = Global_DataBase.read_table(MeasSettings).get_state()

        if meas_state == MEASUREMENT_ONGOING:
            # Odczyt pomiarow z bazy danych
            time_scope_last_meas = Global_DataBase.read_last_record(MeasurementInfo).get_time_scope()
            frequency_measurement = Global_DataBase.read_filtered_table_live(time_scope_last_meas)
            x_ax = [ el.get_data_meas() for el in frequency_measurement]
            
            # transmit pwr
            y_ax.append([ el.get_trans_pwr() for el in frequency_measurement])
            # received pwr
            y_ax.append([ el.get_meas_pwr() for el in frequency_measurement])

            return generate_graph( x_ax, y_ax, "stub")
        else:
            triggered_by = dash.callback_context.triggered[0]
            
            if None == triggered_by['value']:
                last_measurement = Global_DataBase.read_last_record(MeasurementInfo)
                results_table = Global_DataBase.read_filtered_table(last_measurement.get_time_scope())
               
                x_ax = [ el.get_data_meas() for el in results_table]

                y_ax.append([ el.get_meas_pwr() for el in results_table])
                y_ax.append([ el.get_trans_pwr() for el in results_table])

                return generate_graph( x_ax, y_ax, "stub")
            
            else:
                retFig =  dash.no_update

        return retFig

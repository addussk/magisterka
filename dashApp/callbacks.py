from statemachine import DataBase
from dashApp.models import FrontEndInfo, Temperature, MeasSettings, MeasurementInfo
from dash.dependencies import Input, Output, State
from dash import html, ALL
from dash import callback_context as ctx
from dashApp.templates import *
from dashApp.extensions import db
from defines import *
import dash
import datetime
from drivers import OUTPUT_INDICATORS_FNC, OUTPUT_INDICATORS
from MlxSensorArray import mlxSensorArrayInstance
from uwave_starter import checkIfUwaveIsRunning, startUwaveProcess, save_table_for_uwave, load_table_from_uwave
from PiecykAutomationInterface import PAI_Instance as pai
from PiecykRequest import PRStartExperiment, PRStopExperiment, PRFakeTemperature, PRSynthFreq, PRSynthLevel, PRSynthRfEnable, PRAttenuator, PRExit, PRPing
from MeasurementSession import MeasurementSessionInstance as msi, TIME_KEY
from ActualConfig import ActualConfigInstance as aci
from ActualConfig import Mode


Global_DataBase = DataBase(db)

ATTENUATION_LIST = [0, 0.5, 1, 2, 4, 8, 16, 32]

FORM_INPUT_ID_ARR = ["fixed-freq-input", "power-fix-input"]

start_btn_off_style = {
    'backgroundColor': '#065b0a9d',
}

start_btn_on_style = {
    'backgroundColor': '#08f614',
}

stop_btn_off_style = {
    'backgroundColor': '#731603d3',
}

stop_btn_on_style = {
    'backgroundColor': '#f10202',
}

mode_btns_on_style = {
    'border': 'solid 4px rgb(40, 243, 4)',
}


mode_btns_id = ['manual-mode-btn', 'p-track-mode-btn', 'pf-track-mode-btn', 't-track-mode-btn']

MANUAL_MODE = 0
P_TRACKING_MODE = 1
PF_TRACKING_MODE = 2
T_TRACKING_MODE = 3




def has_triggered(id):
    return (ctx.triggered[0]['prop_id'] == id+'.n_clicks')

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

# DO USUNIECIA
    # Funkcja ustawiajaca kolor start btn oraz status headera
    # @dashapp.callback(
        # [
            # Output('start-btn','style'),
            # Output('stop-btn','style'),
        # ],
        # [
            # Input('btns-color', 'data'),
        # ],
    # )
    # def update_color(data):
        # if LOG_INPUT_PARAM_ON:
            # print("[CALLBACK] update_color input param: ", data)

        # # W zaleznosci od koloru start btn zaktualizuj wartosc headera
        # #retHeader = "Status: OFF" if '#065b0a9d' == data['start-btn-style']['backgroundColor'] else "Status: ON"
        
        # return [data['start-btn-style'], data['stop-btn-style']]


    @dashapp.callback(
        [Output('status-header', 'children'), Output('header-error', 'style'), Output('header-error-msg','children')],
        Input('interval-component', 'n_intervals')
    )
    def update_status(data):
        resp = pai.request(PRPing("ReadingRfOnOff"))
        status = "Status: ---"
        if resp is not None:
            status = "Status: ON" if resp.rfOn else "Status: OFF"
        display = "block" if mlxSensorArrayInstance.get_communication_error() else "none"
        error = {"display":display}
        return [status, error, "IR sensors - communication error. Check connection cable!"]


    @dashapp.callback(
        Output('hidden-div', 'style'),
        [
            Input('start-btn', 'n_clicks'),
            Input('stop-btn', 'n_clicks'),
        ]
    )
    def start_stop_btn(start_clicks, stop_clicks):
        if has_triggered('stop-btn'):
            print("----- STOP ---------")
            aci.stopProcess()
            
        if has_triggered('start-btn'):
            print("------ START ----------")
            aci.requestStartProcess()
        return None
 

    # Style przyciskow START/STOP odświeżane automatycznie co 1 sek - dzieki temu wątek
    # odpowiedzialny za dany tryb grzania może się zakończyć i to zostanie odzwierciedlone
    # na przyciskach.
    # Przy okazji wyswietlamy aktualny tryb pracy
    @dashapp.callback(
        [
            Output('start-btn','style'),
            Output('stop-btn','style'), 
   #         Output('mode-select-btn','value')       
        ],    
        Input('interval-component', 'n_intervals')
    )
    def update_start_stop_btn_style(n):
        mode_labels = {
            Mode.MANUAL: "Manual",
            Mode.TEMPERATURE_TRACKING: "Temperature tracking",
            Mode.SCANNING: "Scanning"
        }
        mode = aci.getMode()
        mode_text = "(undefined)"
        if mode in mode_labels.keys():
            mode_text = "Mode: " + mode_labels[mode]
        
        if aci.isRunning():
            return [start_btn_on_style, stop_btn_off_style]   #, mode_text]
        else:
            return [start_btn_off_style, stop_btn_on_style]   #, mode_text]
        
      
        

# DO USUNIECIA        
    # @dashapp.callback(
        # Output('btns-color', 'data'),
        # [
            # Input('stop-btn', 'n_clicks'),
            # Input('start-btn', 'n_clicks'),
        # ],
        # [
            # State('btns-color', 'data'),
            # State('mode-btn-hg', 'data'),
            # State("cfg-mode-store", "data"),
        # ],
    # )
    # def start_stop_btn(n_clicks_stp, n_clicks_str, data, data_mode, cfg_mode):
        # if LOG_INPUT_PARAM_ON:
            # print("[CALLBACK]start_stop_btn [m`ode-btn-hg, cfg-mode-store]: ", data_mode, cfg_mode)

        # # callback context sluzy do sprawdzenia czy callback wywolany jest podczas inicjalizacji
        # ctx = dash.callback_context
        # # Odczytanie stanu czy pomiar jest dokonywany
        # measurement_status = Global_DataBase.read_last_record(MeasSettings).get_state()

        # # If obslugujacy callback przy zaladowaniu strony
        # if ctx.triggered[0]['value'] == None:
            # # jesli pomiar nie jest wystartowany, ustaw odpowiedni kolor
            # if MEASUREMENT_FREE == measurement_status:
                # data['start-btn-style'] = start_btn_off_style
                # data['stop-btn-style'] = stop_btn_on_style

            # # case dla pomiaru ktory jest dokonywany, kolor ma wskazywac ze pomiar jest pobierany
            # else:
                # data['start-btn-style']=start_btn_on_style
                # data['stop-btn-style'] = stop_btn_off_style

        # elif ctx.triggered[0]['prop_id'] == 'stop-btn.n_clicks':
            # # Btn zostal wcisniety przez uzytkownika
  # #      if MEASUREMENT_FREE == measurement_status:           # ten warunek jest dla mnie niezrozumiały
  # #          data['stop-btn-style'] = stop_btn_on_style
  # #      elif MEASUREMENT_ONGOING == measurement_status:      # ten też jest niezrozumiały; skoro było kliknięcie w STOP, to należy je przeprocesować.
            # # Zapis do bazy danych - zatrzymanie pomiaru
            # Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_STOP)
            # data['start-btn-style'] = start_btn_off_style
            # data['stop-btn-style'] = stop_btn_on_style
                
        # elif ctx.triggered[0]['prop_id'] == 'start-btn.n_clicks':
            # cfg_to_store = []
            # # Btn zostal wcisniety przez uzytkownika
            # if MEASUREMENT_FREE == measurement_status:
                # # Zapis  do bazy danych zaczecie pomiaru
                # Global_DataBase.update_setting(MeasSettings, MeasSettings.state, MEASUREMENT_START)
                # # Ustawienie odpowiednich kolorow dla przyciskow w celu informowania czy pomiar odbywa sie w danej chwili
                # data['start-btn-style'] = start_btn_on_style
                # data['stop-btn-style'] = stop_btn_off_style

                # if mode_btns_id[MANUAL_MODE] == data_mode:
                    # # dodanie mode 0 reprezentujacego tracking mode
                    # cfg_to_store.append(MANUAL_MODE)
                    
                    # for key, value in cfg_mode['cur_fix_meas_setting'].items():
                        # if key != "turn_on":
                            # cfg_to_store.append((key,value))
                    
                # elif mode_btns_id[P_TRACKING_MODE] == data_mode:
                    # # dodanie mode 1 reprezentujacego tracking mode
                    # cfg_to_store.append(P_TRACKING_MODE)

                    # for key, value in cfg_mode['cur_track_meas_setting'].items():
                        # if key != "turn_on":
                            # cfg_to_store.append((key,value))
                
                # elif mode_btns_id[PF_TRACKING_MODE] == data_mode:
                    # # dodanie mode 2 reprezentujacego tracking mode
                    # cfg_to_store.append(PF_TRACKING_MODE)

                    # for key, value in cfg_mode['cur_sweep_meas_setting'].items():
                        # if key != "turn_on":
                            # cfg_to_store.append((key,value))
                # elif mode_btns_id[T_TRACKING_MODE] == data_mode:
                    # cfg_to_store.append(T_TRACKING_MODE)
                    # print("==== TRACKING START PRESSED")
                # else:
                    # raise Exception("Error in start_stop_btn fnc")

                # cfg_to_store.append(MEASUREMENT_START)

                # # zapisujemy do bazy danych configuracje dla wybranego trybu
                # if LOG_DB_ON:
                    # print("[CALLBACK] start_stop_btn read cfg from the form: ",cfg_to_store)

                # Global_DataBase.configure_measurement(cfg_to_store)
                # Global_DataBase.create_MeasurementInfo("badanie {}".format(datetime.datetime.now()), datetime.datetime.now())

            # else:
                # #TODO: rozwazyc opcje dla manualu, nadpisanie parametru
                # dash.no_update

        # return data
    
    
    
    
    # Włącz / wyłącz okienka wyboru trybu pracy
    @dashapp.callback(
        [Output('dialog-mode-selector', 'style'), Output('mode-selector', 'value')
        ],
        [Input('mode-select-btn', 'n_clicks'),
        Input('dialog-mode-selector-close-btn', 'n_clicks')],
        [State('dialog-mode-selector', "style")],
    )
    def mode_select_btn(n_clicks, n_clicks_2, dms_style):
        mode = aci.getMode().value
        if n_clicks is None and n_clicks_2 is None:
            return [{'display':'none'}, mode]    # aby poprawnie zachowywało się Open mode controls po pierwszym załadowaniu aplikacji

        if n_clicks>0 or n_clicks_2>0:
            if dms_style["display"]=="none":
                return [{'display':'block'}, mode]    
            else:
                return [{'display':'none'}, mode]


    # zmiana trybu pracy
    @dashapp.callback(
        Output('hidden-div', 'children'),
        Input('mode-selector', 'value')
    )
    def mode_selector(mode):
        mode_types = {
            'manual': Mode.MANUAL,
            't-tracking': Mode.TEMPERATURE_TRACKING,
            'scanning': Mode.SCANNING
        }
        assert mode in mode_types.keys(), "Unknown mode type"
        aci.setMode(mode_types[mode])
 
    
    
    # Otwiera i zamyka okienko konfiguracji wybranego wcześniej trybu pracy
    @dashapp.callback(
        [Output('manual-mode-controls', 'style'), Output('dialog-form-t-tracking', 'style')],  #, Output('t-tracking-mode-controls', 'style'), Output('scanning-mode-controls', 'style')]
        [Input('config-open-btn', 'n_clicks'), Input('close-manual-mode-controls-btn', 'n_clicks'), Input('close-t-tracking-mode-controls-btn', 'n_clicks')], # DOPISAĆ POZOSTAŁE INPUTY ZAMYKAJĄCE
        [State('mode-selector', 'value'), State('t-tracking-table', 'data')]
    )
    def open_close_mode_controls_btn(open_clicks, close_manual_clicks, close_t_tracking_clicks, mode_selector_value, rows):
        mode_controls = {
            'manual': [{'display':'block'}, {'display':'none'}],
            't-tracking': [{'display':'none'}, {'display':'block'}],
            'scanning': [{'display':'none'}, {'display':'none'}]
        }
        
        show_no_ctrl_panels = [{'display':'none'}, {'display':'none'}]
        
        if has_triggered('config-open-btn') and mode_selector_value in mode_controls.keys():
            print("###########################", mode_selector_value)
            return mode_controls[mode_selector_value]
        
        if has_triggered('close-t-tracking-mode-controls-btn'):
            save_table_for_uwave(rows)
        
        return show_no_ctrl_panels
    
    
    # Załadowanie z pliku zawartości tabeli dla trybu temperature-tracking
    @dashapp.callback(
        Output('tt-table-div', 'children'),
        Input('config-open-btn', 'n_clicks'),
        State('mode-selector', 'value'))
    def t_tracking_load_table(n_clicks, mode_selector_value):
        if n_clicks is not None and mode_selector_value == 't-tracking':
            return tt_table(data=load_table_from_uwave())
        else:
            return tt_table(data=[])    


    # Dodanie wiersza w tabeli dla trybu temperatur-tracking
    @dashapp.callback(
        Output('t-tracking-table', 'data'),
        Input('tt-add-row-btn', 'n_clicks'),
        State('t-tracking-table', 'data'),
        State('t-tracking-table', 'columns'))
    def t_tracking_add_row(n_clicks, rows, columns):
        if n_clicks > 0 and has_triggered('tt-add-row-btn'):
            rows.append({c['id']: '' for c in columns})
        return rows

   
# DO USUNIECIA   
    # @dashapp.callback(
        # [Output(mode_id, 'style' ) for mode_id in mode_btns_id],
        # [Input('mode-btn-hg', 'data')],
    # )
    # def highlight_mode_btn(data):
        # # default value dla: tryb bez zaznaczonego moda
        # retArr = [{'border':'none'}, {'border':'none'}, {'border':'none'}, {'border':'none'}]

        # # W store przechowywana dana z nazwa btn ktory ma zostac podswietlony, sprawdzamy w tablicy pozycje i edytujemy dla niego styl w zwracanej wartosci
        # retArr[mode_btns_id.index(data)] = mode_btns_on_style
        # return retArr

# Podswietlane ramki - kandydat do usuniecia
    # @dashapp.callback(
        # Output('mode-btn-hg', 'data'),
        # [Input(mode_id, 'n_clicks' ) for mode_id in mode_btns_id],
        # [State('mode-btn-hg', 'data')],
    # )
    # def mode_btn(manual, p_track, pf_track, t_track, data):
        # ctx = dash.callback_context

        # # Odczytanie stanu czy pomiar jest dokonywany
        # measurement_status = Global_DataBase.read_last_record(MeasSettings).get_state()
        
        # # Init seq
        # if ctx.triggered[0]['value'] == None:
            # if MEASUREMENT_FREE == measurement_status:
                # data = mode_btns_id[MANUAL_MODE]
            # else:
                # meas_mode = Global_DataBase.read_last_record(MeasSettings).get_mode()
                # if MANUAL_MODE == meas_mode:
                    # data = mode_btns_id[MANUAL_MODE]
                # elif P_TRACKING_MODE == meas_mode:
                   # data = mode_btns_id[P_TRACKING_MODE]
                # elif PF_TRACKING_MODE == meas_mode:
                    # data = mode_btns_id[PF_TRACKING_MODE]
                # elif T_TRACKING_MODE == meas_mode:
                    # data = mode_btns_id[T_TRACKING_MODE]
                # else:
                    # raise Exception("Wrong measurement mode")
        # # Seq po wcisnieciu przycisku mode
        # else:
            # if ctx.triggered[0]['prop_id'] == 'manual-mode-btn.n_clicks':
                # data = mode_btns_id[MANUAL_MODE]
            # elif ctx.triggered[0]['prop_id'] == 'p-track-mode-btn.n_clicks':
                # data = mode_btns_id[P_TRACKING_MODE]
            # elif ctx.triggered[0]['prop_id'] == 'pf-track-mode-btn.n_clicks':
                # data = mode_btns_id[PF_TRACKING_MODE]
            # elif ctx.triggered[0]['prop_id'] == 't-track-mode-btn.n_clicks':
                # data = mode_btns_id[T_TRACKING_MODE]
            # else:
                # raise Exception("Fail in mode_btn fnc")
  
        # return data
     
    # Funkcja obslugujace przyciski do ustawiania czestotliwosci
    @dashapp.callback(
        [
            Output('freq_input', 'value'),
            Output('freq-input-val', 'data'),
        ],
        [
            Input('freq-inc-btn', 'n_clicks'),
            Input('freq-dec-btn', 'n_clicks'),
            Input("cfg-mode-store", "data"),
        ],
        [
            State('freq-input-val', 'data'),
        ],
    )
    def inc_dec_freq(inc_freq_clicked, dec_freq_clicked, settings, current_freq):
        triggered_by = dash.callback_context.triggered[0]['prop_id']
        triggered_value = dash.callback_context.triggered[0]['value']
        retValue = current_freq
        # Init seq
        if triggered_value == None:
            pass
        elif triggered_by == 'cfg-mode-store.data':
            for mode in ['cur_fix_meas_setting', 'cur_track_meas_setting', 'cur_sweep_meas_setting']:
                isTurnOn = triggered_value[mode]['turn_on'] 
                if isTurnOn:
                    retValue = settings[mode]['start_freq']
        # Service seq
        else:
            if triggered_by == 'freq-inc-btn.n_clicks':
                setValue = current_freq + 10      # click -> +10 MHz frequency step
                resp = pai.request(PRSynthFreq(setValue * 1e6))
                retValue = resp.frequency / 1e6
            elif triggered_by == 'freq-dec-btn.n_clicks':
                setValue = current_freq - 10      # click -> +10 MHz frequency step
                resp = pai.request(PRSynthFreq(setValue * 1e6))
                retValue = resp.frequency / 1e6
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
                setValue = current_pwr + 1            # click -> +1 dB attenuator step
                resp = pai.request(PRAttenuator(setValue))
                retValue = resp.attenuation
            elif triggered_by == 'power-dec-btn.n_clicks':
                setValue = current_pwr - 1            # click -> -1 dB attenuator step
                resp = pai.request(PRAttenuator(setValue))
                retValue = resp.attenuation
            else:
                raise Exception("Error in inc_dec_pwr fnc")
        return [int(retValue), int(retValue)]





    # Callback obslugujacy odczyt kazdego z sensorow za pomoca tablicy zawierajacej wskaznik na funkcje do ich odczytu
    @dashapp.callback(
        [Output((label_indicator_id+"value"), 'children') for label_indicator_id in OUTPUT_INDICATORS.keys()],
        [Input('interval-component', 'n_intervals'),]
    )
    def update_sensors_output(refresh):
        retArr = []

        for indicator in OUTPUT_INDICATORS.keys():
            retArr.append(OUTPUT_INDICATORS_FNC[indicator]())

        return retArr
        

    # Callback wyswietlajacy formularz dla danego typu
#    @dashapp.callback(
#        [
#            Output('dialog-form-fix', 'style'),
#            Output('dialog-form-p-tracking', 'style'),
#            Output('dialog-form-pf-tracking', 'style'),
#            Output('dialog-form-t-tracking', 'style')
#        ],
#        [
#            Input('manual-mode-btn', 'n_clicks' ),
#            Input('p-track-mode-btn', 'n_clicks' ),
#            Input('pf-track-mode-btn', 'n_clicks' ),
#            Input('t-track-mode-btn', 'n_clicks' ),
#            Input('accept-btn-fix', 'n_clicks'),
#            Input('accept-btn-p', 'n_clicks'),
#            Input('accept-btn-pf', 'n_clicks'),
#            Input('accept-btn-t', 'n_clicks')
#        ],
#    )
#    def diag_box_on_off(fix_btn, p_btn, pf_btn, t_btn, accept_btn_f, accept_btn_p, accept_btn_pf, accept_btn_t):
#        style = [ dash.no_update, dash.no_update, dash.no_update, dash.no_update ]
#
#        triggered_by = dash.callback_context.triggered[0]['prop_id']
#
#        if triggered_by == 'manual-mode-btn.n_clicks':
#            style = [ {'display':'block'}, dash.no_update, dash.no_update, dash.no_update ]
#        elif triggered_by == 'p-track-mode-btn.n_clicks':
#            style = [ dash.no_update, {'display':'block'}, dash.no_update, dash.no_update]
#        elif triggered_by == 'pf-track-mode-btn.n_clicks':
#            style = [ dash.no_update, dash.no_update, {'display':'block'}, dash.no_update ]
#        elif triggered_by == 't-track-mode-btn.n_clicks':
#            style = [ dash.no_update, dash.no_update, dash.no_update, {'display':'block'} ]
#        else:
#            style = [ {'display':'none'}, {'display':'none'}, {'display':'none'}, {'display':'none'} ]   # chowanie paneli
#
#        return style
    
    # Odczyty temperatury z linijki sensorów IR
    @dashapp.callback(
        [ Output('mlx-sensor-0', 'value'),
          Output('mlx-sensor-1', 'value'),
          Output('mlx-sensor-2', 'value'),
          Output('mlx-sensor-3', 'value'),
          Output('mlx-sensor-4', 'value'),
          Output('thermometer-indicator', 'value'),
          Output('led-timer', 'value')
        ],  
        Input('interval-component', 'n_intervals')
    )
    def update_mlx_sensors(value):
        values = []
        for i in range(len(mlxSensorArrayInstance)):
            temps = mlxSensorArrayInstance[i]
            v = temps["object"]
            values.append(str(v))
        values.append(mlxSensorArrayInstance.get_averaged_temperature())
        values.append(aci.getProcessTimeStr())
        return values


    # Pilnowanie, czy aplikacja uwave jest uruchomiona w tle i jeśli nie jest, to jej uruchamianie
    @dashapp.callback(
        Output('uwave_status_txt','children'),
        Input('interval-component', 'n_intervals')
    )
    def update_uwave_status(value):
        UWAVE_PROCESS_NAME = "uwave"
        if checkIfUwaveIsRunning():
            return "RUNNING"
        else:
            # start process
            startUwaveProcess()
            if checkIfUwaveIsRunning():
                return "process started"
            else:
                return "STOPPED"
        



# ten button zmienił ID
#    @dashapp.callback(
#        Output('hidden-div', 'children'),
#        Input('accept-btn-t', 'n_clicks'),
#        State('t-tracking-table', 'data') )
#    def t_tracking_save_table(n_clicks, rows):
#        if n_clicks is not None and n_clicks > 0:
#            save_table_for_uwave(rows)
#        return None
    


    
# DO USUNIECIA
    
    # @dashapp.callback(
        # Output("cfg-mode-store", "data"),
        # [
            # Input('dialog-form-fix', 'children'),
            # Input('dialog-form-p-tracking', 'children'),
            # Input('dialog-form-pf-tracking', 'children'),
            # Input('accept-btn-fix', 'n_clicks'),
            # Input('accept-btn-p', 'n_clicks'),
            # Input('accept-btn-pf', 'n_clicks'),
            # Input('close-t-tracking-mode-controls-btn', 'n_clicks'),              # ten button zmienił ID
            # Input('dialog-form-t-tracking', 'children'),
        # ],
        # State("cfg-mode-store", "data"),
    # )
    # def store_measurment_settings(form_fix, form_p_track, form_pf_track, acc_btn_fix, acc_btn_p, acc_btn_pf, acc_btn_t, form_t_track, cfg_mode):
        # if LOG_CALL_SEQUENCE:
            # print("[CALLBACK] store_measurment_settings ")
            
        # retVal, config_from_form = cfg_mode, []
        # state_measurement = Global_DataBase.read_table(MeasSettings)
        # triggered_by = dash.callback_context.triggered[0]

        # if None == triggered_by['value']:
            # retVal = dash.no_update
        # else:
            # # sprawdz czy mozna zaczac nowy pomiar
            # if state_measurement.get_state() in [None, MEASUREMENT_FREE]:
                # temp_dict = {}

                # if triggered_by['prop_id'] == 'accept-btn-fix.n_clicks':
                    # config_from_form = unpack_html_element(form_fix)

                    # temp_dict.update({
                        # "turn_on": True,
                        # "start_freq": config_from_form[0][1],
                        # "power":config_from_form[1][1],
                        # "time_step":config_from_form[2][1],})

                    # cfg_mode['cur_fix_meas_setting'] = temp_dict

                    # cfg_mode['cur_track_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_sweep_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_temp_tracking_settings']['turn_on'] = False
                    
                # elif triggered_by['prop_id'] == 'accept-btn-p.n_clicks':
                    # config_from_form = unpack_html_element(form_p_track)

                    # temp_dict.update({
                        # "turn_on": True,
                        # "start_freq": config_from_form[0][1],
                        # "stop_freq":config_from_form[1][1],
                        # "power_min":config_from_form[2][1],
                        # "power_max":config_from_form[3][1],
                        # "time_step":config_from_form[4][1],
                        # })

                    # cfg_mode['cur_track_meas_setting'] = temp_dict

                    # cfg_mode['cur_fix_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_sweep_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_temp_tracking_settings']['turn_on'] = False
                    
                # elif triggered_by['prop_id'] == 'accept-btn-pf.n_clicks':
                    # config_from_form = unpack_html_element(form_pf_track)

                    # temp_dict.update({
                        # "turn_on": True,
                        # "start_freq": config_from_form[0][1],
                        # "stop_freq":config_from_form[1][1],
                        # "power_min":config_from_form[2][1],
                        # "power_max":config_from_form[3][1],
                        # "time_step":config_from_form[4][1],
                    # })

                    # cfg_mode['cur_sweep_meas_setting'] = temp_dict

                    # cfg_mode['cur_fix_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_track_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_temp_tracking_settings']['turn_on'] = False
                    
                # elif triggered_by['prop_id'] == 'close-t-tracking-mode-controls-btn.n_clicks':
                # #    config_from_form = unpack_html_element(form_t_track)
                    
                    # temp_dict = {
                        # "turn_on": True,
                        # "time_step": 1     # TU JEST BŁĄD config_from_form[1]
                    
                    # }
                    
                    # cfg_mode['cur_temp_tracking_settings'] = temp_dict
                    
                    # cfg_mode['cur_fix_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_track_meas_setting']['turn_on'] = False
                    # cfg_mode['cur_sweep_meas_setting']['turn_on'] = False                    
                    
                # else:
                    # raise Exception("Fail in store_measurment_settings fnc")

            # else:
                # # TODO : komunikat ze trwa aktualnie pomiar
                # pass

        # retVal = cfg_mode

        # return retVal


#DO USUNIECIA
    # @dashapp.callback(
        # [
            # Output(el, 'value') for el in FORM_INPUT_ID_ARR
        # ],
        # [
            # Input('freq_input', 'value'),
            # Input('power_input', 'value'),
        # ],
    # )
    # def update_freq_input_store(freq_in, pwr_in):
        # return [freq_in, pwr_in]

    
    # Przełączanie panelu bocznego pomiędzy Statusem a konfiguracją wykresu
    @dashapp.callback(
        [
            Output("output-panel", "style"),
            Output("graph-cfg-panel", "style")
        ],
        [
            Input("graph-cfg-btn", "n_clicks")
        ],
        [
            State("output-panel", "style"),
            State("graph-cfg-panel", "style")
        ]
    )
    def show_graph_cfg_panel(n_clicks, op_style, gc_style):
        if n_clicks is not None:
            if op_style["display"]=="none":
                return [{"display":"block"}, {"display":"none"}]
            else:
                return [{"display":"none"}, {"display":"block"}]


    # Pobieranie danych z wykresu w formie pliku CSV
    @dashapp.callback(
        Output("download-traces", "data"),
        Input("download-traces-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def download_traces(n_clicks):
        return dict(content=msi.getTracesAsCsv(), filename=msi.getResultsFileName()+".csv")


    # Aktualizacja wykresu co sekundę
    @dashapp.callback(
        Output('control-chart-live', 'figure'),
        [
            Input('interval-component', 'n_intervals'),
            Input({"type":"graph-trace-switch", "key": ALL}, "on")
        ]
        )
    def update_graph_live(n, trace_switch_list):
        x_ax, y_ax = list(), list()
        retFig = dash.no_update
        
        if aci.isRunning() or "graph-trace-switch" in ctx.triggered[0]['prop_id']:   # drugi warunek dla zaktualizowania wykresu po klikaniu w przełączniki poszczególnych krzywych

            legend_switch = trace_switch_list[-2]   # hardcoded for simplicity

            tracesList = list()
            if msi.isFrequencyDomain:
                x_data = msi.getTrace(MHZ_KEY)
            else:
                x_data = msi.getTrace(TIME_KEY)

            print(trace_switch_list)
            for i, stl in enumerate(switch_traces):
                print(i, stl)
                if trace_switch_list[i]:
                    for st in stl:
                        trace = {
                            "x": x_data,
                            "y": msi.getTrace(st["key"]),
                            "mode": "lines+markers",
                            'type': 'scatter',
                            'line': {'color':st['color']},
                            "name": st["label"],
                        }
                        tracesList.append(trace)

            fig={
                    "data": tracesList,
                    "layout": {
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)",
                        "xaxis": dict(
                            showline=True, showgrid=True, zeroline=False, gridcolor="#333", ticklabelstep=2, ticklen=3, tickformat="%H:%M:%S"
                        ),
                        "yaxis": dict(
                            showline=True, showgrid=True, zeroline=True, gridcolor="#333", dtick=5, nticks=10, ticklabelstep=1, ticklen=3, tickmode="auto"
                        ),
                        "autosize": True,
                        "font": {
                            "color": "#ddd",
                            "size": 16
                        },
                        "margin" : {
                            "b": 40,
                            "l": 25,
                            "t": 15,
                            "r": 5
                        },
                        "showlegend": legend_switch
                    },
                }

            return fig
     #   else:
            # triggered_by = dash.callback_context.triggered[0]
            
            # if None == triggered_by['value']:
                # last_measurement = Global_DataBase.read_last_record(MeasurementInfo)
                # results_table = Global_DataBase.read_filtered_table(last_measurement.get_time_scope())
               
                # x_ax = [ el.get_data_meas() for el in results_table]

                # y_ax.append([ el.get_meas_pwr() for el in results_table])
                # y_ax.append([ el.get_trans_pwr() for el in results_table])

                # return generate_graph( x_ax, y_ax, "stub")
            
            # else:
               # retFig =  dash.no_update

        return retFig

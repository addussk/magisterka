import time, datetime, random
from scripts import dummy_val_tracking, dummy_val_tracking_received_pwr
from defines import *
import threading
from dashApp.models import Results, FrontEndInfo, MeasSettings, MeasurementInfo, Temperature
from drivers import LTDZ, DS1820, ADC_driver, PowerSupply

class DataBase(object):
   ptr_to_database = None

   def __init__(self, ptr) -> None:
      self.ptr_to_database = ptr

   def set_database_ptr(self, ptr):
      self.ptr_to_database = ptr

   def get_database_ptr(self):
      return self.ptr_to_database

   # funkcja do ustawienia parametrow pomiarow
   def configure_measurement(self, parm):
      if LOG_INPUT_PARAM_ON:
         print("[DB] Function: configure_measurement input param: ", parm)

      # FIXED MODE 
      if parm[0] == 0:
         # aktualnie UI zawiera formularz ktory pozwala na wpisanie czest, mocy i kroku czasu. TODO: Dopytac czy potrzeba dla fix moda zakres mocy
         self.update_setting(MeasSettings, MeasSettings.mode, parm[0])
         self.update_setting(MeasSettings, MeasSettings.start_freq, parm[1][1])
         self.update_setting(MeasSettings, MeasSettings.power_min, parm[2][1])
         self.update_setting(MeasSettings, MeasSettings.power_max, parm[2][1])
         self.update_setting(MeasSettings, MeasSettings.time_step, parm[3][1])
         self.update_setting(MeasSettings, MeasSettings.state, parm[4])

      # TRACKING MODE 
      if parm[0] == 1:
         self.update_setting(MeasSettings, MeasSettings.mode, parm[0])
         self.update_setting(MeasSettings, MeasSettings.start_freq, parm[1][1])
         self.update_setting(MeasSettings, MeasSettings.stop_freq, parm[2][1])
         self.update_setting(MeasSettings, MeasSettings.power_min, parm[3][1])
         self.update_setting(MeasSettings, MeasSettings.power_max, parm[4][1])
         self.update_setting(MeasSettings, MeasSettings.time_step, parm[5][1])
         self.update_setting(MeasSettings, MeasSettings.state, parm[6])
      
      # SWEEPING MODE
      if parm[0] == 2:
         self.update_setting(MeasSettings, MeasSettings.mode, parm[0])
         self.update_setting(MeasSettings, MeasSettings.start_freq, parm[1][1])
         self.update_setting(MeasSettings, MeasSettings.stop_freq, parm[2][1])
         self.update_setting(MeasSettings, MeasSettings.power_min, parm[3][1])
         self.update_setting(MeasSettings, MeasSettings.power_max, parm[4][1])
         self.update_setting(MeasSettings, MeasSettings.time_step, parm[5][1])
         self.update_setting(MeasSettings, MeasSettings.state, parm[6])

   def read_record_all(self, typeTable):
      return self.ptr_to_database.session.query(typeTable).order_by(typeTable.id).all()

   # funkcja odczytuje dany rzad w wskazanej tablicy
   def read_specific_row(self, typeTable, numRow):
      for el in self.read_record_all(typeTable):
         if el.get_id() == numRow:
            return el
      return None

   # Funkcja odczytujaca podana ilosc rekordow w podanej tabeli
   def read_last_records(self, type, nmb_of_rec):
      return self.ptr_to_database.session.query(type).order_by(type.id.desc()).limit(nmb_of_rec).all()
   
   def read_last_record(self, typeTable):
      return self.ptr_to_database.session.query(typeTable).order_by(typeTable.id.desc()).first()

   def read_table(self, typeTable):
      return self.ptr_to_database.session.query(typeTable).order_by(typeTable.id).first()

   def read_filtered_table(self, timeScope):
      table = self.ptr_to_database.session.query(Results).filter( (Results.time_of_measurement >= timeScope[0]) & (Results.time_of_measurement <= timeScope[1])).all()
      return table
   
   def read_filtered_table_live(self, timeScope):
      table = self.ptr_to_database.session.query(Results).filter( (Results.time_of_measurement >= timeScope[0]) ).all()
      return table
   
   def read_record(self, typeTable, typeKey):
      record = self.ptr_to_database.session.query(typeTable).order_by(typeTable.id).first()
      return record.get(typeKey)

   def read_recent_slider_val(self):
      return (self.ptr_to_database.session.query(FrontEndInfo).order_by(FrontEndInfo.id).first()).get_slider()
   
   def write_to_database_FrontEndInfo(self, sliderVal=2500, toolStatus=False):
      self.ptr_to_database.session.add(FrontEndInfo(slider_val=sliderVal, tool_status=toolStatus))
      self.ptr_to_database.session.commit()
   
   def write_to_database_Results(self, freq, pwr_transmitted, pwr_received):
      tim=datetime.datetime.now()
      self.ptr_to_database.session.add(Results(measured_freq=freq, measured_power=pwr_received,transmited_power=pwr_transmitted, time_of_measurement=tim))
      self.ptr_to_database.session.commit()

   def create_table_Results(self, freq=17, power=1, tim=datetime.datetime.now()):
      self.ptr_to_database.session.add(Results(measured_freq=freq, measured_power=power,transmited_power=power, time_of_measurement=tim))
      self.ptr_to_database.session.commit()

   # Funkcja do utworzenia record w tablicy MeasSettings przechowujacej ustawienie pomiaru
   def create_MeasSettings(self, choosenMode=0, measStatus=MEASUREMENT_FREE, startFreq=2400, stopFreq=2400, pwr_min=1, pwr_max=13, fStep=1, tStep=5):
      self.ptr_to_database.session.add(MeasSettings(mode=choosenMode, state=measStatus, start_freq=startFreq, stop_freq=stopFreq, power_min=pwr_min, power_max=pwr_max, freq_step=fStep, time_step=tStep))
      self.ptr_to_database.session.commit()

   def create_MeasurementInfo(self, name="init", b_date=datetime.datetime.now(), f_date=datetime.datetime.now()):
      self.ptr_to_database.session.add(MeasurementInfo(name=name, beginning=b_date, finish=f_date))
      self.ptr_to_database.session.commit()

   # Funkcja odpowiedzialna za aktualizacje konkretnej pozycji w wskazanym rekordzie
   def update_setting(self, typeTable, typeKey, val):
      self.ptr_to_database.session.query(typeTable).filter(typeTable.id==1).update({typeKey: val})
      self.ptr_to_database.session.commit()
   
   # Funkcja aktualizuje dana kolumne w wskazanej tablicy ostatnio dodanego rekordu
   def update_last_record(self, typeTable, typeKey, val):
      self.ptr_to_database.session.query(typeTable).order_by(typeTable.id.desc()).first().update(typeKey, val)
      self.ptr_to_database.session.commit()

   # Funkcja sluzaca do aktualizacji informacji dotyczacych calibracji
   def update_calib_info(self, calibState, attVal):
      table = self.read_table(FrontEndInfo)
      table.change_calib_status(calibState)
      table.set_attenuation(attVal)
      self.ptr_to_database.session.commit()

class State(DataBase):

   name = "state"
   allowed = []

   def switch(self, state, ptr_to_db):
      """ Switch to new state """
      if state.name in self.allowed:
         print('Current:',self,' => switched to new state',state.name)
         self.__class__ = state
         state.__init__(self, ptr_to_db)
      else:
         print('Current:',self,' => switching to',state.name,'not possible.')

   def __str__(self):
      return self.name
   
   def print_state(self):
      print("Current State: {}".format(self.name))

class Init(State):
   name = "init"
   allowed = ['calibration', 'idle']
   status = None

   def __init__(self, ptrToDB) -> None:
      print("Init Instance")
      self.status = False
      self.set_database_ptr(ptrToDB)

   def initialization(self):

      self.db_init()
      print("TODO: initialization things")
      self.update_setting(FrontEndInfo,FrontEndInfo.tool_status, True)
      print("Initialization completed")
      self.status = True
   
   def isInitialized(self):
      return self.status

   def db_init(self):
      try:
         front_table = self.read_record_all(FrontEndInfo)
         front_table[0].set_default()
      except :
         self.write_to_database_FrontEndInfo()

      try:
         meassett_table = self.read_record_all(MeasSettings)
         meassett_table[0].set_default()
      except:
         self.create_MeasSettings()
      
      try:
         measurementInfo = self.read_record_all(MeasurementInfo)
         if measurementInfo == []:
            # przejdz do obslugi wyjatku
            raise Exception
         else:
            # nie rob nic, tablica zawiera dane
            pass
      except:
         self.create_MeasurementInfo()

      # Sprawdz czy istnieje rekord w Frequqncy, jesli nie, utworz, jesli istnieje
      if len(self.read_record_all(Results)) == 0:
         self.create_table_Results()
      else:
         # dla czestotliwosci nie jest potrzebne wprowadzanie zadnej wartosci
         pass
      
class Calibration(State):
   name = "calibration"
   allowed = ["idle"]
   status = False
   
   def calibration(self):
      print("TODO: calibration stuff")
      time.sleep(1)
      print("Calibration completed")
      self.status = COMPLETED
   
class Measurement(State):
   name = "measurement"
   allowed = ['idle']
   MHz = 1000000

   mode = 0
   state = 0
   start_freq = 0
   stop_freq = 0
   power = 0
   time_step = 0
   freq_step = 0
   ptrAdcDriver = None

   def __init__(self, ptr_to_db) -> None:
      if LOG_DB_ON:
         print("[MEASUREMENT] Init phase: Measurement settings: ", self.read_table(MeasSettings).get_all())

      self.update_settings()
      # Ustawienie wierzcholka funkcji kwadratowej posrodku czestotliwosci poczatkowej a koncowej
      temp_mid = (self.stop_freq + self.start_freq)/2
      self.update_setting(FrontEndInfo, FrontEndInfo.slider_val, temp_mid)
      try:
         self.ptrAdcDriver = ADC_driver()
      except:
         print("Warning: ADC is unavailable")
         self.ptrAdcDriver = None

   def managing_measurement(self, type_req, thread_list):
      if LOG_SM_ON:
         print("[MEASUREMENT] managing_measurement type request: ", type_req)
         print("[MEASUREMENT] managing_measurement class members[mode, start_freq, stop_freq]: ", self.mode, self.start_freq, self.stop_freq)
      
      if type_req == MEASUREMENT_START:
         if self.mode == 0:
            thread_list.append(threading.Thread(target=self.fixed__freq_mode))
         elif self.mode == 1:
            thread_list.append(threading.Thread(target=self.tracking_mode))
         elif self.mode == 2:
            thread_list.append(threading.Thread(target=self.sweeping_mode))
         else:
            raise Exception("Problem with creation measurement")

      elif type_req == MEASUREMENT_STOP:
         self.stop_measurement()
         print("task terminated")

      else:
         raise Exception("Problem with handling with measurement")

   def stop_measurement(self):
      print("Stopped measurement")
      self.state = MEASUREMENT_FREE
      try:
         # skonfigurowanie polaczenia z syntezatorem czestotliwosci
         x = LTDZ()
         x.find_device()

         # wylaczenie syntezatora
         x.turn_RF_out_off(x.config_serial())
         x.turn_chip_off(x.config_serial())
      except:
         print("Warning:LTDZ has not been power down")
         pass

   def measure(self, freq, in_power):

      if self.ptrAdcDriver == None:
         print("Watch out! ADC is  unconnected, dummy data will be generated for measurement of received power")
         transmittedPwr = dummy_val_tracking(freq, in_power, self.ptr_to_database)
         receivedPwr = dummy_val_tracking_received_pwr(transmittedPwr)
      else:
         receivedPwr = self.ptrAdcDriver.read_voltage()
         transmittedPwr = self.ptrAdcDriver.read_voltage()+1 # 1 tymczasowa wartosc, na razie mierzona wartosc za pomoca jednego channela. Wartosc dodany by rozroznic dwie wartosci

      self.write_to_database_Results(freq, transmittedPwr, receivedPwr)

      return transmittedPwr

   def sweeping_mode(self):
      print("Sweeping mode")

   def tracking_mode(self):
      print("Tracking mode")

      first_time = True
      scan_freq = self.start_freq
      tmp_power = self.power
      scanning_scope = abs(self.stop_freq - self.start_freq)
      best_result = 0
      slid_val = self.read_recent_slider_val()

      while self.state == MEASUREMENT_START:
         time.sleep(self.time_step)

         if first_time or (slid_val != self.read_recent_slider_val()):
            print("[TRACKING] Fast scanning results: ")
            if slid_val != self.read_recent_slider_val():
               SCANNING_RESULT.clear()

            for iter in range(scanning_scope):
               iter_freq = scan_freq+iter
               received_power = self.measure(iter_freq, tmp_power)
               SCANNING_RESULT.append((received_power, iter_freq))

            if first_time:
               best_result = min(SCANNING_RESULT)
               first_time = False
               self.update_setting(FrontEndInfo, FrontEndInfo.isScanAvalaible, True)

            # przywracanie defaultowych parametrow do kolejnego skanowania
            slid_val = self.read_recent_slider_val()
            scan_freq = self.start_freq

         else:
            print("[TRACKING] Measuring..")

            # Aktualizacja minimum przy zmianie f0
            best_result = (self.measure(best_result[1], tmp_power), best_result[1])
            print(best_result)

            # Krok w gore
            meas_freq = best_result[1] + self.freq_step
            if(meas_freq > self.stop_freq):
                  meas_freq =  best_result[1]

            up_freq_res = (self.measure(meas_freq, tmp_power), meas_freq)

            # Krok w dol
            meas_freq = best_result[1] - 1
            if(meas_freq <= self.start_freq):
               meas_freq = best_result[1]

            less_freq_res = (self.measure(meas_freq, tmp_power), meas_freq)

            print("[TRACKING] Scanning results: {}".format([up_freq_res, less_freq_res, best_result]))
            best_result = min([up_freq_res, less_freq_res, best_result])
            print("[TRACKING] Update the best setting: Freq:{}, R_Power: {}".format(best_result[1], best_result[0]))

            self.ptr_to_database.session.add(Results(measured_freq=best_result[1], measured_power=best_result[0], time_of_measurement=datetime.datetime.now()))
            self.ptr_to_database.session.commit()

            best_result = (best_result[0] + random.random(), best_result[1])
            self.update_setting(MeasSettings, MeasSettings.best_scan_freq, best_result[1])
            self.update_setting(MeasSettings, MeasSettings.best_scan_power, best_result[0])

   def fixed__freq_mode(self):

      try:
         # skonfigurowanie polaczenia z syntezatorem czestotliwosci
         x = LTDZ()
         x.find_device()
      except:
         print("Warning: NO COMMUNICATION with LTDZ")

      try:
         # wlaczenie syntezatora
         print("turn chip")
         x.turn_chip_on(x.config_serial())
         print("turn RF out")
         x.turn_RF_out_on(x.config_serial())
         print("set power:")
         x.set_power(x.config_serial(), self.power)
         print("set freq")
         x.set_freq(x.config_serial(), self.start_freq * self.MHz)
      except:
         print("Warning: LTDZ has not been configured properly")

      while self.state == MEASUREMENT_START:
         print("Fixed measurement")
         time.sleep(self.time_step)

         retVal = self.measure(self.start_freq, self.power)

   def update_settings(self):
      self.mode = self.read_record(MeasSettings, "mode")
      self.state = self.read_record(MeasSettings, "state")
      self.start_freq = self.read_record(MeasSettings, "start_freq")
      self.stop_freq = self.read_record(MeasSettings, "stop_freq")
      self.power_min = self.read_record(MeasSettings, "power_min")
      self.power_max = self.read_record(MeasSettings, "power_max")
      self.freq_step = self.read_record(MeasSettings, "freq_step")
      self.time_step = self.read_record(MeasSettings, "time_step")

class Idle(Measurement):
   """ State of being in hibernation after powered on """
   name = "idle"
   allowed = ['off', 'on', 'measurement']

class Guard(object):
   """ A class representing a guardian """
   status = None
   db = None
   pwrSupplDriver = None
   scheduler = list()
   isInitStatus = False
   isCalibratedStatus = False

   new_settings = {
      "slider_val":2500,
      "tool_status" : False,
      "isScanAvalaible": False,
      "calib_status":False,
   }

   # Przechowuje info nt ostatniego ustawionego pomiaru
   measurement_form = {
      "mode": 0,
      "state": MEASUREMENT_FREE,
      "start_freq": 2400,
      "stop_freq": 2400,
      "power": 10,
      "freq_step": 1,
      "time_step": 5,
   }

   def __init__(self, in_name='Main', database_ptr = None):
      self.name = in_name
      self.pwrSupplDriver = PowerSupply()
      # State of the guard - default is init.
      self.state = Init(database_ptr)
      self.db = DataBase(database_ptr)

   # setter functions
   def set_status(self, status):
      self.status = status

   def set_calib_status(self, status):
      self.isCalibratedStatus = status

   def set_init_status(self, status):
      self.isInitStatus = status

   # getter functions
   def get_status(self):
      return self.state.status

   def isCalibrated(self):
      return self.isCalibratedStatus

   # rest functions
   def change_state(self, state):
      """ Change state """
      self.state.switch(state, self.db.get_database_ptr())

   # funkcja sprawdza czy ustawienia ulegly zmianie - do refactoringu, ulepszyc dodawanie kolejnych ustawien
   def isChangeInSetting(self):
      # rzeczy ktore zawiera baza danych w alchemy
      for key in ["tool_status", "calib_status"]:

         read_record = self.db.read_record(FrontEndInfo, key)
         if read_record == "invalid name":
            raise Exception("Wrong member")

         if read_record != self.new_settings[key]: 
            print("Diff tool_status ", read_record , " ", self.new_settings[key])
            return True
         
      for key in [ "state"]:
         read_record = self.db.read_record(MeasSettings, key)

         if read_record == "invalid name":
            raise Exception("Wrong member")
         
         if read_record != self.measurement_form[key]:
            return True

      return False

   # funkcja dokonuje pomiaru temperatury za pomoca classy DS1820
   def measure_temperature(self):
      if LOG_SENSORS_ON:
         print("Measure temperature...")

      tmpSensor = DS1820()
      read_temp=tmpSensor.read_temp()

      self.db.ptr_to_database.session.add(Temperature(obj_temp=read_temp+5, sys_temp=read_temp, time_of_measurement=datetime.datetime.now()))
      self.db.ptr_to_database.session.commit()
   
   # funkcja sprawdzajaca czy uzytkownik wybral jakas akcje, wybiera krok w state machine
   def choose_step(self):
      if LOG_SM_ON:
         print("[SM] Has the setting been changed?: ", self.isChangeInSetting())
         print("[SM] Calibration status: ", self.db.read_record(FrontEndInfo,"calib_status"))
         print("[SM] Measurement mode in DB: ", self.db.read_record(MeasSettings,"mode"))

      # Jesli nie ma zmiany -> STEP_IDLE
      if (not self.isChangeInSetting()):
         retStep = STEP_IDLE
      # Obsluga zadania 
      else:
         # Odczyt informacji dotyczacych zasilacza ustawionych przez uzytkownika.
         front_info_table = self.db.read_table(FrontEndInfo)

         # Sprawdzenie czy ustawienia ulegly zmianie
         if self.new_settings["tool_status"] != front_info_table.get_tool_status():
            if front_info_table.get_tool_status():
               retStep = STEP_TURN_POWER_ON
            else: retStep = STEP_TURN_POWER_OFF

         # Po wyslaniu zapytania o calibracje, ustaw odpowiedni krok.
         if self.new_settings["calib_status"] != front_info_table.get_calib_status():
            if front_info_table.get_calib_status():
               retStep = STEP_CALIBRATION
            else: retStep = STEP_IDLE

         # Ustawienia pomiarow odczytane z front end'u
         read_mes_set = self.db.read_table(MeasSettings)
         if self.measurement_form["state"] != read_mes_set.get_state():
            retStep = STEP_MEASUREMENT

      return retStep

   def state_machine(self):
      read_mes_set = self.db.read_table(MeasSettings)
      current_step = self.choose_step()

      if LOG_SM_ON:
         print("[SM] Current Step: ", current_step)

      if  current_step == STEP_IDLE:
         print("Nothing change, stay in ", self.state.__class__)
         if self.state.__class__ != Idle and self.state.__class__ != Measurement:
            self.change_state(Idle)

      elif current_step == STEP_TURN_POWER_ON:
         self.pwrSupplDriver.turn_on()
         self.new_settings["tool_status"] = self.pwrSupplDriver.get_current_status()
      
      elif current_step == STEP_TURN_POWER_OFF:
         self.pwrSupplDriver.turn_off()
         self.new_settings["tool_status"] = self.pwrSupplDriver.get_current_status()

      elif current_step == STEP_CALIBRATION:
         # TODO: Dopisac inicjalizacje dla HMC, i ustawianie poprawnej wartosci tlumienia.
         self.db.read_table(FrontEndInfo).change_calib_status(STOP_CALIBRATE)
         self.new_settings["calib_status"] = STOP_CALIBRATE
      
      elif current_step == STEP_MEASUREMENT:
         if LOG_SM_ON:
            print("[SM] MEASUREMENT MODE: ", self.measurement_form)
            
         if read_mes_set.get_state() == MEASUREMENT_START:
            self.change_state(Measurement)
            self.state.managing_measurement(read_mes_set.get_state(), self.scheduler)
            for task in self.scheduler:
               task.start()

            self.measurement_form["state"] = MEASUREMENT_ONGOING
            self.db.update_setting(MeasSettings,MeasSettings.state, MEASUREMENT_ONGOING)

         elif read_mes_set.get_state() == MEASUREMENT_STOP:
            self.scheduler.pop()
            self.db.update_last_record(MeasurementInfo, MeasurementInfo.finish, datetime.datetime.now())
            self.state.managing_measurement(read_mes_set.get_state(), self.scheduler)
            self.db.update_setting(MeasSettings,MeasSettings.state, MEASUREMENT_FREE)
            self.measurement_form["state"] = MEASUREMENT_FREE
            self.db.update_setting(FrontEndInfo, FrontEndInfo.isScanAvalaible, False)
            self.change_state(Idle)

      else:
         if LOG_ON:
            print("UNKNOWN STATE")




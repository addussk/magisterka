import time, datetime, random
from scripts import dummy_val_tracking
from database import *
import threading
from dashApp.models import Frequency, FrontEndInfo, MeasSettings

class DataBase(object):
   ptr_to_database = None

   def __init__(self, ptr) -> None:
      self.ptr_to_database = ptr

   def set_database_ptr(self, ptr):
      self.ptr_to_database = ptr

   def get_database_ptr(self):
      return self.ptr_to_database

   def write_to_database(self, db, sett, val):
      print("CLIENT: Write to DB")
      if sett in db.keys():
         db[sett] = val
      else:
         raise Exception("Key isn't in dictionary")

   def read_from_database(self, db, sett):
      if sett in db.keys():
         return db[sett]
      else:
         raise Exception("Key isn't in dictionary")

   # funkcja do ustawienia parametrow pomiarow
   def configure_measurement(self, parm):
      # FIXED MODE 
      if parm[0] == 0:
         self.update_setting(MeasSettings, MeasSettings.mode, parm[0])
         self.update_setting(MeasSettings, MeasSettings.start_freq, parm[1][1])
         self.update_setting(MeasSettings, MeasSettings.power, parm[2][1])
         self.update_setting(MeasSettings, MeasSettings.time_step, parm[3][1])
         self.update_setting(MeasSettings, MeasSettings.state, parm[4])

      # TRACKING MODE 
      if parm[0] == 1:
         self.update_setting(MeasSettings, MeasSettings.mode, parm[0])
         self.update_setting(MeasSettings, MeasSettings.start_freq, parm[1][1])
         self.update_setting(MeasSettings, MeasSettings.stop_freq, parm[2][1])
         self.update_setting(MeasSettings, MeasSettings.power, parm[3][1])
         self.update_setting(MeasSettings, MeasSettings.freq_step, parm[4][1])
         self.update_setting(MeasSettings, MeasSettings.time_step, parm[5][1])
         self.update_setting(MeasSettings, MeasSettings.state, parm[6])
      
      # SWEEPING MODE - TBD

   # Funkcja odczytujaca podana ilosc rekordow w podanej tabeli
   def read_last_records(self, type, nmb_of_rec):
      return self.ptr_to_database.session.query(type).order_by(type.time_of_measurement.desc()).limit(nmb_of_rec).all()

   def read_table(self, typeTable):
      return self.ptr_to_database.session.query(typeTable).order_by(typeTable.id).first()
   
   def read_record(self, typeTable, typeKey):
      record = self.ptr_to_database.session.query(typeTable).order_by(typeTable.id).first()
      return record.get(typeKey)

   def read_recent_slider_val(self):
      return (self.ptr_to_database.session.query(FrontEndInfo).order_by(FrontEndInfo.id).first()).get_slider()
   
   def write_to_database_FrontEndInfo(self, sliderVal=2500, toolStatus=False):
      self.ptr_to_database.session.add(FrontEndInfo(slider_val=sliderVal, tool_status=toolStatus))
      self.ptr_to_database.session.commit()
   
   def write_to_database_Frequency(self, freq=17, power=1, tim=datetime.datetime.now()):
      self.ptr_to_database.session.add(Frequency(measured_freq=freq, measured_power=power, time_of_measurement=tim))
      self.ptr_to_database.session.commit()

   # Funkcja do utworzenia record w tablicy MeasSettings przechowujacej ustawienie pomiaru
   def create_MeasSettings(self, choosenMode=0, measStatus=MEASUREMENT_FREE, startFreq=2400, stopFreq=2400, pwr=10, fStep=1, tStep=5):
      self.ptr_to_database.session.add(MeasSettings(mode=choosenMode, state=measStatus, start_freq=startFreq, stop_freq=stopFreq, power=pwr, freq_step=fStep, time_step=tStep))
      self.ptr_to_database.session.commit()

   def update_setting(self, typeTable, typeKey, val):
      self.ptr_to_database.session.query(typeTable).filter(typeTable.id==1).update({typeKey: val})
      self.ptr_to_database.session.commit()

      # for row in self.ptr_to_database.session.query(typeTable).all():
      #    print(row.get())

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
      self.write_to_database_FrontEndInfo()
      self.write_to_database_Frequency()
   
   def initialization(self):
      print("TODO: initialization things")

      print("Initialization completed")
      self.status = True
   
   def isInitialized(self):
      return self.status

class Calibration(State):
   name = "calibration"
   allowed = ["idle"]
   status = False
   
   def calibration(self):
      print("TODO: calibration stuff")
      time.sleep(1)
      print("Calibration completed")
      self.status = COMPLETED
   
class Off(State):
   name = "off"
   allowed = ['on', 'idle']

   def turn_off(self):
      print("Turn on process")

class On(State):
   """ State of being powered on and working """
   name = "on"
   allowed = ['off','idle']

   def turn_on(self):
      print("Turn on process")

class Measurement(State):
   name = "measurement"
   allowed = ['idle']

   mode = 0
   state = 0
   start_freq = 0
   stop_freq = 0
   power = 0
   time_step = 0
   freq_step = 0

   def __init__(self, ptr_to_db) -> None:
      self.update_settings()
      # Ustawienie wierzcholka funkcji kwadratowej posrodku czestotliwosci poczatkowej a koncowej
      temp_mid = (self.stop_freq + self.start_freq)/2
      self.update_setting(FrontEndInfo, FrontEndInfo.slider_val, temp_mid)
     
   def managing_measurement(self, type_req, thread_list):
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
   
   def measure(self, freq, in_power):
      retVal = dummy_val_tracking(freq, in_power, self.ptr_to_database)
      return retVal

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
            SCANNING_RESULT.clear()

            for iter in range(scanning_scope):
               iter_freq = scan_freq+iter
               received_power = self.measure(iter_freq, tmp_power)
               SCANNING_RESULT.append((received_power, iter_freq))

            if first_time:
               best_result = min(SCANNING_RESULT)
               first_time = False
               self.write_to_database(DATA_BASE, "isScanAvalaible", True)

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

            self.ptr_to_database.session.add(Frequency(measured_freq=best_result[1], measured_power=best_result[0], time_of_measurement=datetime.datetime.now()))
            self.ptr_to_database.session.commit()

            best_result = (best_result[0] + random.random(), best_result[1])

   def fixed__freq_mode(self):
      while self.state == MEASUREMENT_START:
         print("Fixed measurement")
         time.sleep(self.time_step)

         retVal = self.measure(self.start_freq, self.power)

         self.ptr_to_database.session.add(Frequency(measured_freq=self.start_freq, measured_power=retVal, time_of_measurement=datetime.datetime.now()))
         self.ptr_to_database.session.commit()
         
   def update_settings(self):
      self.mode = self.read_record(MeasSettings, "mode")
      self.state = self.read_record(MeasSettings, "state")
      self.start_freq = self.read_record(MeasSettings, "start_freq")
      self.stop_freq = self.read_record(MeasSettings, "stop_freq")
      self.power = self.read_record(MeasSettings, "power")
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
   scheduler = list()
   
   settings = {
      "init_status": None,
      "calib_status" : False,
      "isScanAvalaible": False,
   }

   new_settings = {
      "slider_val":2500,
      "tool_status" : False,
   }

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
      # State of the guard - default is init.
      self.state = Init(database_ptr)
      self.db = DataBase(database_ptr)
      self.db.create_MeasSettings()
   
   # setter functions
   def set_status(self, status):
      self.status = status
   
   def set_calib_status(self, status):
      self.settings["calib_status"] = status

   # getter functions
   def get_status(self):
      print("Status of {}: ".format(self.state.name))
      return self.state.status

   def isCalibrated(self):
      return self.settings["calib_status"]

   # rest functions
   def change_state(self, state):
      """ Change state """
      self.state.switch(state, self.db.get_database_ptr())
   
   def change_settings(self, key, value):
      if key in self.settings.keys():
         self.settings[key] = value
      else: raise Exception("Key doesn't exist!")

      self.write_to_db(DATA_BASE, self.settings)
   
   # funkcja sprawdza czy ustawienia ulegly zmianie - do refactoringu, ulepszyc dodawanie kolejnych ustawien
   def isChangeInSetting(self):
      # rzeczy ktore zawiera baza danych w alchemy
      for key in ["tool_status"]:

         read_record = self.db.read_record(FrontEndInfo, key)
         if read_record == "invalid name":
            raise Exception("Wrong member")

         if read_record != self.new_settings[key]:
            return True
         
      for key in ["mode", "state"]:
         read_record = self.db.read_record(MeasSettings, key)

         if read_record == "invalid name":
            raise Exception("Wrong member")
         
         if read_record != self.measurement_form[key]:
            return True

      return False

   def check(self):
      read_settings = self.read_db()
      read_mes_set = self.db.read_table(MeasSettings)

      isChanged = self.isChangeInSetting()

      if (read_settings == self.settings) and not isChanged:
         print("Nothing change, stay in ", self.state.__class__)
         if self.state.__class__ != Idle and self.state.__class__ != Measurement:
            self.change_state(Idle)       
      
      else:
         print("Take action")
         #  stworzyc zmienna przechowujaca setup w bazie danych
         state_from_db = read_mes_set.get_state()
         # If settings has been changed, choose requested action
         db_tool_status = self.db.read_record(FrontEndInfo,"tool_status")
         if self.new_settings["tool_status"] != db_tool_status:

            if db_tool_status == True:
               print("ON MODE")
               self.change_state(On)
               self.state.turn_on()
               self.new_settings["tool_status"] = True

            elif db_tool_status == False:
               print("OFF MODE")
               self.change_state(Off)
               self.state.turn_off()
               self.new_settings["tool_status"] = False

            else: raise Exception("Wrong tool status")

         if self.measurement_form["state"] != read_mes_set.get_state():
            print("MEASUREMENT MODE")
            if read_mes_set.get_state() == MEASUREMENT_START:
               self.change_state(Measurement)
               self.state.managing_measurement(read_mes_set.get_state(), self.scheduler)
               for task in self.scheduler:
                  task.start()

               self.measurement_form["state"] = MEASUREMENT_ONGOING
               self.db.update_setting(MeasSettings,MeasSettings.state, MEASUREMENT_ONGOING)
            elif read_mes_set.get_state() == MEASUREMENT_STOP:
               self.change_state(Measurement)
               self.scheduler.pop()
               self.state.managing_measurement(read_mes_set.get_state(), self.scheduler)
               self.db.update_setting(MeasSettings,MeasSettings.state, MEASUREMENT_FREE)
               self.measurement_form["state"] = MEASUREMENT_FREE
               self.change_state(Idle)

   def read_db(self):
      print("Reading database")
      return DATA_BASE

   def write_to_db(self, db, *args):
      print("Write to DB")
      for el in args:
         db.update(el)


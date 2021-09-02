import time, datetime, random
from scripts import dummy_val_tracking
from database import *
import threading
from dashApp.models import Frequency, FrontEndInfo

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

   def read_from_Alchemy(self, table):
      records = self.ptr_to_database.session.query(table).order_by(table.time_of_measurement.desc()).limit(20).all()
      for el in records:
         print(el.get())

   
   def read_recent_slider_val(self):
      return (self.ptr_to_database.session.query(FrontEndInfo).order_by(FrontEndInfo.id.desc()).first()).get_slider()
   
   def write_to_database_FrontEndInfo(self, arg1):
      self.ptr_to_database.session.add(FrontEndInfo(slider_val=arg1))
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

   def __init__(self) -> None:
      print("Init Instance")
      self.status = False
   
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
   allowed = ['on']

   def turn_off(self):
      print("Turn on process")

      return TURN_OFF

class On(State):
   """ State of being powered on and working """
   name = "on"
   allowed = ['off','measurement','idle']

   def turn_on(self):
      print("Turn on process")

      return TURN_ON

class Measurement(State):
   name = "measurement"
   allowed = ['idle']

   meas_status = 0
   mode = 0
   start_freq = 0
   stop_freq = 0
   power = 0
   time_stamp = 0
   reset_tracing_period = 0
   freq_step = 0

   def __init__(self, ptr_to_db) -> None:
      self.update_settings(DATA_BASE)
      
      # Ustawienie wierzcholka funkcji kwadratowej posrodku czestotliwosci poczatkowej a koncowej
      temp_mid = (self.stop_freq + self.start_freq)/2
      self.write_to_database_FrontEndInfo(temp_mid)
     
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
      self.meas_status = MEASUREMENT_FREE
   
   def measure(self, freq, in_power):
      retVal = dummy_val_tracking(freq, in_power, self.ptr_to_database)
      return retVal

   def sweeping_mode(self):
      print("Sweeping mode")
   
   def tracking_mode(self):
      print("Tracking mode")

      first_time = True
      tmp_freq = self.start_freq
      tmp_power = self.power
      scanning_scope = abs(self.stop_freq - self.start_freq)
      best_result = 0
      slid_val = self.read_recent_slider_val()

      while self.meas_status == MEASUREMENT_START:
         time.sleep(self.time_stamp)

         if first_time or (slid_val != self.read_recent_slider_val()):
            print("[TRACKING] Fast scanning results: ")
            SCANNING_RESULT.clear()

            for iter in range(scanning_scope):
               tmp_freq_iter = tmp_freq+iter
               received_power = self.measure(tmp_freq_iter, tmp_power)
               SCANNING_RESULT.append((received_power, tmp_freq_iter))

            if first_time:
               best_result = min(SCANNING_RESULT)
               first_time = False
               self.write_to_database(DATA_BASE, "isScanAvalaible", True)

         else:
            print("[TRACKING] Measuring..")

            # Krok w gore
            tmp_freq = best_result[1] + self.freq_step
            if(tmp_freq > self.stop_freq):
                  tmp_freq =  best_result[1]

            up_freq_res = (self.measure(tmp_freq, tmp_power), tmp_freq) 

            # Krok w dol
            tmp_freq = best_result[1] - 1
            if(tmp_freq <= self.start_freq):
               tmp_freq = best_result[1]

            less_freq_res = (self.measure(tmp_freq, tmp_power), tmp_freq) 

            print("[TRACKING] Scanning results: {}".format([up_freq_res, less_freq_res, best_result]))
            best_result = min([up_freq_res, less_freq_res, best_result])
            print("[TRACKING] Update the best setting: Freq:{}, R_Power: {}".format(best_result[1], best_result[0]))

            self.ptr_to_database.session.add(Frequency(measured_freq=best_result[1], measured_power=best_result[0], time_of_measurement=datetime.datetime.now()))
            self.ptr_to_database.session.commit()

            best_result = (best_result[0] + random.random(), best_result[1])

   def fixed__freq_mode(self):
      while self.meas_status == MEASUREMENT_START:
         print("Fixed measurement")
         time.sleep(self.time_stamp)

         retVal = self.measure(self.start_freq, self.power)

         self.ptr_to_database.session.add(Frequency(measured_freq=self.start_freq, measured_power=retVal, time_of_measurement=datetime.datetime.now()))
         self.ptr_to_database.session.commit()
         
   def update_settings(self, db):
      self.mode = read_from_database(db, "mode")
      self.start_freq = read_from_database(db, "start_freq")
      self.stop_freq = read_from_database(db, "stop_freq")
      self.power = read_from_database(db, "power")
      self.time_stamp = read_from_database(db, "time_stamp")
      self.reset_tracing_period = read_from_database(db, "reset_tracing_period")
      self.meas_status = read_from_database(db, "meas_req")
      self.freq_step = read_from_database(db, "freq_step")

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
      "tool_status" : TURN_OFF,
      "meas_req": MEASUREMENT_FREE,
      "mode" : 0,
      "start_freq" : 0,
      "stop_freq" : 0,
      "power" : 0,
      "time_stamp" : 0,
      "reset_tracing_period" : 0,
      "freq_step": 0,
      "isScanAvalaible": False,
   }

   def __init__(self, in_name='Main', database_ptr = None):
      self.name = in_name
      # State of the guard - default is init.
      self.state = Init()
      self.db = DataBase(database_ptr)
   
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
      self.db.read_from_Alchemy(Frequency)
   
   def change_settings(self, key, value):
      if key in self.settings.keys():
         self.settings[key] = value
      else: raise Exception("Key doesn't exist!")

      self.write_to_db(DATA_BASE, self.settings)
   
   def check(self):
      read_settings = self.read_db()

      if read_settings == self.settings:
         print("Nothing change, stay in IDLE")
         if self.state.__class__ != Idle and self.state.__class__ != Measurement:
            self.change_state(Idle)       
      
      else:
         print("Take action")
         # If settings has been changed, choose requested action
         if self.settings["tool_status"] != read_settings["tool_status"]:

            if read_settings["tool_status"] == TURN_ON:
               print("ON MODE")
               self.change_state(On)
               retStatus = self.state.turn_on()
               self.change_settings("tool_status", retStatus)

            elif read_settings["tool_status"] == TURN_OFF:
               print("OFF MODE")
               self.change_state(Off)
               retStatus = self.state.turn_off()
               self.change_settings("tool_status", retStatus)

            else: raise Exception("Wrong tool status")

         if self.settings["meas_req"] != read_settings["meas_req"]:
            print("MEASUREMENT MODE")
            if read_settings["meas_req"] == MEASUREMENT_START:
               self.change_state(Measurement)
               self.state.managing_measurement(read_settings["meas_req"], self.scheduler)
               for task in self.scheduler:
                  task.start()

               self.settings["meas_req"] = MEASUREMENT_ONGOING
               self.change_settings("meas_req", MEASUREMENT_ONGOING)
            elif read_settings["meas_req"] == MEASUREMENT_STOP:
               self.change_state(Measurement)
               self.scheduler.pop()
               self.state.managing_measurement(read_settings["meas_req"], self.scheduler)
               self.change_settings("meas_req", MEASUREMENT_FREE)
               self.change_state(Idle)

   def read_db(self):
      print("Reading database")
      return DATA_BASE

   def write_to_db(self, db, *args):
      print("Write to DB")
      for el in args:
         db.update(el)


import time
from database import *
class State(object):

   name = "state"
   allowed = []

   def switch(self, state):
      """ Switch to new state """
      if state.name in self.allowed:
         print('Current:',self,' => switched to new state',state.name)
         self.__class__ = state
         state.__init__(self)

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
   def __init__(self) -> None:
      print("Calibration instance")
   
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

class Idle(State):
   """ State of being in hibernation after powered on """
   name = "idle"
   allowed = ['off', 'on', 'measurement']

class Measurement(State):
   name = "measurement"
   allowed = ['idle']

   def measurement(self, type_req, settup):
      print("measurement")

      if type_req == MEASUREMENT_START:
         self.start_measurement()

      elif type_req == MEASUREMENT_STOP:
         self.stop_measurement()
      

   def stop_measurement(self):
      print("Stopped measurement")
   
   def start_measurement(self):
      print("Start measurement")
   
class Guard(object):
   """ A class representing a guardian """
   status = None
   
   scheduler = list()
   
   settings = {
      "init_status": None,
      "calib_status" : False,
      "tool_status" : TURN_OFF,
      "meas_req": None,
      "settup":{
         "mode" : 0,
         "start_freq" : 0,
         "stop_freq" : 0,
         "power" : 0,
         "time_stamp" : 0,
         "reset_tracing_period" : 0,
      }
   }
   

   def __init__(self, in_name='Main'):
      self.name = in_name
      # State of the guard - default is init.
      self.state = Init()
   
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
      self.state.switch(state)
   
   def change_settings(self, key, value):
      if key in self.settings.keys():
         self.settings[key] = value
      else: raise Exception("Key doesn't exist!")

      self.write_to_db(DATA_BASE, self.settings)
   
   def check(self):
      read_settings = self.read_db()

      if read_settings == self.settings:
         print("Nothing change, stay in IDLE")
      
      else:
         print("Take action")
         # If settings has been changed, choose requested action
         if self.settings["tool_status"] != read_settings["tool_status"]:

            if read_settings["tool_status"] == TURN_ON:
               self.change_state(On)
               retStatus = self.state.turn_on()
               self.change_settings("tool_status", retStatus)

            elif read_settings["tool_status"] == TURN_OFF:
               self.change_state(Off)
               retStatus = self.state.turn_off()
               self.change_settings("tool_status", retStatus)

            else: raise Exception("Wrong tool status")

            if read_settings["meas_req"] != read_settings["meas_req"]:
               self.change_state(Measurement)
               self.state.measurement(read_settings["meas_req"], read_settings["settup"])

            

   def read_db(self):
      print("Reading database")
      return DATA_BASE

   def write_to_db(self, db, *args):
      print("Write to DB")
      for el in args:
         db.update(el)


# INTEGRATED TO APP file
# comp = Guard(State)

# comp.state.print_state()
# comp.state.initialization()

# # Initialization process
# if comp.state.isInitialized():
#    comp.change_settings("init_status", COMPLETED)

#    if comp.isCalibrated():
#       comp.change_state(Idle)
   
#    else:
#       comp.change_state(Calibration)
#       comp.state.calibration()
#       comp.change_settings("calib_status", comp.get_status())

#       if comp.isCalibrated() == False:
#          raise Exception("Problem with calibration")
      
#       comp.change_state(Idle)
# else:
#    raise Exception("Problem with initialization")

# comp.state.print_state()

# while True:
#    print("Endless loop")
#    comp.state.print_state()
#    comp.check()
#    time.sleep(3)
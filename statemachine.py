import time

TURN_OFF = 0
TURN_ON = 1
COMPLETED = 2

DATA_BASE = {
   "init_status": None,
   "calib_status" : False,
   "tool_status" : TURN_OFF,
}
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

class On(State):
   """ State of being powered on and working """
   name = "on"
   allowed = ['off','measurement','idle']

class Idle(State):
   """ State of being in hibernation after powered on """
   name = "idle"
   allowed = ['off', 'on', 'measurement']

class Measurement(State):
   """ State of being in suspended mode after switched on """
   name = "measurement"
   allowed = ['on']
   
class Guard(object):
   """ A class representing a guardian """
   status = None
   
   settings = {
      "init_status": None,
      "calib_status" : False,
      "tool_status" : TURN_OFF,
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
   def change(self, state):
      """ Change state """
      self.state.switch(state)
   
   def change_settings(self, key, value):
      if key in self.settings.keys():
         self.settings[key] = value
      else: raise Exception("Key doesn't exist!")
   
   def check(self):
      read_settings = self.read_db()

      if read_settings == self.settings:
         print("Nothing change, stay in IDLE")
      
      else:
         print("Take action")

   def read_db(self):
      print("Reading database")
      return 0

   def write_to_db(self, db, *args):
      print("Write to DB")
      for el in args:
         print(el)


comp = Guard(State)

comp.state.print_state()
comp.state.initialization()

# Initialization process
if comp.state.isInitialized():
   comp.change_settings("init_status", COMPLETED)

   if comp.isCalibrated():
      comp.change(Idle)
   
   else:
      comp.change(Calibration)
      comp.state.calibration()
      comp.set_calib_status(comp.get_status())

      if comp.isCalibrated() == False:
         raise Exception("Problem with calibration")
      
      comp.change(Idle)
else:
   raise Exception("Problem with initialization")

comp.state.print_state()

while True:
   print("Endless loop")
   comp.check()
   time.sleep(3)
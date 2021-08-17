
TURN_OFF = 0
TURN_ON = 1
COMPLETED = 2
MEASUREMENT_NONE = 3
MEASUREMENT_START = 4
MEASUREMENT_HOLD = 5
MEASUREMENT_STOP = 6


DATA_BASE = {
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

def write_to_database(db, sett, val):
   print("CLIENT: Write to DB")
   if sett in db.keys():
      db[sett] = val
   else:
      raise Exception("Key isn't in dictionary")

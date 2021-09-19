
TURN_OFF = 0
TURN_ON = 1
COMPLETED = 2
MEASUREMENT_FREE = 3
MEASUREMENT_START = 4
MEASUREMENT_ONGOING = 5
MEASUREMENT_HOLD = 6
MEASUREMENT_STOP = 7

DATA_BASE = {
   "init_status": None,
   "calib_status" : False,
   "isScanAvalaible": False
}

SCANNING_RESULT = list()


def write_to_database(db, sett, val):
   print("CLIENT: Write to DB")
   if sett in db.keys():
      db[sett] = val
   else:
      raise Exception("Key isn't in dictionary")

def read_from_database(db, sett):
   if sett in db.keys():
      return db[sett]
   else:
      raise Exception("Key isn't in dictionary")

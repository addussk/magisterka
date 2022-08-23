# The object of the class represents the measured dataset for the current measurement session.

import datetime
from MlxSensorArray import mlxSensorArrayInstance


TIME_KEY = "timestamp"
FWD_KEY = "fwdPwrDbm"
RFL_KEY = "rflPwrDbm"
MHZ_KEY = "frequencyMhz"
T0_KEY = "t0"
T1_KEY = "t1"
T2_KEY = "t2"
T3_KEY = "t3"
T4_KEY = "t4"
TAVG_KEY = "tavg"
TREQ_KEY = "treq"
TINTERNAL_KEY = "temp_int"
VOLTAGE_KEY = "voltage"
CURRENT_KEY = "current"



class MeasurementSession:
    
    def __init__(self):
        self.session_title = "default title"
        self.__data = {     # a dictionary of lists
            TIME_KEY: [],
            FWD_KEY: [],
            RFL_KEY: [],
            MHZ_KEY: [],
            T0_KEY: [],
            T1_KEY: [],
            T2_KEY: [],
            T3_KEY: [],
            T4_KEY: [],
            TAVG_KEY: [],
            TREQ_KEY: [],
            TINTERNAL_KEY: [],
            VOLTAGE_KEY: [],
            CURRENT_KEY: []
            }
        self.isFrequencyDomain = False      # time domain by default

    def clearAllTraces(self):
        for k, v in self.__data.items():
            self.__data[k] = list()

    def __str__(self):
        s = f"Trace title: {self.session_title},\nTrace length: {len(self.__data[TIME_KEY])}\n"
        s += f"MHz: {self.__data[MHZ_KEY]} FWD: {self.__data[FWD_KEY]} RFL: {self.__data[RFL_KEY]}"
        return s
    
    def addDataPoint(self, fwdPwrDbm, rflPwrDbm, frequencyMhz=None, tempSensorList=(), tempRequested=None, tempInternal=None, voltage=None, current=None):
        self.__data[TIME_KEY].append(datetime.datetime.now())
        self.__data[FWD_KEY].append(round(fwdPwrDbm, 2))
        self.__data[RFL_KEY].append(round(rflPwrDbm, 2))
        f = round(frequencyMhz, 3) if frequencyMhz is not None else 0
        self.__data[MHZ_KEY].append(f)
        self.__data[T0_KEY].append(mlxSensorArrayInstance[0]['object'])
        self.__data[T1_KEY].append(mlxSensorArrayInstance[1]['object'])
        self.__data[T2_KEY].append(mlxSensorArrayInstance[2]['object'])
        self.__data[T3_KEY].append(mlxSensorArrayInstance[3]['object'])
        self.__data[T4_KEY].append(mlxSensorArrayInstance[4]['object'])
        self.__data[TAVG_KEY].append(mlxSensorArrayInstance.get_averaged_temperature())
        self.__data[TREQ_KEY].append(tempRequested)
        self.__data[TINTERNAL_KEY].append(tempInternal)
        self.__data[VOLTAGE_KEY].append(voltage)
        self.__data[CURRENT_KEY].append(current)

    def getTrace(self, key):
        print("------------")
        return self.__data[key]
    
    
MeasurementSessionInstance = MeasurementSession()

msi = MeasurementSessionInstance

if __name__=="__main__":
    msi.addDataPoint(10, 12)
    msi.addDataPoint(12, 22, 2345.56789)
    msi.addDataPoint(13, 32)
    print(msi)

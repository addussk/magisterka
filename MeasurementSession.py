# The object of the class represents the measured dataset for the current measurement session.

import datetime
from MlxSensorArray import mlxSensorArrayInstance
from RfPowerDetector import rfPowerDetectorInstance 
from copy import copy, deepcopy
from defines import RESULTS_SAVE_DIRECTORY
import time
import numpy as np

TIME_KEY = "timestamp"
FWD_KEY = "fwdPwrDbm"
FWD_WATTS_KEY = "fwdPwrWatts"
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
            FWD_WATTS_KEY: [],
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
        self.__plottedData = deepcopy(self.__data)
        self.isFrequencyDomain = False      # time domain by default
        self.__resultsFileName = ""
        self.desiredPlotTraceLength = 100
        

    def clearAllTraces(self):
        for k, v in self.__data.items():
            self.__data[k] = list()
            self.__plottedData[k] = list()

    def __str__(self):
        s = f"Trace title: {self.session_title},\nTrace length: {len(self.__data[TIME_KEY])}\n"
        s += f"MHz: {self.__data[MHZ_KEY]} FWD: {self.__data[FWD_KEY]} dBm  RFL: {self.__data[RFL_KEY]} dBm"
        return s
    
    def addDataPoint(self, fwdPwrDbm, rflPwrDbm, frequencyMhz=None, tempRequested=None, tempInternal=None):
        self.__data[TIME_KEY].append(datetime.datetime.now())
        self.__data[FWD_KEY].append(round(fwdPwrDbm, 3))
        self.__data[FWD_WATTS_KEY].append(round(10**((fwdPwrDbm-30)/10), 2))
        self.__data[RFL_KEY].append(round(rflPwrDbm, 3))
        f = round(frequencyMhz, 3) if frequencyMhz is not None else 0
        self.__data[MHZ_KEY].append(f)
        self.__data[T0_KEY].append(mlxSensorArrayInstance[0]['object'])
        self.__data[T1_KEY].append(mlxSensorArrayInstance[1]['object'])
        self.__data[T2_KEY].append(mlxSensorArrayInstance[2]['object'])
        self.__data[T3_KEY].append(mlxSensorArrayInstance[3]['object'])
        self.__data[T4_KEY].append(mlxSensorArrayInstance[4]['object'])
        self.__data[TAVG_KEY].append(mlxSensorArrayInstance.get_averaged_temperature())
        if tempRequested is not None and tempRequested > -199:
            self.__data[TREQ_KEY].append(tempRequested)
        else:
            self.__data[TREQ_KEY].append(None)
        self.__data[TINTERNAL_KEY].append(tempInternal)
        self.__data[VOLTAGE_KEY].append(round(rfPowerDetectorInstance.getPaVoltage(no_update=True), 3))
        self.__data[CURRENT_KEY].append(round(rfPowerDetectorInstance.getPaCurrent(no_update=True), 3))
        if len(self.__data[MHZ_KEY]) % 30 == 0:
            self.__selectDataForPlot()
        else:
            for key, datalist in self.__data.items():
                self.__plottedData[key].append(datalist[-1])  # add last element
        
    def getTrace(self, key):
        #return self.__data[key]
        return self.__plottedData[key]
    
    
    def __selectDataForPlot(self):
        length = len(self.__data[MHZ_KEY])
        
        if length < self.desiredPlotTraceLength:
            self.__plottedData = deepcopy(self.__data)
        
        selected_indexes = np.linspace(0, length-1, self.desiredPlotTraceLength, dtype=int)

        for key in self.__data.keys():
            self.__plottedData[key].clear()

        for idx in np.nditer(selected_indexes):
            for key in self.__data.keys():
                self.__plottedData[key].append( self.__data[key][idx] ) 
            
    
    def replaceTracesFromOtherInstance(self, msi):
        self.clearAllTraces()
        for key in self.__data.keys():
            trace = msi.getTrace(key)
            self.__data[key] = copy(trace)
        self.isFrequencyDomain = msi.isFrequencyDomain
        self.__plottedData = deepcopy(self.__data)
    
    # Functions returns a string, which represents all traces.
    # It can be saved into a CSV file.
    def getTracesAsCsv(self):
        SEPARATOR = ";"
        keys = [      # order of columns needs to be well defined
            TIME_KEY,
            FWD_KEY,
            FWD_WATTS_KEY,
            RFL_KEY,
            MHZ_KEY,
            T0_KEY,
            T1_KEY,
            T2_KEY,
            T3_KEY,
            T4_KEY,
            TAVG_KEY,
            TREQ_KEY,
       #     TINTERNAL_KEY,
            VOLTAGE_KEY,
            CURRENT_KEY
        ]

        lines = []
        for i in range(len(self.__data[FWD_KEY])):   # FWD because it is always stored
            if i==0:                                 # header
                line = SEPARATOR.join(map(str, keys))
                lines.append("#" + line)
                continue
            line = ""
            for j, key in enumerate(keys):
                try:
                    v = self.__data[key][i]
                except:
                    v = "(no data)"
                line += str(v)
                if j<(len(keys)-1):
                    line += ";"
            lines.append(line)
        output = "\n".join(lines)
        self.__updateFileName()
        return output
    
    def __updateFileName(self):
        self.__resultsFileName = f"results_" + time.strftime("%Y%m%d-%H%M%S")
    
    def getResultsFileName(self):
        return self.__resultsFileName
    
    def saveTracesToFile(self, fn_suffix=""):
        if fn_suffix != "":
            fn_suffix = f"_{fn_suffix}"
        csv = self.getTracesAsCsv()
        fname = f"{RESULTS_SAVE_DIRECTORY}/{self.__resultsFileName}{fn_suffix}.csv"
        with open(fname, "w") as text_file:
            text_file.write(csv)
        
    
MeasurementSessionInstance = MeasurementSession()

msi = MeasurementSessionInstance

if __name__=="__main__":
    msi.addDataPoint(10, 12)
    msi.addDataPoint(12, 22, 2345.56789)
    msi.addDataPoint(13, 32)
    print(msi)

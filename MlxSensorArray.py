from smbus2 import SMBus
from mlx90614 import MLX90614
from random import random
from threading import Lock

i2cMutex = Lock()

class MlxSensorArray:
    
    # Constructor takes the following arguments:
    # adresses:       list of I2C adresses of IR sensors
    # i2cbus:         number of I2C bus
    # dommy_values:   set to True, if you do not have the sensor array
    def __init__(self, addresses=[], i2cbus=1, dummy_values=False):
        self.__addresses = addresses
        self.dummy_values = dummy_values
        self.__sensors = []
        self.__bus = SMBus(i2cbus)
        self.__object_temperatures = [None] * len(addresses)
        self.__ambient_temperatures = [None] * len(addresses)
        
        for adr in addresses:
            sensor = MLX90614(self.__bus, address=adr)
            self.__sensors.append(sensor)
        self.update_readings()
       
    # Reads object temprature from the idx-sensor
    def read_object_temperature(self, sensor_idx):
        try:
            if not self.dummy_values:
                sensor = self.__sensors[sensor_idx]
                i2cMutex.acquire()
                temperature = sensor.get_obj_temp()
                temperature = round(temperature, 3)  # there is no more accuracy in the sensor
            else:
                temperature = self.__addresses[sensor_idx] + round(random(),2)
        except e:
            print(f"Exception during object temperature IR sensor read idx={sensor_idx}, message:{e}")
            temperature = None
        finally:
            i2cMutex.release()
        self.__object_temperatures[sensor_idx] = temperature
        return temperature

    # Reads ambient tempreature from the idx-sensor 
    def read_ambient_temperature(self, sensor_idx):
        try:
            if not self.dummy_values:
                sensor = self.__sensors[sensor_idx]
                i2cMutex.acquire()
                temperature = sensor.get_amb_temp()
                temperature = round(temperature, 3)  # there is no more accuracy in the sensor
            else:
                temperature = self.__addresses[sensor_idx] - 10 + round(random(),2)    # -10 just to make it different from obj_temp (no special meaning)
        except e:
            print(f"Exception during ambient temperature IR sensor read idx={sensor_idx}, message:{e}")
            temperature = None
        finally:
            i2cMutex.release()            
        self.__ambient_temperatures[sensor_idx] = temperature
        return temperature

    def get_averaged_temperature(self):
        s = 0
        for i in range(len(self)):
            s += self[i]["object"]
        average = s / len(self)
        return round(average, 3)

    # Updates all readings in the sensor array
    def update_readings(self):
        for idx in range(len(self.__sensors)):
            self.read_ambient_temperature(idx)
            self.read_object_temperature(idx)
            
    def __len__(self):
        return len(self.__addresses)
    
    def __getitem__(self, idx):
        return {"ambient":self.__ambient_temperatures[idx], "object":self.__object_temperatures[idx]}
    
mlxSensorArrayInstance = MlxSensorArray(addresses=[0x5B, 0x5C, 0x5D, 0x5E, 0x5A], i2cbus=1, dummy_values = False)

# Testing code:
if __name__=="__main__":
    msa = MlxSensorArray(addresses=[0x5B, 0x5C, 0x5D, 0x5E, 0x5A], i2cbus=1, dummy_values = False)

    for j in range(10):   # read everything many times
        print()
        for i in range(len(msa)):
            temps = msa[i]
            print(f"sensor id={i}, readings: {temps}")
        msa.update_readings()
    
    
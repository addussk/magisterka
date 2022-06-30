import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
from scipy import interpolate
import random
from MlxSensorArray import i2cMutex

class RfPowerDetector:
    
    def __init__(self, i2cbus=1, dummy_values=False):
        self.dummy_values = dummy_values

        fwd_att_cpl =  0 + 16  # dB  +30 att
        rfl_att_cpl =  0 + 16  # dB  +30 att
        self.interpolators = {
            # from the AD8317 datasheet, Fig. 7 (at 5.8 GHz)
            # Pin = -45 dBm, Vout = 1.36 V
            # Pin = -10 dBm, Vout = 0.58 V
                "fwd": interpolate.interp1d([1.36, 0.58], [-45+fwd_att_cpl, -10+fwd_att_cpl], fill_value='extrapolate'),
                "rfl": interpolate.interp1d([1.36, 0.58], [-45+fwd_att_cpl, -10+fwd_att_cpl], fill_value='extrapolate')
            }

        self.__fwdPowerDbm = 0
        self.__rflPowerDbm = 0

    def readVoltage(self, ch="fwd"):
        if not self.dummy_values:
            if ch not in ["fwd", "rfl"]:
                raise Exception(f"ADC: Incorrect channel, given: {ch}")
            voltage = 0
            i2cMutex.acquire()
            try:
                i2c = busio.I2C(board.SCL, board.SDA)
                ads = ADS.ADS1115(i2c)
                #Single Ended Mode
                chan = None
                if ch=="fwd":
                    chan = AnalogIn(ads, ADS.P0)
                elif ch=="rfl":
                    chan = AnalogIn(ads, ADS.P1)
                voltage = chan.voltage    # actual I2C read - must be secured by i2c mutex!
            finally:
                i2cMutex.release()
            
            #print(f"Reading for ch={ch}: adc={chan.value}, voltage={chan.voltage}")
            return voltage
        else:
            return random.uniform(1.0, 1.2)   # dummy, random numbers
    
    def __calibration(self, voltage, ch_id="fwd"):
        pwr_dBm = self.interpolators[ch_id](voltage)
        return pwr_dBm
    
    def getFwdPowerDbm(self):
        ch_id = "fwd"
        v = self.readVoltage(ch_id)
        pwr = float(self.__calibration(v, ch_id))
        self.__fwdPowerDbm = pwr
        return pwr
    
    def getRflPowerDbm(self):
        ch_id = "rfl"
        v = self.readVoltage(ch_id)
        pwr = float(self.__calibration(v, ch_id))
        print("---", v, pwr)
        self.__rflPowerDbm = pwr
        return pwr
    
    def getReturnLossDb(self):
        rl = self.__fwdPowerDbm - self.__rflPowerDbm 
        return rl
    
rfPowerDetectorInstance = RfPowerDetector()


if __name__=="__main__":
    rpd = RfPowerDetector(dummy_values = False)
    fwd = rpd.getFwdPowerDbm()
    print(f"FWD power={fwd} dBm")
    rfl = rpd.getRflPowerDbm()
    print(f"RFL power={rfl} dBm")
    rl = rpd.getReturnLossDb()
    print(f"Return Loss = {rl}")
    
    

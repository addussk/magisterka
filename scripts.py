import random, math
from dashApp.models import FrontEndInfo
import time
from w1thermsensor import W1ThermSensor


def dummy_temperature(min_temp=0, max_temp=100):
    
    sensor = W1ThermSensor()
    temp = sensor.get_temperature()
    print(temp)
    return temp


def dummy_val_fixed_meas(freq):
    return abs(math.sin(freq))

def dummy_val_tracking(freq, in_power, db):
    a, p = 1/10, 100
    mid_freq= (db.session.query(FrontEndInfo).order_by(FrontEndInfo.id).first()).get_slider()
    return (a*(freq - mid_freq)**2 - p) * math.sin(math.radians(math.pi*freq)*1.5)

def dummy_val_tracking_received_pwr(measured_power):
    return measured_power - random.randint(10,20)
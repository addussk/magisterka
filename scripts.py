import random, math, datetime
from database import SLIDER_CONTAINER, read_from_database

def dummy_temperature(min_temp=0, max_temp=100):
    sum = 0 
    
    for x in range(5):
        sum += round(random.uniform(min_temp, max_temp), 1)

    return int(sum/5)


def dummy_val_fixed_meas(freq):
    return abs(math.sin(freq))

def dummy_val_tracking(freq, in_power):
    a, p = 1/10, (100 * in_power)
    mid_freq= read_from_database(SLIDER_CONTAINER, "slider_val")
    return (a*(freq - mid_freq)**2 - p) * math.sin(math.radians(math.pi*freq)*1.5)
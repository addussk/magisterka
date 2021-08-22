import random, math, datetime

def dummy_temperature(min_temp=0, max_temp=100):
    sum = 0 
    
    for x in range(5):
        sum += round(random.uniform(min_temp, max_temp), 1)

    return int(sum/5)


def dummy_val_fixed_meas(freq):
    # t = datetime.datetime.now()
    return math.sin(freq)

def dummy_val_tracking(freq, in_power):
    return math.sin(freq)
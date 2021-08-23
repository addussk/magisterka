import random, math, datetime

def dummy_temperature(min_temp=0, max_temp=100):
    sum = 0 
    
    for x in range(5):
        sum += round(random.uniform(min_temp, max_temp), 1)

    return int(sum/5)


def dummy_val_fixed_meas(freq):
    return abs(math.sin(freq))

def dummy_val_tracking(freq, in_power):
    r_number = random.randint(1,10)
    return (in_power*abs(math.sin(freq)) + (in_power/r_number)*math.cos(freq))
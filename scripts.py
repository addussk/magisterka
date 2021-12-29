import random, math
from dashApp.models import FrontEndInfo


def dummy_val_tracking(freq, in_power, db):
    a, p = 1/10, 100
    mid_freq= (db.session.query(FrontEndInfo).order_by(FrontEndInfo.id).first()).get_slider()
    return (a*(freq - mid_freq)**2 - p) * math.sin(math.radians(math.pi*freq)*1.5)

def dummy_val_tracking_received_pwr(measured_power):
    return measured_power - random.randint(10,20)
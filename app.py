import datetime, time, threading, psutil
from flask import Flask
from scripts import dummy_temperature
from dashApp.webapp import create_app

from dashApp.models import Frequency, Temperature, Ustawienia
app = Flask(__name__, instance_relative_config=False)

app, db = create_app(app)

def gen_dummy_freq():
    # print("Measure frequency...")
    db.session.add(Frequency(measured_freq=psutil.cpu_percent(), time_of_measurement=datetime.datetime.now()))
    db.session.commit()

def gen_dummy_temp():
    db.session.add(Temperature(measured_temp=dummy_temperature(), time_of_measurement=datetime.datetime.now()))
    db.session.commit()

def read_setting_from_db():
    latest_set = db.session.query(Ustawienia).order_by(Ustawienia.id.desc()).first()
    return latest_set.get()

def made_measurement():
    while(True):
        # print("Started task...")
        # print("%s: %s" % (threading.current_thread().name, time.ctime(time.time())))
        curr_setting = read_setting_from_db()
        print(curr_setting)
        time.sleep(10)
        gen_dummy_freq()

        # print("Measure temperature...")
        gen_dummy_temp()
        
        # print("task completed")

t2 = threading.Thread(target=made_measurement)
t2.start()

if __name__ == '__main__':
    db.create_all()
    app.run_server(debug=True)
    t2.join()
    # t1 = threading.Thread(target=app.run_server)
    # t1.start()
    
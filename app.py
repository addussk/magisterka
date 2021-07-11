import datetime, time, threading, psutil
from flask import Flask
from scripts import dummy_temperature
from dashApp.webapp import create_app

app = Flask(__name__)

app, db = create_app(app)

def made_measurement():
    from dashApp.models import Frequency, Temperature
    while(True):
        print("Started task...")
        print("%s: %s" % (threading.current_thread().name, time.ctime(time.time())))
        time.sleep(10)

        print("Measure frequency...")
        db.session.add(Frequency(measured_freq=psutil.cpu_percent(), time_of_measurement=datetime.datetime.now()))
        db.session.commit()

        print("Measure temperature...")
        db.session.add(Temperature(measured_temp=dummy_temperature(), time_of_measurement=datetime.datetime.now()))
        db.session.commit()
        print("task completed")

t2 = threading.Thread(target=made_measurement)
t2.start()

if __name__ == '__main__':
    db.create_all()
    t1 = threading.Thread(target=app.run_server)
    t1.start()
    
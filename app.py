import datetime, time, threading, psutil
from flask import Flask
from scripts import dummy_temperature
from dashApp.webapp import create_app
from statemachine import Guard, Idle, Calibration, State
from database import *
from dashApp.models import  Ustawienia, Temperature, Frequency
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
    comp = Guard(State, db)

    comp.state.print_state()
    comp.state.initialization()
    # Initialization process
    if comp.state.isInitialized():
        comp.change_settings("init_status", COMPLETED)

        if comp.isCalibrated():
            comp.change_state(Idle)
    
        else:
            comp.change_state(Calibration)
            comp.state.calibration()
            comp.change_settings("calib_status", comp.get_status())

            if comp.isCalibrated() == False:
                raise Exception("Problem with calibration")
            
            comp.change_state(Idle)
    else:
        raise Exception("Problem with initialization")

    comp.state.print_state()

    while(True):
        # print("Endless loop")
        # comp.state.print_state()
        comp.check()
        time.sleep(5)

        # OLD PART
        # print("Started task...")
        # print("%s: %s" % (threading.current_thread().name, time.ctime(time.time())))
        # curr_setting = read_setting_from_db()
        # print(curr_setting)
        # time.sleep(10)
        # gen_dummy_freq()

        print("Measure temperature...")
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
    
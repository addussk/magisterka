import datetime, time, threading, psutil
from flask import Flask
from scripts import dummy_temperature
from dashApp.webapp import create_app
from statemachine import Guard, Idle, Calibration, State
from database import *
from dashApp.models import  MeasSettings, Temperature, Frequency
app = Flask(__name__, instance_relative_config=False)

app, db = create_app(app)

def gen_dummy_temp():
    db.session.add(Temperature(measured_temp=dummy_temperature(), time_of_measurement=datetime.datetime.now()))
    db.session.commit()

def made_measurement():
    comp = Guard(State, db)

    comp.state.print_state()
    comp.state.initialization()
    # Initialization process
    if comp.state.isInitialized():
        comp.set_init_status(COMPLETED)

        if comp.isCalibrated():
            comp.change_state(Idle)
    
        else:
            comp.change_state(Calibration)
            comp.state.calibration()
            comp.set_calib_status(COMPLETED)

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
    
from dashApp.webapp import create_app
from statemachine import Guard, Idle, Calibration, State
from defines import *
import datetime, time, threading
from flask import Flask

app = Flask(__name__, instance_relative_config=False)

app, db = create_app(app)

def make_measurement():
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
        if LOG_ON:
            print("task started")
            print("the number of Thread objects currently alive: ", threading.active_count())
            print("current thread: ", threading.current_thread())
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print("Current Time is :", current_time)
        
        # comp.state.print_state()
        comp.state_machine()
        time.sleep(5)

        comp.measure_temperature()

        if LOG_ON:
            print("task completed")

t2 = threading.Thread(target=make_measurement)
t2.start()

if __name__ == '__main__':
    #app.run_server(host='192.168.0.94', port=8080, debug=False, threaded=True)
    app.run_server(host="0.0.0.0", port=8080, debug=False, threaded=True)   # 0.0.0.0 for both access types: local and from the network
    t2.join()
    # t1 = threading.Thread(target=app.run_server)
    # t1.start()

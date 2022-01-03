import datetime, time, threading
from flask import Flask
from dashApp.webapp import create_app
from statemachine import Guard, Idle, Calibration, State
from database import *

app = Flask(__name__, instance_relative_config=False)

app, db = create_app(app)

class Results(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measured_freq = db.Column(db.Integer)
    measured_power = db.Column(db.Integer)
    transmited_power = db.Column(db.Integer)
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.measured_freq) 
    
    def get(self):
        return (self.measured_power, self.time_of_measurement)
    
    def get_meas_freq(self):
        return self.measured_freq
    
    def get_meas_pwr(self):
        return self.measured_power

    def get_trans_pwr(self):
        return self.transmited_power
    
    def get_data_meas(self):
        return self.time_of_measurement
    
class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    obj_temp = db.Column(db.Integer)
    sys_temp = db.Column(db.Integer)
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def get(self):
        return (self.sys_temp, self.time_of_measurement)
    
    def get_sys_temperature(self):
        return self.sys_temp

class MeasSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    start_freq = db.Column(db.Integer, nullable=False)
    stop_freq = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    freq_step = db.Column(db.Integer, nullable=False)
    time_step = db.Column(db.Integer, nullable=False)
    best_scan_freq = db.Column(db.Integer)
    best_scan_power = db.Column(db.Integer)


    def __repr__(self):
        return '<Mode {}>'.format(self.state)
    
    def set_default(self):
        self.mode = 0
        self.state = 3 # MEASUREMENT_FREE
        self.start_freq = 2400
        self.stop_freq = 2400
        self.power = 10
        self.freq_step = 1
        self.time_step = 5
        
    def get(self, member):
        if member == "mode":
            return self.mode

        elif member == "state":
            return self.state
        
        elif member == "start_freq":
            return self.start_freq

        elif member == "stop_freq":
            return self.stop_freq
        
        elif member == "power":
            return self.power

        elif member == "freq_step":
            return self.freq_step
        
        elif member == "time_step":
            return self.time_step

        else: return "invalid name"

    def get_mode(self):
        return self.mode
        
    def get_state(self):
        return self.state
    
    def get_minimum(self):
        return [self.best_scan_power, self.best_scan_freq]

    def get_all(self):
        return self.id, self.mode, self.state, self.start_freq, self.stop_freq, self.power, self.freq_step, self.time_step
    
class FrontEndInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slider_val = db.Column(db.Integer, nullable=False)
    tool_status = db.Column(db.Boolean)
    isScanAvalaible = db.Column(db.Boolean)
    
    def __repr__(self):
        return '<Slider Value: {}>'.format(self.slider_val)

    def set_default(self):
        self.slider_val = 2500
        self.tool_status = False
        self.isScanAvalaible = False

    def get(self, member):
        if member == "slider_val":
            return self.slider_val

        elif member == "tool_status":
            return self.tool_status
        
        elif member == "isScanAvalaible":
            return self.isScanAvalaible


        else: return "invalid name"

    def get_tool_status(self):
        return self.tool_status

    def get_slider(self):
        return self.slider_val

    def change_tool_status(self, value):
        self.tool_status = value
        self.tool_status = value

class MeasurementInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255) )
    beginning = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    finish = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def update(self, key, value):
        print("imhere@@@@@@")
        print(key.__class__, type(key), type(self.finish))
        if key == self.name:
            self.name = value
        elif key == self.finish:
            self.finish = value
        else:
            print("else@@@@")

    def get_all(self):
        return self.id, self.name, self.beginning, self.finish


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
        # comp.state.print_state()
        comp.check()
        time.sleep(5)

        print("Measure temperature...")
        comp.measure_temperature()

        #adc_measurement()
        
        # print("task completed")

t2 = threading.Thread(target=made_measurement)
t2.start()

if __name__ == '__main__':
    db.create_all()
    app.run_server(host='192.168.1.106', port=8080,debug=True)
    t2.join()
    # t1 = threading.Thread(target=app.run_server)
    # t1.start()
    
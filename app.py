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


class Frequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measured_freq = db.Column(db.Integer, nullable=False)
    measured_power = db.Column(db.Integer, nullable=False)
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.measured_freq) 
    
    def get(self):
        return (self.measured_power, self.time_of_measurement)
    

class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measured_temp = db.Column(db.Integer, nullable=False)
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def get(self):
        return (self.measured_temp, self.time_of_measurement)
    
    def get_temperature(self):
        return self.measured_temp

class MeasSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.Integer, nullable=False)
    state = db.Column(db.Integer, nullable=False)
    start_freq = db.Column(db.Integer, nullable=False)
    stop_freq = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    freq_step = db.Column(db.Integer, nullable=False)
    time_step = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Mode {}>'.format(self.state)
    
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

    def get_state(self):
        return self.state

    def get_all(self):
        return self.id, self.mode, self.state, self.start_freq, self.stop_freq, self.power, self.freq_step, self.time_step


class FrontEndInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slider_val = db.Column(db.Integer, nullable=False)
    tool_status = db.Column(db.Boolean)
    isScanAvalaible = db.Column(db.Boolean)

    def __repr__(self):
        return '<Slider Value: {}>'.format(self.slider_val)

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
    
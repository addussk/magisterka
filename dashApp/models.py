import datetime
from dashApp.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username) 

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

class MeasurementInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255) )
    beginning = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    finish = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    def update(self, key, value):
        if key.key == "name":
            self.name = value
        elif key.key == "beginning":
            self.beginning = value
        elif key.key == "finish":
            self.finish = value
        else:
            print("else@@@@")

    def get_all(self):
        return self.id, self.name, self.beginning, self.finish
    
    def get_time_scope(self):
        return [self.beginning, self.finish]
    
    def get_id(self):
        return self.id
    
    def get_name(self):
        return self.name

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
    power_min = db.Column(db.Integer, nullable=False)
    power_max = db.Column(db.Integer, nullable=False)
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
        self.power_min = 1
        self.power_max = 13
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
        
        elif member == "power_min":
            return self.power_min
        
        elif member == "power_max":
            return self.power_max

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
        return self.id, self.mode, self.state, self.start_freq, self.stop_freq, self.power_max, self.freq_step, self.time_step
    
class FrontEndInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slider_val = db.Column(db.Integer, nullable=False)
    tool_status = db.Column(db.Boolean)
    calib_status = db.Column(db.Boolean)
    attenuation = db.Column(db.Integer)
    isScanAvalaible = db.Column(db.Boolean)
    
    def __repr__(self):
        return '<Slider Value: {}>'.format(self.slider_val)

    def set_default(self):
        self.slider_val = 2500
        self.attenuation = 0
        self.tool_status = False
        self.isScanAvalaible = False
        self.calib_status = False
    
    def set_attenuation(self, value):
        self.attenuation = value

    def change_tool_status(self, value):
        self.tool_status = value
    
    def change_calib_status(self, value):
        self.calib_status = value

    def get(self, member):
        if member == "slider_val":
            return self.slider_val

        elif member == "tool_status":
            return self.tool_status
        
        elif member == "isScanAvalaible":
            return self.isScanAvalaible

        elif member == "calib_status":
            return self.calib_status

        elif member == "attenuation":
            return self.attenuation

        else: return "invalid name"

    def get_tool_status(self):
        return self.tool_status

    def get_slider(self):
        return self.slider_val

    def get_calib_status(self):
        return self.calib_status
    
    def get_attenuation(self):
        return self.attenuation
    
import datetime
from dashApp.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username) 

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
    state = db.Column(db.Integer)
    start_freq = db.Column(db.Integer, nullable=False)
    stop_freq = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    freq_step = db.Column(db.Integer, nullable=False)
    time_step = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Mode {}>'.format(self.state)
    
    def get(self):
        return (self.id, self.mode, self.state, self.start_freq, self.stop_freq, self.power, self.freq_step, self.time_step)

class FrontEndInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slider_val = db.Column(db.Integer, nullable=False)
    tool_status = db.Column(db.Boolean)

    def __repr__(self):
        return '<Slider Value: {}>'.format(self.slider_val)

    def get(self, member):
        if member == "slider_val":
            return self.slider_val

        elif member == "tool_status":
            return self.tool_status

        else: return "invalid name"

    def get_tool_status(self):
        return self.tool_status

    def get_slider(self):
        return self.slider_val

    def change_tool_status(self, value):
        self.tool_status = value
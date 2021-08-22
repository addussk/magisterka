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

class Ustawienia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meas_mode = db.Column(db.Integer, nullable=False)
    start_freq = db.Column(db.Integer, nullable=False)
    stop_freq = db.Column(db.Integer, nullable=False)
    power = db.Column(db.Integer, nullable=False)
    time_stemp = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<Mode {}>'.format(self.meas_mode)
    
    def get(self):
        return (self.id, self.meas_mode, self.start_freq, self.stop_freq, self.power, self.time_stemp)

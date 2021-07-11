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
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.measured_freq) 
    
    def get(self):
        return (self.measured_freq, self.time_of_measurement)
    

class Temperature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measured_temp = db.Column(db.Integer, nullable=False)
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username)

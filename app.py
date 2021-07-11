import datetime, time, threading, psutil
import dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dashApp.layout import layout_main
from dashApp.callbacks import register_callbacks

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = Flask(__name__)
# inject Dash
app = dash.Dash(
    server=app,
    url_base_pathname='/dashboard/',
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
)
app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/test.db"

app.layout = layout_main

db = SQLAlchemy(app.server)

register_callbacks(app)
class Frequency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    measured_freq = db.Column(db.Integer, nullable=False)
    time_of_measurement = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User {}>'.format(self.username) 
    
    def get(self):
        return (self.measured_freq, self.time_of_measurement)

def made_measurement():
    while(True):
        print("Started task...")
        print("%s: %s" % (threading.current_thread().name, time.ctime(time.time())))
        time.sleep(10)
        db.session.add(Frequency(measured_freq=psutil.cpu_percent(), time_of_measurement=datetime.datetime.now()))
        db.session.commit()
        print("task completed")

t2 = threading.Thread(target=made_measurement)
t2.start()

if __name__ == '__main__':
    db.create_all()
    t1 = threading.Thread(target=app.run_server)
    t1.start()
    
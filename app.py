import datetime, time, threading, psutil
import dash
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dashApp.layout import layout_main
from dashApp.callbacks import register_callbacks
from scripts import dummy_temperature

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

def made_measurement():
    from dashApp.models import Frequency, Temperature
    while(True):
        print("Started task...")
        print("%s: %s" % (threading.current_thread().name, time.ctime(time.time())))
        time.sleep(10)

        print("Measure frequency...")
        db.session.add(Frequency(measured_freq=psutil.cpu_percent(), time_of_measurement=datetime.datetime.now()))
        db.session.commit()

        print("Measure temperature...")
        db.session.add(Temperature(measured_temp=dummy_temperature(), time_of_measurement=datetime.datetime.now()))
        db.session.commit()
        print("task completed")

t2 = threading.Thread(target=made_measurement)
t2.start()

if __name__ == '__main__':
    db.create_all()
    t1 = threading.Thread(target=app.run_server)
    t1.start()
    
import datetime, time, threading
import dash

def made_measurement(db):
    while(True):
        print("Started task...")
        print("%s: %s" % (threading.current_thread().name, time.ctime(time.time())))
        time.sleep(10)
        # db.session.add(Measurement(measurement=psutil.cpu_percent(), date_measurement=datetime.datetime.now()))
        # db.session.commit()
        print("task completed")
    
if __name__ == '__main__':
    from flask import Flask
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

    
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy(app.server)
    db.create_all()

    from dashApp.layout import layout_main
    app.layout = layout_main

    from dashApp.callbacks import register_callbacks
    register_callbacks(app)

    t1 = threading.Thread(target=app.run_server(debug=True)).start()
    t2 = threading.Thread(target=made_measurement(db)).start()
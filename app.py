import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
from numpy import True_
import plotly
from dash.dependencies import Input, Output


    
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

    app.run_server(debug=True)
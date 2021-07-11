import dash
from flask_sqlalchemy import SQLAlchemy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_app(app):
    # inject Dash
    app = dash.Dash(
    server=app,
    url_base_pathname='/dashboard/',
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets
    )

    app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/test.db"

    from dashApp.layout import layout_main
    app.layout = layout_main

    
    from dashApp.callbacks import register_callbacks
    register_callbacks(app)

    db = SQLAlchemy(app.server)

    return app, db

import dash
from flask_sqlalchemy import SQLAlchemy

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_app(app):
    # inject Dash
    app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/dashboard/',
    suppress_callback_exceptions=True,
    )

    app.server.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/test.db"
    app.server.config['SECRET_KEY'] = 'asd asd asd'

    from dashApp.layout import layout_main
    app.layout = layout_main

    
    from dashApp.callbacks import register_callbacks
    register_callbacks(app)

    db = SQLAlchemy(app.server)

    return app, db

import dash
from flask_sqlalchemy import SQLAlchemy

SQLALCHEMY_TRACK_MODIFICATIONS = False

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

def create_app(app):

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/test.db"
    app.config['SECRET_KEY'] = 'asd asd asd'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    db = SQLAlchemy(app)
    db.init_app(app)
    app.app_context().push()

    # inject Dash
    app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname='/dashboard/',
    suppress_callback_exceptions=True,
    )

    from dashApp.layout import layout_main
    app.layout = layout_main

    
    from dashApp.callbacks import register_callbacks
    register_callbacks(app)


    return app, db

import dash
from dashApp.extensions import db

SQLALCHEMY_TRACK_MODIFICATIONS = False


def create_app(app):

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db/test.db"
    app.config['SECRET_KEY'] = 'asd asd asd'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    db.init_app(app)
    db.app = app
    db.create_all()

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

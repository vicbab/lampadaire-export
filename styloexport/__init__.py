from typing import Optional

from flask import Flask

from . import api, commands, views

__version__ = "0.0.32"

__pdoc__ = {}
__pdoc__["create_app"] = False
__pdoc__["article"] = False
__pdoc__["commands"] = False
__pdoc__["config"] = False
__pdoc__["forms"] = False
__pdoc__["pandocapi"] = False
__pdoc__["styloapi"] = False
__pdoc__["utils"] = False
__pdoc__["views"] = False
__pdoc__["wsgi"] = False


def create_app(test_config: Optional[dict] = None) -> Flask:
    # create and configure the app
    app = Flask(__name__)

    app.config.from_pyfile("config.py")
    if test_config:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    app.register_blueprint(views.blueprint)
    app.register_blueprint(api.blueprint, url_prefix="/api")
    app.register_blueprint(commands.blueprint)
    return app


app = create_app()

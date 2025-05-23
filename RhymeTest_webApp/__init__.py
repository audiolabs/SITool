import os
from flask import Flask
from flask_session import Session
import logging
from .utils import load_config
from .config import Config

def setup_logging(app):
    logging.basicConfig(
        level=app.config['LOGGING_LEVEL'],
        format=app.config['LOGGING_FORMAT']
    )


def create_app(config_path=None):
    """Create and configure the Flask app."""
    app = Flask(__name__)

    # Load the default configuration from config.py
    app.config.from_object(Config)

    # Load app configuration
    config_path = app.config["CONFIG_FILE_PATH"]
    print(f"Config Path: {config_path}")
    config = load_config(config_path)
    app.config.update(config)

    Session(app)

    # Set up logging
    setup_logging(app)
    language = app.config.get('language')
    # Register routes
    with app.app_context():
        if language == "gr":
            from . import routes_gr as routes
        else:
            from . import routes
        app.register_blueprint(routes.bp)

    return app
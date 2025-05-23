import os
import logging

class Config:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.urandom(30)
    SESSION_TYPE = "filesystem"
    SESSION_FILE_DIR = "session_data"
    LOGGING_LEVEL = logging.INFO
    LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

    # Hardcode the path to the configuration file
    CONFIG_FILE_PATH = "./RhymeTest_webApp/config_files/config_DRT_without_LP.yaml"


class DevelopmentConfig(Config):
    DEBUG = True
    LOGGING_LEVEL = logging.DEBUG

class ProductionConfig(Config):
    DEBUG = False
    LOGGING_LEVEL = logging.WARNING
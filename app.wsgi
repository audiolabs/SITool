import sys
import logging

logging.basicConfig(stream=sys.stderr)
logging.error("Python version: " + sys.version)

# Add the app directory to the Python path
sys.path.insert(0, 'var/www/html/si-tool-speech-intelligibility-toolkit-for-subjective-evaluation')

# Import the Flask application
from RhymeTest_webApp import create_app

application = create_app()

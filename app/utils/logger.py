import logging
from flask import current_app

def setup_logger():
    """Configure the application logger."""
    if not current_app.debug:
        # Create a file handler
        file_handler = logging.FileHandler('app.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        current_app.logger.addHandler(file_handler)

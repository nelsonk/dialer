import logging

from logging.handlers import TimedRotatingFileHandler, RotatingFileHandler

from configs.settings import access_log_file, error_log_file

class Logger:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Avoid re-initializing
            self.access_log_file = access_log_file
            self.error_log_file = error_log_file

            self.logger = logging.getLogger(__name__)
            self.logger.setLevel(logging.DEBUG)

            self.error_file_handler = RotatingFileHandler(self.error_log_file, maxBytes=500*1024*1024, backupCount=3)
            self.error_file_handler.setLevel(logging.ERROR)
            self.access_file_handler = TimedRotatingFileHandler(self.access_log_file, when="midnight", interval=2, backupCount=3)
            self.access_file_handler.setLevel(logging.DEBUG)
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(logging.INFO)

            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            self.error_file_handler.setFormatter(formatter)
            self.access_file_handler.setFormatter(formatter)
            self.console_handler.setFormatter(formatter)

            self.logger.addHandler(self.error_file_handler)
            self.logger.addHandler(self.access_file_handler)
            self.logger.addHandler(self.console_handler)
            
            self.initialized = True

    def get_logger(self):
        return self.logger




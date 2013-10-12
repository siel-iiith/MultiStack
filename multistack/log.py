import logging
import StringIO

from flask import current_app

class LogStream(StringIO.StringIO):

    def add_logger(self, logger):
        self.logger = logger

    def write(self, data):
        """
        write string to logger
        """
        self.logger.info(data)

def set_prefixed_format(prefix):
    """
    It updates the Handler's formatter to add a prefix to the
    logrecord.
    """

    formatter = logging.Formatter("{0} - %(message)s".format(prefix))
    # Updating the formatter of SysLogHandler
    handler = current_app.logger.handlers[-1].setFormatter(formatter)

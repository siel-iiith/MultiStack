import logging
import StringIO

from flask import current_app

class MyStream(StringIO.StringIO):

    def write(self, data):
        """
        write string to logger
        """
        current_app.logger.info(data)

def set_prefixed_format(prefix):
    """
    It updates the Handler's formatter to add a prefix to the
    logrecord.
    """

    formatter = logging.Formatter("{0} - %(message)s".format(prefix))
    handler = logging.handlers.SysLogHandler(address = '/dev/log')
    handler.setFormatter(formatter)

    # This step removes the previous SysLogHandler in the list. If not
    # removed, multiple log messages will be logged with different
    # prefixes.

    current_app.logger.handlers.pop()
    current_app.logger.addHandler(handler)
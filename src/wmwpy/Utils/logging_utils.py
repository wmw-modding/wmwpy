import io
import logging
import traceback


def log_exception():
    fileio = io.StringIO()
    traceback.print_exc(file = fileio)

    logging.error(fileio.getvalue())

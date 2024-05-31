import logging
import sys
from typing import Optional

import pygitguardian


LOG_FORMAT = "%(asctime)s %(levelname)s %(process)x:%(thread)x %(name)s:%(funcName)s:%(lineno)d %(message)s"

logger = logging.getLogger(__name__)


_log_handler = None


def disable_logs() -> None:
    """By default, disable all logs, because when an error occurs we log an error
    message and also print a human-friendly message using display_errors(). If we don't
    disable all logs, then error logs are printed, resulting in the error being shown
    twice.
    """
    logging.disable()


def set_log_handler(handler: logging.Handler) -> None:
    """Defines the log handler to use in case --debug is set. Used by RichGGShieldUI to
    override the StreamHandler instance used by default"""
    global _log_handler
    _log_handler = handler


def setup_debug_logs(
    *,
    filename: Optional[str] = None,
) -> None:
    """Configure Python logger to log to stderr if filename is None, or to filename if
    it's set.
    """
    root = logging.getLogger()

    # Re-enable logging, reverting the call to disable_logs()
    logging.disable(logging.NOTSET)

    # Define the minimum log level. We also silence charset_normalizer because its debug
    # output does not bring much.
    root.setLevel(logging.DEBUG)
    logging.getLogger("charset_normalizer").setLevel(logging.WARNING)

    # Define log handler
    if filename and filename != "-":
        handler = logging.FileHandler(filename)
        handler.setFormatter(logging.Formatter(LOG_FORMAT))
    elif _log_handler:
        handler = _log_handler
    else:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(LOG_FORMAT))

    root.addHandler(handler)

    # Log some startup information
    logger.debug("args=%s", sys.argv)
    logger.debug("py-gitguardian=%s", pygitguardian.__version__)

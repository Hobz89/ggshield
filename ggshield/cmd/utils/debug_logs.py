import logging
import sys
from typing import Optional

import pygitguardian

from ggshield.utils.logger import Logger


LOG_FORMAT = "%(levelname)s: %(message)s"
DEBUG_LOG_FORMAT = "%(asctime)s %(levelname)s %(process)x:%(thread)x %(name)s:%(funcName)s:%(lineno)d %(message)s"

logger = Logger(__name__)


_logged_debug_info = False
_last_set_log_level = logging.WARNING


def setup_logs(*, level: int = logging.INFO, filename: Optional[str] = None) -> None:
    global _logged_debug_info, _last_set_log_level

    # Prevent reducing log level: using `--debug --verbose` should produce debug logs
    if level > _last_set_log_level:
        return
    _last_set_log_level = level

    log_format = LOG_FORMAT if level > logging.DEBUG else DEBUG_LOG_FORMAT
    logging.basicConfig(filename=filename, level=level, format=log_format, force=True)

    if level == logging.DEBUG and not _logged_debug_info:
        logger.debug("args=%s", sys.argv)
        logger.debug("py-gitguardian=%s", pygitguardian.__version__)
        _logged_debug_info = True

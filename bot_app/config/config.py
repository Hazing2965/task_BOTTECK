import logging
from logging.handlers import RotatingFileHandler
import os

async def setup_logger():
    LOG_DIR = "/var/log/bot_app"
    os.makedirs(LOG_DIR, exist_ok=True)
    
    logger = logging.getLogger('bot_app')
    logger.setLevel(logging.DEBUG)

    logger.handlers.clear()

    log_format = logging.Formatter(
        "[{asctime}] #{levelname:8} {filename}:{lineno} - {name} - \"{message}\"",
        style="{"
    )

    # Консольный вывод
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Файловый обработчик для DEBUG
    debug_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'debug.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(log_format)
    logger.addHandler(debug_handler)

    # Файловый обработчик для INFO
    info_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'info.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(log_format)
    logger.addHandler(info_handler)

    # Файловый обработчик для ERROR
    error_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, 'error.log'),
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(log_format)
    logger.addHandler(error_handler)





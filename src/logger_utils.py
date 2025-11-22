import logging
import os
from datetime import datetime

# ---------- Logger Utility for InteraVoice ----------

# Create logs directory if not exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Daily rotating log file
LOG_FILE = os.path.join(LOG_DIR, f"interavoice_{datetime.now().date()}.log")


def get_logger(name: str = "InteraVoice"):
    """
    Returns a logger configured to write to log file + console.
    Format: TIMESTAMP | LEVEL | MODULE | MESSAGE
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Prevent double handlers
    if not logger.handlers:
        # File log
        file_handler = logging.FileHandler(LOG_FILE)
        file_handler.setLevel(logging.INFO)

        # Console log
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Format pattern
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

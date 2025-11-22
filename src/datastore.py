import json
from pathlib import Path
from logger_utils import get_logger

logger = get_logger("DataStore")

BASE_DIR = Path(__file__).resolve().parent.parent  # project root


class DataStore:
    """Loads and provides access to FAQ data from JSON file."""

    def __init__(self, file_path=None):
        if file_path is None:
            file_path = BASE_DIR / "data" / "faqs.json"

        self.file_path = file_path
        logger.info("Loading FAQ data from: %s", file_path)

        self._faqs = self._load()

    def _load(self):
        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                logger.info("Loaded %d FAQ entries", len(data))
                return data
        except FileNotFoundError:
            logger.error("FAQ file not found: %s", self.file_path)
            return []
        except Exception as e:
            logger.error("Error reading FAQ file: %s", e)
            return []

    def all_faqs(self):
        return self._faqs

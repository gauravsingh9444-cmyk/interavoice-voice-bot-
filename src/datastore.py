'''
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
'''
import json
from pathlib import Path
import os
from logger_utils import get_logger

logger = get_logger("DataStore")

# Get the directory where datastore.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

class DataStore:
    """Loads and provides access to FAQ data from JSON file."""

    def __init__(self, file_path=None):
        if file_path is None:
            # Look for faqs.json in data folder relative to current directory
            file_path = os.path.join(current_dir, "data", "faqs.json")
        
        self.file_path = Path(file_path)
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
            # Create a sample FAQ file if it doesn't exist
            sample_data = [
                {
                    "question": "What is InteraVoice?",
                    "answer": "InteraVoice is a voice-enabled AI assistant designed to help with customer support and FAQs."
                },
                {
                    "question": "How much does it cost?",
                    "answer": "Please contact our sales team for pricing information."
                }
            ]
            # Create directory if it doesn't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            with self.file_path.open("w", encoding="utf-8") as f:
                json.dump(sample_data, f, indent=2)
            logger.info("Created sample FAQ file with %d entries", len(sample_data))
            return sample_data
        except Exception as e:
            logger.error("Error reading FAQ file: %s", e)
            return []

    def all_faqs(self):
        return self._faqs
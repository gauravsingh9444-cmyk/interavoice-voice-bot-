from difflib import SequenceMatcher
from typing import List, Dict, Optional
from logger_utils import get_logger

logger = get_logger("IntentEngine")


class IntentEngine:
    """
    Simple intent matching engine:
    Uses string similarity to find the closest matching FAQ.
    """

    def __init__(self, threshold: float = 0.55):
        self.threshold = threshold
        logger.info("IntentEngine initialized with threshold %.2f", threshold)

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def best_match(self, user_text: str, faqs: List[Dict]) -> Optional[Dict]:
        logger.info("Finding intent for: %s", user_text)

        best = None
        best_score = 0.0

        for item in faqs:
            q = item.get("question", "")
            score = self._similarity(user_text, q)

            logger.info("Compared with '%s' | Score %.2f", q, score)

            if score > best_score:
                best_score = score
                best = item

        if best_score >= self.threshold:
            logger.info("Match found: '%s' (score %.2f)", best["question"], best_score)
            return best

        logger.info("No suitable match found for '%s'", user_text)
        return None

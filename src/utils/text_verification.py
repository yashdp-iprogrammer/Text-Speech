import os
from detoxify import Detoxify

TOXICITY_THRESHOLD = float(os.getenv("TOXICITY_THRESHOLD", 0.3))

_model = None

def get_model():
    global _model
    if _model is None:
        _model = Detoxify("original", device="cpu")
    return _model

def verify_text(text: str) -> bool:
    """
    Returns True if text is safe, False if toxic.
    """
    if not text or not text.strip():
        return False

    try:
        model = get_model()
        result = model.predict(text)

        # Check toxicity scores
        for score in result.values():
            if score > TOXICITY_THRESHOLD:
                return False

        return True

    except Exception:
        return False
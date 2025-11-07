# response_evaluator.py

def evaluate_response_confidence(response: str) -> str:
    """
    Returns a confidence score: 'High', 'Medium', or 'Low'
    based on depth, clarity, and signs of evasion or generic phrasing.
    """
    response = response.lower()

    if any(phrase in response for phrase in [
        "i'm not sure", "i haven't used", "i would need to check", "i don't remember"
    ]):
        return "Low"

    if any(phrase in response for phrase in [
        "usually", "standard tools", "depends", "it varies", "i guess"
    ]):
        return "Medium"

    if any(phrase in response for phrase in [
        "in production", "we scaled", "i implemented", "i used", "we deployed"
    ]):
        return "High"

    return "Medium"  # Default fallback


def detect_possible_web_lookup(response: str, latency_seconds: float) -> bool:
    """
    Returns True if the response is likely copied or looked up online.
    Criteria: long latency + generic or formal phrasing.
    """
    response = response.lower()
    generic_signals = [
        "a promise is an object", "event loop is", "etl stands for", "distributed systems are"
    ]

    if latency_seconds > 15 and any(phrase in response for phrase in generic_signals):
        return True

    return False


def summarize_response_quality(response: str, latency_seconds: float) -> dict:
    """
    Returns a summary dict with confidence score and lookup suspicion.
    """
    return {
        "confidence": evaluate_response_confidence(response),
        "possible_web_lookup": detect_possible_web_lookup(response, latency_seconds)
    }

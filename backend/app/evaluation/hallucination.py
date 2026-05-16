ABSTENTION_PHRASES = [
    "i don't have enough information",
    "the context does not provide",
    "cannot answer from the context",
    "not enough information"
]


def detect_abstention(response: str) -> bool:
    response_lower = response.lower()
    return any(phrase in response_lower for phrase in ABSTENTION_PHRASES)


def detect_hallucination(response: str, chunks: list) -> float:
    """
    Returns a score from 0.0 to 1.0.
    0.0 = fully grounded, 1.0 = fully hallucinated.
    Based on inverse word overlap between response and all chunks.
    """

    response_words = set(response.lower().split())

    all_chunk_words = set()

    for chunk in chunks:
        text = chunk["text"] if isinstance(chunk, dict) else chunk.text
        all_chunk_words.update(text.lower().split())

    if not response_words:
        return 1.0

    overlap = response_words.intersection(all_chunk_words)

    return round(1.0 - len(overlap) / len(response_words), 2)

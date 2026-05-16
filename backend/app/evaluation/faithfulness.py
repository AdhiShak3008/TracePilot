def compute_faithfulness(response: str, chunks: list) -> float:
    """
    Returns a score from 0.0 to 1.0.
    Measures what fraction of response words are covered by retrieved chunks.
    """

    response_words = set(response.lower().split())

    all_chunk_words = set()

    for chunk in chunks:
        text = chunk["text"] if isinstance(chunk, dict) else chunk.text
        all_chunk_words.update(text.lower().split())

    if not response_words:
        return 0.0

    covered = response_words.intersection(all_chunk_words)

    return round(len(covered) / len(response_words), 2)

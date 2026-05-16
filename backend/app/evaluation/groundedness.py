STOPWORDS = {
    "the", "is", "a", "an", "to", "of",
    "and", "in", "on", "for", "what", "best", "how"
}


def check_groundedness(response: str, chunks: list) -> bool:

    response_words = set(response.lower().split())

    for chunk in chunks:

        text = chunk["text"] if isinstance(chunk, dict) else chunk.text

        chunk_words = {
            word
            for word in text.lower().split()
            if word not in STOPWORDS
        }

        if len(response_words.intersection(chunk_words)) >= 2:
            return True

    return False

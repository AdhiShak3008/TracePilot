import re
from collections import Counter

STOPWORDS = {"the", "is", "of", "what", "who", "a", "an", "to", "in", "on"}


def tokenize(text: str):

    words = re.findall(r"\b\w+\b", text.lower())

    return [word for word in words if word not in STOPWORDS]


def load_knowledge_base():

    with open("data/knowledge_base.txt", "r", encoding="utf-8") as file:

        text = file.read()

    return text.split("\n")


def score_chunk(chunk: str, query: str):

    chunk_words = tokenize(chunk)
    query_words = tokenize(query)

    chunk_counter = Counter(chunk_words)
    query_counter = Counter(query_words)

    score = 0

    for word in query_counter:

        score += min(query_counter[word], chunk_counter[word])

    return round(score / max(len(query_words), 1), 2)


def retrieve_chunks(query: str, top_k: int = 3):

    chunks = load_knowledge_base()

    scored_chunks = []

    for chunk in chunks:

        if not chunk.strip():
            continue

        score = score_chunk(chunk, query)

        scored_chunks.append({"text": chunk, "score": score})

    scored_chunks.sort(key=lambda x: x["score"], reverse=True)

    top_chunks = scored_chunks[:top_k]

    for i, chunk in enumerate(top_chunks):

        chunk["chunk_id"] = f"chunk_{i}"
        chunk["rank"] = i + 1

    return top_chunks

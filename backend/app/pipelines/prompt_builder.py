def build_prompt(query: str, chunks: list) -> str:

    context = "\n".join(
        chunk["text"] if isinstance(chunk, dict) else chunk.text
        for chunk in chunks
    )

    return f"""Answer ONLY using the context below.
If the answer is not in the context, say: "I don't have enough information to answer this."

Context:
{context}

Question:
{query}"""

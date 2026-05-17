PROMPT_MODES = {

    "strict": """
You are a retrieval-grounded AI assistant.

Answer ONLY using the provided context.

If the answer is not explicitly contained
in the context, say:

"I don't have enough information to answer this."
""",

    "balanced": """
You are a retrieval-grounded AI assistant.

Answer using the provided context.

Reasonable inferences are allowed,
but do not introduce unsupported facts
or fabricate information.

If the context is clearly insufficient,
say you don't have enough information.
""",

    "permissive": """
You are a helpful AI assistant.

Use the context below to help answer
the question.
"""
}


def build_prompt(query: str, chunks: list, mode: str = "strict") -> str:

    context = "\n\n".join(
        chunk["text"] if isinstance(chunk, dict) else chunk.text
        for chunk in chunks
    )

    system_prompt = PROMPT_MODES.get(mode, PROMPT_MODES["strict"])

    return f"""
{system_prompt}

Context:
{context}

Question:
{query}
"""

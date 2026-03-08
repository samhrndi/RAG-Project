# src/utils.py

def build_augmented_query(query: str, msgs: list, n: int = 4) -> str:
    """Prepend the last n conversation exchanges to the query for context."""
    pairs = [
        (msgs[i]["content"], msgs[i+1]["content"])
        for i in range(0, len(msgs) - 1, 2)
        if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant"
    ]
    if not pairs:
        return query
    recent = pairs[-n:]
    history_text = "\n".join(f"Human: {h}\nAssistant: {a}" for h, a in recent)
    return f"Previous conversation:\n{history_text}\n\nCurrent question: {query}"

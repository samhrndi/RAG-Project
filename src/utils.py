# src/utils.py

def build_augmented_query(query: str, msgs: list, recent: int = 2, max_older: int = 2) -> str:
    """
    Build a context-augmented query using sliding window + response compression.

    Strategy:
      - Last `recent` exchanges: kept verbatim
      - Up to `max_older` older exchanges: assistant responses truncated to 120 chars
      - Anything beyond that window is dropped entirely

    This keeps history tokens bounded regardless of conversation length.
    A 10-turn conversation costs roughly the same as a 4-turn one.
    """
    pairs = [
        (msgs[i]["content"], msgs[i+1]["content"])
        for i in range(0, len(msgs) - 1, 2)
        if msgs[i]["role"] == "user" and msgs[i+1]["role"] == "assistant"
    ]
    if not pairs:
        return query

    verbatim = pairs[-recent:]
    older = pairs[-(recent + max_older):-recent] if len(pairs) > recent else []

    lines = []
    for h, a in older:
        lines.append(f"Human: {h}\nAssistant: {a[:120]}...")
    for h, a in verbatim:
        lines.append(f"Human: {h}\nAssistant: {a}")

    history_text = "\n".join(lines)
    return f"Previous conversation:\n{history_text}\n\nCurrent question: {query}"

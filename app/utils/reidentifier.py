import re
from collections import defaultdict, deque
from typing import Dict

def _normalize_label(label):
    return (label or "").strip().upper()

def _build_label_queues(entities):
    buckets: Dict[str, deque] = defaultdict(deque)

    def sort_key(e):
        return e.get("start", float("inf"))

    try:
        entities_sorted = sorted(entities, key=sort_key)
    except Exception:
        entities_sorted = entities

    for ent in entities_sorted:
        label = _normalize_label(ent.get("label", ""))
        text = (ent.get("text") or "").strip()
        if not label or not text:
            continue
        buckets[label].append(text)
    return buckets

def reidentify_text(anonymized_text, entities_json):
    if not anonymized_text:
        return anonymized_text

    entities = entities_json.get("entities", []) if isinstance(entities_json, dict) else []
    label_queues = _build_label_queues(entities)

    pattern = re.compile(r"\[([A-Za-z][A-Za-z0-9 _\-\.\/]*)\s*(?:_(\d+))?\]")

    def _replace(match: re.Match) -> str:
        raw_label = match.group(1) or ""
        index_str = match.group(2)
        norm_label = _normalize_label(raw_label)

        if index_str is not None:
            try:
                idx = int(index_str)
                values = list(label_queues.get(norm_label, []))
                if 1 <= idx <= len(values):
                    return values[idx - 1]
                else:
                    return match.group(0)
            except Exception:
                return match.group(0)

        q = label_queues.get(norm_label)
        if q and len(q) > 0:
            return q.popleft()

        return match.group(0)

    return pattern.sub(_replace, anonymized_text)

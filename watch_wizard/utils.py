from dataclasses import is_dataclass, asdict
import json

def distinct(sequence: list, key: str):
    seen = set()
    for s in sequence:
        value = getattr(s, key)
        if not value in seen:
            seen.add(value)
            yield s
    return seen

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if is_dataclass(o):
                return asdict(o)
            if hasattr(o, 'to_json'):
                return o.to_json()
            return super().default(o)
        except:
            return o.__dict__
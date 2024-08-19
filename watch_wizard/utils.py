from pydantic import BaseModel, SecretStr
from dataclasses import is_dataclass, asdict
import json


def distinct(sequence: list, key: str):
    seen = set()
    for s in sequence:
        value = getattr(s, key)
        if value not in seen:
            seen.add(value)
            yield s
    return seen


def enhanced_json_serializer(obj) -> str:
    return json.dumps(obj, cls=EnhancedJSONEncoder)


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, SecretStr):
            return str(o)
        if isinstance(o, BaseModel):
            return o.model_dump()
        if hasattr(o, 'to_json'):
            return o.to_json()
        if is_dataclass(o):
            return asdict(o)
        return super().default(o)
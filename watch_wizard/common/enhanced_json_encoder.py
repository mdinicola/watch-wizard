from dataclasses import is_dataclass, asdict
import json

class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        try:
            if is_dataclass(o):
                return asdict(o)
            return super().default(o)
        except TypeError:
            return o.__dict__
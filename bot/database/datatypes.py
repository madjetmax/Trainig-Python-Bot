import json
from sqlalchemy.types import TypeDecorator, Text

class CustomJSON(TypeDecorator):
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, ensure_ascii=False)  # ASCII encoding
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return None
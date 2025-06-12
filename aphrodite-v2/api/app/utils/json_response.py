"""
Custom JSON Response with datetime serialization support
"""

import json
from datetime import datetime
from typing import Any, Dict
from fastapi.responses import JSONResponse as FastAPIJSONResponse


class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JSONResponse(FastAPIJSONResponse):
    """Custom JSONResponse that handles datetime serialization"""
    
    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            cls=DateTimeEncoder,
        ).encode("utf-8")

from __future__ import annotations

import json
from typing import Any, Dict

def load_wireframe(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

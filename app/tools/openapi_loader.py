from __future__ import annotations

import json
import os
from typing import Any, Dict
import requests
import yaml

def load_openapi(path_or_url: str) -> Dict[str, Any]:
    text = _read_text(path_or_url)
    # JSON first
    try:
        return json.loads(text)
    except Exception:
        pass
    # YAML
    return yaml.safe_load(text)

def _read_text(path_or_url: str) -> str:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        r = requests.get(path_or_url, timeout=30)
        r.raise_for_status()
        return r.text
    with open(path_or_url, "r", encoding="utf-8") as f:
        return f.read()

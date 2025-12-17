from __future__ import annotations

from typing import Any, Dict
import requests

def load_figma_minimal(file_key: str, token: str) -> Dict[str, Any]:
    # Minimal extraction: list pages + basic structure. Figma API response is large.
    headers = {"X-Figma-Token": token}
    url = f"https://api.figma.com/v1/files/{file_key}"
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    doc = data.get("document", {})

    pages = []
    children = (doc.get("children") or [])
    for child in children:
        if child.get("type") == "CANVAS":
            pages.append({"id": child.get("id"), "name": child.get("name"), "type": child.get("type")})
    return {
        "name": data.get("name"),
        "pages": pages,
        "raw": {"lastModified": data.get("lastModified")},
    }

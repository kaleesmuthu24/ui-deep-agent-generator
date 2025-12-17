from __future__ import annotations

import os

def _read(name: str) -> str:
    here = os.path.dirname(__file__)
    p = os.path.join(here, name)
    with open(p, "r", encoding="utf-8") as f:
        return f.read()

def load_prompt_bundle():
    return {
        "system": _read("system_prompt.md"),
        "skills": _read("skills.md"),
        "ui_spec_prompt": _read("ui_spec_prompt.md"),
        "react_codegen_prompt": _read("react_codegen_prompt.md"),
        "playwright_prompt": _read("playwright_prompt.md"),
    }

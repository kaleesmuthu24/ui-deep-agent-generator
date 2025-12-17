from __future__ import annotations

import json
from typing import Dict, Any

def _baseline_ui_spec(source_payload: Dict[str, Any], theme: Dict[str, Any], app_name: str) -> Dict[str, Any]:
    kind = source_payload["kind"]
    data = source_payload["data"]

    # A pragmatic baseline: produce 2-3 pages even without LLM.
    pages = []
    if kind == "wireframe":
        pages = data.get("pages", [])
    elif kind == "openapi":
        # infer resource groups from tags
        paths = data.get("paths", {}) or {}
        tags = {}
        for pth, ops in paths.items():
            if not isinstance(ops, dict):
                continue
            for method, op in ops.items():
                if method.lower() not in ("get","post","put","patch","delete"):
                    continue
                t = (op or {}).get("tags") or ["API"]
                for tag in t:
                    tags.setdefault(tag, []).append({"path": pth, "method": method.lower(), "operation": op or {}})
        # create a page per tag
        for tag, items in list(tags.items())[:8]:
            # choose up to 6 operations
            sections = []
            for it in items[:6]:
                op = it["operation"]
                op_id = op.get("operationId") or f"{it['method']}_{it['path'].strip('/').replace('/','_')}"
                title = op.get("summary") or op_id
                if it["method"] == "get":
                    sections.append({"type": "table", "title": title, "source": {"kind": "openapi", "operationId": op_id}})
                else:
                    sections.append({"type": "form", "title": title, "source": {"kind": "openapi", "operationId": op_id}})
            pages.append({"name": tag, "route": f"/{tag.lower().replace(' ','-')}", "sections": sections})
        if not pages:
            pages = [{"name": "API", "route": "/api", "sections": [{"type":"table","title":"Operations","source":{"kind":"openapi","operationId":"__all__"}}]}]
    elif kind == "figma":
        # minimal: each figma page becomes a route
        fig_pages = data.get("pages", [])
        for pg in fig_pages[:8]:
            pages.append({"name": pg.get("name","Page"), "route": f"/{pg.get('name','page').lower().replace(' ','-')}", "sections":[{"type":"layout","title":pg.get("name","Page"),"source":{"kind":"figma","nodeId":pg.get("id")}}]})
        if not pages:
            pages = [{"name":"Home","route":"/","sections":[{"type":"layout","title":"Home","source":{"kind":"figma","nodeId":"root"}}]}]

    return {
        "appName": app_name,
        "theme": {"name": theme.get("name", "OrgTheme")},
        "source": {"kind": kind},
        "pages": pages,
    }

def build_ui_spec(llm, prompts: Dict[str,str], source_payload: Dict[str, Any], theme: Dict[str, Any], app_name: str) -> Dict[str, Any]:
    baseline = _baseline_ui_spec(source_payload, theme, app_name)

    # If no LLM, return baseline
    if llm is None:
        return baseline

    # LLM refinement: enforce schemas, better grouping, add empty states, etc.
    system = prompts["system"]
    skills = prompts["skills"]
    ui_spec_prompt = prompts["ui_spec_prompt"]

    payload = {
        "baseline": baseline,
        "source_payload": source_payload,
        "theme_tokens": theme,
    }

    msg = f"""{ui_spec_prompt}

# INPUT (JSON)
{json.dumps(payload, indent=2)}
"""

    try:
        resp = llm.invoke([
            {"role":"system","content": system + "\n\n" + skills},
            {"role":"user","content": msg},
        ])
        text = getattr(resp, "content", None) or str(resp)
        # Expect a JSON object in the output
        ui_spec = json.loads(_extract_json(text))
        return ui_spec
    except Exception:
        # Fail safe: baseline
        return baseline

def _extract_json(text: str) -> str:
    # naive: first {...} block
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start:end+1]
    raise ValueError("No JSON found")

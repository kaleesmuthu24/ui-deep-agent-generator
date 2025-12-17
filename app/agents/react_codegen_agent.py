from __future__ import annotations

import json
from typing import Dict, Any

from app.tools.react_templates import base_vite_template_files, materialize_routes, infer_openapi_operations

def generate_react_app(
    llm,
    prompts: Dict[str,str],
    ui_spec: Dict[str, Any],
    theme: Dict[str, Any],
    app_name: str,
    api_base_url: str,
    with_tests: bool,
) -> Dict[str, str]:
    # Start from deterministic template + inferred routes.
    file_map: Dict[str, str] = {}
    file_map.update(base_vite_template_files(app_name=app_name))
    file_map.update(materialize_routes(ui_spec=ui_spec))

    # Generate OpenAPI operation map if source is openapi OR wireframe uses openapi sources
    ops = infer_openapi_operations(ui_spec)
    file_map["src/api/operations.ts"] = ops["operations_ts"]
    file_map["src/api/types.ts"] = ops["types_ts"]
    file_map["src/api/http.ts"] = ops["http_ts"].replace("__API_BASE_URL__", api_base_url)

    # Theme tokens -> theme.css
    file_map["src/styles/theme.css"] = _theme_css(theme)

    # If no LLM, done.
    if llm is None:
        file_map["GENERATED_NOTES.md"] = _notes(ui_spec, theme, llm_enabled=False)
        return file_map

    # LLM pass: improve layout + copy, without changing build config
    system = prompts["system"]
    skills = prompts["skills"]
    react_prompt = prompts["react_codegen_prompt"]

    req = {
        "ui_spec": ui_spec,
        "theme_tokens": theme,
        "api_base_url": api_base_url,
        "constraints": {
            "vite_ts": True,
            "no_inline_styles": True,
            "prefer_small_components": True,
            "a11y": True,
        },
        "current_files_index": sorted(list(file_map.keys())),
        "instructions": "Return a JSON object mapping file paths to full file contents. Only include files you want to add/replace."
    }

    msg = f"""{react_prompt}

# INPUT (JSON)
{json.dumps(req, indent=2)}
"""

    try:
        resp = llm.invoke([
            {"role":"system","content": system + "\n\n" + skills},
            {"role":"user","content": msg},
        ])
        text = getattr(resp, "content", None) or str(resp)
        patch = json.loads(_extract_json(text))
        if isinstance(patch, dict):
            for k,v in patch.items():
                if isinstance(k, str) and isinstance(v, str):
                    file_map[k] = v
    except Exception:
        pass

    file_map["GENERATED_NOTES.md"] = _notes(ui_spec, theme, llm_enabled=True)
    return file_map

def _extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start:end+1]
    raise ValueError("No JSON found")

def _theme_css(theme: Dict[str, Any]) -> str:
    tokens = theme.get("tokens", {})
    colors = tokens.get("colors", {})
    typography = tokens.get("typography", {})
    radius = tokens.get("radius", {})
    spacing = tokens.get("spacing", {})

    # minimal CSS variables
    def g(d, k, default):
        return d.get(k, default) if isinstance(d, dict) else default

    return f"""/* Generated from org-theme.json */
:root {{
  --brand-primary: {g(colors,'primary','#2f6fed')};
  --brand-secondary: {g(colors,'secondary','#6b7280')};
  --brand-accent: {g(colors,'accent','#10b981')};
  --bg: {g(colors,'background','#0b1220')};
  --surface: {g(colors,'surface','#111827')};
  --text: {g(colors,'text','#e5e7eb')};
  --muted: {g(colors,'muted','#9ca3af')};
  --border: {g(colors,'border','#1f2937')};
  --danger: {g(colors,'danger','#ef4444')};

  --font-sans: {g(typography,'fontFamily','ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto')};
  --font-mono: {g(typography,'monoFamily','ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas')};
  --base-size: {g(typography,'baseSize','16px')};

  --radius-sm: {g(radius,'sm','8px')};
  --radius-md: {g(radius,'md','14px')};
  --radius-lg: {g(radius,'lg','18px')};

  --space-2: {g(spacing,'2','8px')};
  --space-3: {g(spacing,'3','12px')};
  --space-4: {g(spacing,'4','16px')};
  --space-6: {g(spacing,'6','24px')};
}}

html, body {{
  height: 100%;
}}

body {{
  margin: 0;
  font-family: var(--font-sans);
  font-size: var(--base-size);
  background: var(--bg);
  color: var(--text);
}}

a {{
  color: inherit;
}}

.container {{
  max-width: 1120px;
  margin: 0 auto;
  padding: var(--space-6);
}}

.card {{
  background: color-mix(in oklab, var(--surface) 92%, black 8%);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: 0 10px 25px rgba(0,0,0,.25);
}}

.btn {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--brand-primary);
  color: white;
  font-weight: 600;
  cursor: pointer;
}}

.btn.secondary {{
  background: transparent;
  color: var(--text);
}}

.input, select, textarea {{
  width: 100%;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: color-mix(in oklab, var(--surface) 85%, black 15%);
  color: var(--text);
}}

.label {{
  display: block;
  color: var(--muted);
  font-size: 13px;
  margin-bottom: 6px;
}}

.grid {{
  display: grid;
  gap: var(--space-4);
}}

.grid.two {{
  grid-template-columns: repeat(2, minmax(0, 1fr));
}}

.nav {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) 0;
}}

.navlinks {{
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}}

.pill {{
  padding: 8px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--text);
  background: transparent;
}}

.pill.active {{
  background: color-mix(in oklab, var(--brand-primary) 30%, transparent 70%);
  border-color: color-mix(in oklab, var(--brand-primary) 40%, var(--border) 60%);
}}
"""

def _notes(ui_spec: Dict[str, Any], theme: Dict[str, Any], llm_enabled: bool) -> str:
    return f"""# Generated UI Notes

- App: **{ui_spec.get('appName','GeneratedUI')}**
- Theme: **{theme.get('name','OrgTheme')}**
- LLM Enhanced: **{llm_enabled}**

## Pages
{json.dumps(ui_spec.get('pages', []), indent=2)}

## Next steps
- Update `src/api/http.ts` base URL if needed.
- Replace placeholder components with your org design system if you have one.
- If you want the generator to follow stricter org rules, edit `app/prompts/skills.md`.
"""

from __future__ import annotations

import os
import shutil
from typing import Dict, Any, List, Tuple

def template_root_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "..", "templates", "react_vite_ts")

def copy_template_dir(src: str, dst: str, replacements: Dict[str,str]) -> None:
    shutil.copytree(src, dst, dirs_exist_ok=True)
    # Replace tokens in text files
    for root, _, files in os.walk(dst):
        for fn in files:
            if fn.endswith((".ts",".tsx",".json",".md",".html",".css",".mjs",".cjs",".txt",".yml",".yaml")):
                p = os.path.join(root, fn)
                try:
                    with open(p, "r", encoding="utf-8") as f:
                        txt = f.read()
                    for k,v in replacements.items():
                        txt = txt.replace(k, v)
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(txt)
                except Exception:
                    pass

def base_vite_template_files(app_name: str) -> Dict[str,str]:
    # These override/extend the template
    return {
        "src/styles/theme.css": "/* theme injected later */\n",
        "src/styles/app.css": """@import './theme.css';\n\n/* app-level helpers */\n""",
    }

def materialize_routes(ui_spec: Dict[str, Any]) -> Dict[str, str]:
    pages = ui_spec.get("pages", []) or []
    routes = []
    page_files: Dict[str,str] = {}

    for pg in pages:
        name = pg.get("name","Page")
        route = pg.get("route","/")
        comp = _pascal(name) + "Page"
        routes.append((route, comp, name, pg))
        page_files[f"src/pages/{comp}.tsx"] = _page_component(comp, name, pg)

    # Router + Nav
    page_files["src/router.tsx"] = _router(routes)
    page_files["src/components/Nav.tsx"] = _nav(routes)
    page_files["src/pages/HomePage.tsx"] = _home(ui_spec)

    return page_files

def infer_openapi_operations(ui_spec: Dict[str, Any]) -> Dict[str, str]:
    # We generate a minimal operations layer. The generator does NOT need the full spec at runtime.
    # Instead, ui-spec should reference operationIds; you can hand-edit operations later.
    operations = []
    pages = ui_spec.get("pages", []) or []
    for pg in pages:
        for sec in (pg.get("sections") or []):
            src = (sec.get("source") or {})
            if src.get("kind") == "openapi":
                op_id = src.get("operationId")
                if op_id and op_id not in operations:
                    operations.append(op_id)

    operations_ts = """import { http } from './http';\n\n// NOTE: These are stubs inferred from ui-spec.\n// Replace with real endpoints if needed.\n\n"""
    for op in operations:
        fn = _camel(op)
        operations_ts += f"export async function {fn}(payload?: unknown) {{\n  // TODO: map operationId '{op}' to a real endpoint\n  return http.request('{{METHOD}}', '/__TODO__', payload);\n}}\n\n"

    types_ts = """// Minimal shared types. Extend per operation.\nexport type ApiResult<T> = { ok: true; data: T } | { ok: false; error: string };\n"""

    http_ts = """export const API_BASE_URL = process.env.VITE_API_BASE_URL || '__API_BASE_URL__';\n\nexport const http = {\n  async request(method: string, path: string, body?: unknown) {\n    const url = API_BASE_URL.replace(/\/$/, '') + path;\n    const init: RequestInit = {\n      method,\n      headers: { 'Content-Type': 'application/json' },\n    };\n    if (body !== undefined) init.body = JSON.stringify(body);\n    const res = await fetch(url, init);\n    const text = await res.text();\n    const json = (() => {\n      try { return JSON.parse(text); } catch { return text; }\n    })();\n    if (!res.ok) throw new Error(typeof json === 'string' ? json : JSON.stringify(json));\n    return json;\n  }\n};\n"""

    return {"operations_ts": operations_ts, "types_ts": types_ts, "http_ts": http_ts}

def _page_component(comp: str, title: str, page: Dict[str, Any]) -> str:
    sections = page.get("sections", []) or []
    sec_blocks = []
    for i, sec in enumerate(sections):
        st = sec.get("type","section")
        t = sec.get("title", f"Section {i+1}")
        src = sec.get("source", {}) or {}
        if st == "table":
            sec_blocks.append(f"""<div className="card">\n  <h2>{t}</h2>\n  <TableSection title={t} operationId="{src.get('operationId','')}" />\n</div>""")
        elif st == "form":
            sec_blocks.append(f"""<div className="card">\n  <h2>{t}</h2>\n  <FormSection title={t} operationId="{src.get('operationId','')}" />\n</div>""")
        else:
            sec_blocks.append(f"""<div className="card">\n  <h2>{t}</h2>\n  <p style={{ marginTop: 8 }}>This section is a placeholder. Refine it via wireframe or LLM.</p>\n</div>""")

    sec_render = "\n\n".join(sec_blocks) if sec_blocks else "<div className='card'><p>No sections defined.</p></div>"

    return f"""import Nav from '../components/Nav';\nimport {{ FormSection }} from '../components/sections/FormSection';\nimport {{ TableSection }} from '../components/sections/TableSection';\n\nexport default function {comp}() {{\n  return (\n    <div className="container">\n      <Nav />\n      <h1>{title}</h1>\n      <div className="grid">\n        {sec_render}\n      </div>\n    </div>\n  );\n}}\n"""

def _router(routes: List[Tuple[str,str,str,Dict[str,Any]]]) -> str:
    imports = ["import { createBrowserRouter, RouterProvider } from 'react-router-dom';",
               "import HomePage from './pages/HomePage';"]
    elems = ["{ path: '/', element: <HomePage /> }"]
    for route, comp, _, _ in routes:
        if route == "/":
            continue
        imports.append(f"import {comp} from './pages/{comp}';")
        elems.append(f"{{ path: '{route}', element: <{comp} /> }}")

    return "\n".join(imports) + "\n\n" + "\n".join([
        "const router = createBrowserRouter([",
        "  " + ",\n  ".join(elems),
        "]);",
        "",
        "export default function AppRouter(){",
        "  return <RouterProvider router={router} />;",
        "}",
        ""
    ])

def _nav(routes: List[Tuple[str,str,str,Dict[str,Any]]]) -> str:
    links = []
    for route, _, name, _ in routes:
        if route == "/":
            continue
        links.append(f"<a className=\"pill\" href=\"{route}\">{name}</a>")
    links_render = "\n          ".join(links) if links else ""
    return f"""export default function Nav() {{\n  return (\n    <header className="nav">\n      <div>\n        <strong>__APP_NAME__</strong>\n        <div style={{ color: 'var(--muted)', fontSize: 13, marginTop: 4 }}>Themed UI generated from your spec</div>\n      </div>\n      <nav className="navlinks">\n        <a className="pill active" href="/">Home</a>\n        {links_render}\n      </nav>\n    </header>\n  );\n}}\n"""

def _home(ui_spec: Dict[str, Any]) -> str:
    pages = ui_spec.get("pages", []) or []
    cards = []
    for pg in pages[:8]:
        route = pg.get("route","/")
        name = pg.get("name","Page")
        if route == "/":
            continue
        cards.append(f"""<a className="card" href="{route}" style={{ textDecoration: 'none' }}>\n  <h2 style={{ marginTop: 0 }}>{name}</h2>\n  <p style={{ color: 'var(--muted)' }}>Go to {route}</p>\n</a>""")
    cards_render = "\n\n".join(cards) if cards else "<div className='card'><p>No pages inferred.</p></div>"

    return f"""import Nav from '../components/Nav';\n\nexport default function HomePage() {{\n  return (\n    <div className="container">\n      <Nav />\n      <h1>Home</h1>\n      <p style={{ color: 'var(--muted)' }}>Generated routes based on your OpenAPI / wireframe / Figma input.</p>\n      <div className="grid two">\n        {cards_render}\n      </div>\n    </div>\n  );\n}}\n"""

def _pascal(s: str) -> str:
    parts = [p for p in _clean(s).split('-') if p]
    return ''.join(p[:1].upper() + p[1:] for p in parts) or "Page"

def _camel(s: str) -> str:
    p = _pascal(s)
    return p[:1].lower() + p[1:]

def _clean(s: str) -> str:
    s = (s or "page").strip().lower()
    s = ''.join(ch if ch.isalnum() else '-' for ch in s)
    s = '-'.join([p for p in s.split('-') if p])
    return s

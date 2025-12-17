from __future__ import annotations

import json
from typing import Dict, Any

def generate_playwright_tests(llm, prompts: Dict[str,str], ui_spec: Dict[str, Any], app_name: str) -> Dict[str, str]:
    # Default: simple smoke tests (no LLM required)
    baseline = {
        "tests/smoke.spec.ts": _baseline_smoke(ui_spec),
        "playwright.config.ts": _pw_config(),
        "tests/README.md": _tests_readme(),
    }
    if llm is None:
        return baseline

    system = prompts["system"]
    skills = prompts["skills"]
    pw_prompt = prompts["playwright_prompt"]

    req = {
        "ui_spec": ui_spec,
        "constraints": {
            "baseURL": "http://localhost:5173",
            "no_flaky_waits": True,
            "prefer_role_selectors": True
        },
        "expected_output": "Return JSON mapping file paths to file contents for Playwright tests."
    }
    msg = f"""{pw_prompt}

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
                    baseline[k] = v
    except Exception:
        pass

    return baseline

def _extract_json(text: str) -> str:
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start:end+1]
    raise ValueError("No JSON found")

def _baseline_smoke(ui_spec: Dict[str, Any]) -> str:
    pages = ui_spec.get("pages", [])
    checks = []
    for pg in pages[:6]:
        route = pg.get("route","/")
        name = pg.get("name","Page")
        checks.append((name, route))

    lines = [
        "import { test, expect } from '@playwright/test';",
        "",
        "test.describe('smoke', () => {",
        "  test('home loads', async ({ page }) => {",
        "    await page.goto('/');",
        "    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();",
        "  });",
    ]
    for name, route in checks:
        if route == "/":
            continue
        lines += [
            "",
            f"  test('{name} page loads', async ({{ page }}) => {{",
            f"    await page.goto('{route}');",
            "    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();",
            "  });",
        ]
    lines += ["});", ""]
    return "\n".join(lines)

def _pw_config() -> str:
    return """import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  use: {
    baseURL: process.env.PW_BASE_URL || 'http://localhost:5173',
    headless: true
  }
});
"""

def _tests_readme() -> str:
    return """# Playwright Tests

Run the UI first:
```bash
npm run dev
```

Then in another terminal:
```bash
npx playwright install --with-deps
npx playwright test
```

If your dev server runs on a different port, set:
```bash
PW_BASE_URL=http://localhost:5174 npx playwright test
```
"""

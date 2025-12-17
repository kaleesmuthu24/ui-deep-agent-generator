# UI Deep Agent Generator (LangChain + "Claude skills.md" style)

This project generates a **React (Vite + TypeScript)** app from:
- **OpenAPI (Swagger)** spec (YAML/JSON), OR
- **Figma** file (basic node + component extraction), OR
- A light **wireframe JSON** you provide,

…and applies your **Org theme** (design tokens) to the output.

It’s built as a small **multi-step “deep agent”** pipeline:
1) Parse input (OpenAPI/Figma/wireframe)  
2) Produce an intermediate `ui-spec.json`  
3) Generate a themed React app from `ui-spec.json`  
4) Generate Playwright tests (optional)  

If you have an LLM configured, the agent will improve layout + copy.  
If you **don’t**, it still produces a working baseline app using templates + heuristics.

---

## 1) Setup

### Python
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Node (for the generated React app)
Install Node 18+ (or 20+).

---

## 2) Configure LLM (optional but recommended)

Copy `.env.example` to `.env` and set ONE provider:

- OpenRouter (easy, supports Claude/GPT):
  - `LLM_PROVIDER=openrouter`
  - `OPENROUTER_API_KEY=...`
  - `OPENROUTER_MODEL=anthropic/claude-3.5-sonnet` (example)

- OpenAI:
  - `LLM_PROVIDER=openai`
  - `OPENAI_API_KEY=...`
  - `OPENAI_MODEL=gpt-4.1-mini` (example)

- Anthropic:
  - `LLM_PROVIDER=anthropic`
  - `ANTHROPIC_API_KEY=...`
  - `ANTHROPIC_MODEL=claude-3-5-sonnet-20241022` (example)

> If no provider is configured, the generator runs in **offline baseline mode**.

---

## 3) Run (OpenAPI → React)

```bash
python -m app.main generate   --openapi examples/petstore.yaml   --org-theme examples/org-theme.json   --output out/petstore-ui   --app-name PetstoreUI
```

Then run the generated UI:

```bash
cd out/petstore-ui
npm install
npm run dev
```

---

## 4) Run (Figma → React) [basic extraction]

```bash
python -m app.main generate   --figma-file-key YOUR_FILE_KEY   --figma-token YOUR_FIGMA_TOKEN   --org-theme examples/org-theme.json   --output out/figma-ui   --app-name FigmaUI
```

> Figma extraction is intentionally conservative: it tries to infer pages/sections/components.
> For best results, combine it with a “wireframe.json” you export manually (see below).

---

## 5) Wireframe JSON (recommended for precision)

You can supply a `wireframe.json` in this format:
```json
{
  "appName": "MyApp",
  "pages": [
    {
      "name": "Accounts",
      "route": "/accounts",
      "sections": [
        { "type": "table", "title": "Accounts", "source": { "kind": "openapi", "operationId": "listAccounts" } },
        { "type": "form", "title": "Create Account", "source": { "kind": "openapi", "operationId": "createAccount" } }
      ]
    }
  ]
}
```

Run:
```bash
python -m app.main generate   --wireframe examples/wireframe.sample.json   --org-theme examples/org-theme.json   --output out/wireframe-ui   --app-name WireframeUI
```

---

## What you get

The generator writes:
- `out/<app>/ui-spec.json` (intermediate spec)
- `out/<app>/GENERATED_NOTES.md`
- a full React app (Vite + TS) with:
  - `src/styles/theme.css` (CSS variables from Org tokens)
  - `src/components/*` (atoms + layout + form/table renderers)
  - `src/api/*` (fetch client + operation wrappers)
  - `src/pages/*` (routes inferred from OpenAPI or wireframe)
  - `tests/*` (Playwright smoke tests)

---

## Customizing “Claude skills.md” behavior

Edit:
- `app/prompts/skills.md`
- `app/prompts/*.md`

These prompts guide the agent with a “skills.md” pattern:
- strict output formatting
- component conventions
- theme rules
- accessibility checklist
- test generation checklist

---

## Notes

- This project doesn’t require Streamlit/FastAPI; it’s a CLI generator.
- You can extend tools in `app/tools/` and add additional agent steps in `app/agents/orchestrator.py`.

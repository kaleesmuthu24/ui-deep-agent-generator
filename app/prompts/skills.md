# Claude-style skills.md (UI Generator)

## Skill: UI Spec Synthesizer
- Input: baseline ui-spec + OpenAPI/Figma payload + theme tokens
- Output: ONE JSON object `ui-spec` (no extra text)
- Rules:
  - Pages must have: name, route, sections[]
  - Sections must have: type (table|form|layout), title, source {kind, operationId? / nodeId?}
  - Prefer routes like `/accounts`, `/orders`, etc.
  - Group OpenAPI operations by tags or resource name.
  - Include at least one "Home" concept (even if not a page).

## Skill: Theme Application
- Use theme tokens to generate CSS variables and consistent component styling.
- No inline styles unless unavoidable. Prefer CSS classes (but keep it lightweight).

## Skill: React App Generator (Vite + TS)
- Output must compile with Vite + TypeScript.
- Use react-router-dom for routing.
- Provide shared components:
  - Nav, Card, FormSection, TableSection, EmptyState
- If OpenAPI operation IDs exist, generate stubs in `src/api/operations.ts`.
- Never delete build-critical files (package.json, vite config, tsconfig).

## Skill: Test Generator (Playwright)
- Write stable smoke tests:
  - no fragile CSS selectors
  - prefer getByRole(), getByText(), accessible names
- Tests should pass after `npm run dev`.

## Output Format
When asked to output JSON mapping file paths to content:
- Return a single JSON object: `{ "path": "content", ... }`
- No Markdown, no commentary.

You will be given:
- ui_spec JSON
- theme tokens
- constraints and an index of current files

Your task:
- Return a JSON object mapping file paths to full contents.
- Only include files that should be added or replaced.
- Improve: layout, copy, componentization, empty states, error handling.
- Keep the code buildable with Vite + React + TS and the existing template.

Hard rules:
- No markdown.
- No inline styles (prefer CSS classes); tiny inline style is allowed only if necessary.
- Do not remove files.

# Structured Outputs Add-on (Strict JSON) for User-Story + Task Generation

Use this add-on with your `skills_task_relevant.md` so GPT-5.2 produces **consistent, task-relevant** issue bundles.

## What this solves
- Stops the model from adding unrelated tasks (e.g., demographics for “recent transactions”)
- Forces a Domain/Intent “Gate” first
- Forces every AC, Dev task, and QA item to map to a requirement (R#) with a **Relevance** line

## Files
- `issue_bundle_schema.json` — the strict JSON schema to enforce output
- This add-on — how to use the schema and a recommended 2-pass flow

## Recommended Flow (2-pass)
### Pass A — Gate + Requirements + Feature Matrix
Generate:
- `gate`
- `requirements` (R1..Rn)
- `feature_matrix`

Then validate:
- `gate.excluded_topics` includes adjacent-but-not-asked topics
- each requirement has a clear relevance line

### Pass B — Story + Dev + QA + SM (from Pass A only)
Generate the full bundle.
Strictly:
- every AC must map to (R#)
- every dev task must map to (R#)
- QA scenarios/cases must map to (R#)

## OpenAI API usage pattern (Responses API)
Load the schema from `issue_bundle_schema.json` and send as Structured Outputs.

### Minimal Python example
```python
from openai import OpenAI
import json

client = OpenAI()

with open("issue_bundle_schema.json", "r", encoding="utf-8") as f:
    schema = json.load(f)

resp = client.responses.create(
    model="gpt-5.2",
    input=[
        {
            "role": "system",
            "content": "You are an issue creation agent. Follow the skill rules. Output MUST match the JSON schema."
        },
        {
            "role": "user",
            "content": "I want to see customer recent transactions."
        }
    ],
    # Structured Outputs (strict JSON schema)
    text={
        "format": {
            "type": "json_schema",
            "name": schema["name"],
            "strict": True,
            "schema": schema["schema"]
        }
    },
    reasoning={"effort": "high"},
)
print(resp.output_text)
```

## Tuning notes
- If prompts are short/ambiguous, use `reasoning.effort: "high"` to reduce hallucinated scope.
- Keep temperature low (0–0.3) if you’re seeing “creative drift”.

## Validation Rules (simple)
Fail the response if any of these are true:
1) Any `dev_tasks[].mapped_requirements` references an R# that doesn’t exist
2) Any `acceptance_criteria[].mapped_requirements` is empty
3) Any task has `relevance` that cannot be tied to the user prompt (your code can keyword-check)
4) `excluded_topics` is empty when the prompt is narrow (typical drift indicator)

If validation fails, re-prompt with:
“Fix ONLY the validation failures. Do not add new scope.”


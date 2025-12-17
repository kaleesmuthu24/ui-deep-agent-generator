from __future__ import annotations

import os
from typing import Optional

def get_llm() -> Optional[object]:
    provider = (os.getenv("LLM_PROVIDER") or "none").strip().lower()
    if provider in ("none", "", "off", "disabled"):
        return None

    # We intentionally keep this lightweight and tolerant to env differences.
    # If an import fails, we fall back to offline baseline mode.
    try:
        if provider == "openrouter":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENROUTER_API_KEY")
            model = os.getenv("OPENROUTER_MODEL", "anthropic/claude-3.5-sonnet")
            if not api_key:
                return None
            return ChatOpenAI(
                model=model,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
                temperature=0.2,
            )
        if provider == "openai":
            from langchain_openai import ChatOpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
            if not api_key:
                return None
            return ChatOpenAI(model=model, api_key=api_key, temperature=0.2)
        if provider == "anthropic":
            from langchain_anthropic import ChatAnthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
            if not api_key:
                return None
            return ChatAnthropic(model=model, api_key=api_key, temperature=0.2)
    except Exception:
        return None

    return None

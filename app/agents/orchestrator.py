from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.llm.provider import get_llm
from app.tools.openapi_loader import load_openapi
from app.tools.figma_loader import load_figma_minimal
from app.tools.wireframe_loader import load_wireframe
from app.tools.theme_loader import load_theme_tokens
from app.tools.project_writer import write_react_project

from app.agents.ui_spec_agent import build_ui_spec
from app.agents.react_codegen_agent import generate_react_app
from app.agents.tests_agent import generate_playwright_tests
from app.prompts.load_prompts import load_prompt_bundle

@dataclass
class Inputs:
    openapi: Optional[str]
    wireframe: Optional[str]
    figma_file_key: Optional[str]
    figma_token: Optional[str]
    org_theme_path: str
    output_dir: str
    app_name: str
    api_base_url: str
    with_tests: bool

def _read_input_payload(inp: Inputs) -> Dict[str, Any]:
    if inp.wireframe:
        return {"kind": "wireframe", "data": load_wireframe(inp.wireframe)}
    if inp.openapi:
        return {"kind": "openapi", "data": load_openapi(inp.openapi)}
    if inp.figma_file_key and inp.figma_token:
        return {"kind": "figma", "data": load_figma_minimal(inp.figma_file_key, inp.figma_token)}
    raise ValueError("Provide one of: --wireframe, --openapi, or --figma-file-key + --figma-token")

def generate_ui_project(
    openapi: Optional[str],
    wireframe: Optional[str],
    figma_file_key: Optional[str],
    figma_token: Optional[str],
    org_theme_path: str,
    output_dir: str,
    app_name: str,
    api_base_url: str,
    with_tests: bool = False,
) -> None:
    inp = Inputs(
        openapi=openapi,
        wireframe=wireframe,
        figma_file_key=figma_file_key,
        figma_token=figma_token,
        org_theme_path=org_theme_path,
        output_dir=output_dir,
        app_name=app_name,
        api_base_url=api_base_url,
        with_tests=with_tests,
    )

    prompts = load_prompt_bundle()
    llm = get_llm()

    source_payload = _read_input_payload(inp)
    theme = load_theme_tokens(inp.org_theme_path)
    ui_spec = build_ui_spec(llm=llm, prompts=prompts, source_payload=source_payload, theme=theme, app_name=app_name)

    # Generate the React project contents (file map)
    file_map = generate_react_app(
        llm=llm,
        prompts=prompts,
        ui_spec=ui_spec,
        theme=theme,
        app_name=app_name,
        api_base_url=api_base_url,
        with_tests=with_tests,
    )

    if with_tests:
        test_files = generate_playwright_tests(llm=llm, prompts=prompts, ui_spec=ui_spec, app_name=app_name)
        file_map.update(test_files)

    # Write output (React Vite template + generated files)
    write_react_project(output_dir=output_dir, app_name=app_name, file_map=file_map, ui_spec=ui_spec)

    print(f"✅ Generated React app at: {output_dir}")
    print(f"   Next: cd {output_dir} && npm install && npm run dev")

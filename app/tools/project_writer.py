from __future__ import annotations

import json
import os
import shutil
from typing import Dict, Any

from app.tools.react_templates import template_root_dir, copy_template_dir

def write_react_project(output_dir: str, app_name: str, file_map: Dict[str, str], ui_spec: Dict[str, Any]) -> None:
    # 1) Copy base Vite template
    tmpl = template_root_dir()
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    copy_template_dir(tmpl, output_dir, replacements={"__APP_NAME__": app_name})

    # 2) Write generated files
    for rel_path, content in file_map.items():
        out_path = os.path.join(output_dir, rel_path)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

    # 3) Store ui-spec.json
    with open(os.path.join(output_dir, "ui-spec.json"), "w", encoding="utf-8") as f:
        json.dump(ui_spec, f, indent=2)

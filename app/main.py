import argparse
import os
from dotenv import load_dotenv

from app.agents.orchestrator import generate_ui_project

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ui-deep-agent-generator")
    sub = p.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate a themed React app from OpenAPI/Figma/wireframe")
    g.add_argument("--openapi", help="Path/URL to OpenAPI spec (yaml/json)")
    g.add_argument("--wireframe", help="Path to wireframe.json (preferred for precision)")
    g.add_argument("--figma-file-key", help="Figma file key")
    g.add_argument("--figma-token", help="Figma personal access token (or use env Figma token)")
    g.add_argument("--org-theme", required=True, help="Path to org-theme.json (design tokens)")
    g.add_argument("--output", required=True, help="Output directory for generated React app")
    g.add_argument("--app-name", default="GeneratedUI", help="App name")
    g.add_argument("--base-url", default="http://localhost:8080", help="API base URL used by the generated UI")
    g.add_argument("--with-tests", action="store_true", help="Generate Playwright tests")
    return p

def main():
    load_dotenv()
    args = build_parser().parse_args()

    figma_token = args.figma_token or os.getenv("FIGMA_TOKEN")
    generate_ui_project(
        openapi=args.openapi,
        wireframe=args.wireframe,
        figma_file_key=args.figma_file_key,
        figma_token=figma_token,
        org_theme_path=args.org_theme,
        output_dir=args.output,
        app_name=args.app_name,
        api_base_url=args.base_url,
        with_tests=args.with_tests,
    )

if __name__ == "__main__":
    main()

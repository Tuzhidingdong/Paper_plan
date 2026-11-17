#!/usr/bin/env python3
"""Render a Markdown research plan to a checked PDF using installed Edge/Chrome."""
from __future__ import annotations

import argparse
import html
import os
import shutil
import subprocess
from pathlib import Path
from urllib.parse import quote


CSS = """
@page { size: A4; margin: 18mm 17mm 20mm; }
body { font-family: "Microsoft YaHei UI", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif;
       color: #202124; font-size: 10.5pt; line-height: 1.48; }
h1 { font-size: 21pt; margin: 0 0 16pt; page-break-after: avoid; }
h2 { font-size: 16pt; margin-top: 22pt; page-break-after: avoid; }
h3 { font-size: 12.5pt; margin-top: 16pt; page-break-after: avoid; }
p, li { orphans: 3; widows: 3; }
table { width: 100%; border-collapse: collapse; font-size: 9pt; margin: 10pt 0 14pt; }
th, td { border: 0.5pt solid #8b8b8b; padding: 5pt 6pt; vertical-align: top; }
thead { display: table-header-group; }
tr { page-break-inside: avoid; }
blockquote { margin: 8pt 0; padding: 4pt 10pt; border-left: 2pt solid #777; color: #444; }
code, pre { font-family: Consolas, monospace; font-size: 8.5pt; }
pre { white-space: pre-wrap; background: #f4f5f6; padding: 8pt; }
a { color: #174ea6; text-decoration: none; }
hr { border: none; border-top: 1px solid #aaa; margin: 14pt 0; }
"""


def find_browser() -> str | None:
    for command in ("msedge", "chrome", "chromium", "chromium-browser"):
        path = shutil.which(command)
        if path:
            return path
    roots = [
        os.environ.get("PROGRAMFILES", r"C:\Program Files"),
        os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"),
        os.environ.get("LOCALAPPDATA", ""),
    ]
    candidates = [
        Path(roots[0]) / "Microsoft/Edge/Application/msedge.exe",
        Path(roots[1]) / "Microsoft/Edge/Application/msedge.exe",
        Path(roots[0]) / "Google/Chrome/Application/chrome.exe",
        Path(roots[1]) / "Google/Chrome/Application/chrome.exe",
        Path(roots[2]) / "Microsoft/Edge/Application/msedge.exe",
    ]
    return next((str(item) for item in candidates if item.is_file()), None)


def build_html(markdown_text: str, title: str) -> str:
    try:
        import markdown
    except ImportError as exc:
        raise RuntimeError("Install the Markdown dependency with: python -m pip install -r requirements.txt") from exc
    body = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "toc", "sane_lists"],
        output_format="html5",
    )
    return (
        "<!doctype html><html lang='zh-CN'><head><meta charset='utf-8'>"
        f"<title>{html.escape(title)}</title><style>{CSS}</style></head><body>"
        f"{body}</body></html>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("markdown_file", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = args.markdown_file.expanduser().resolve()
    if not source.is_file():
        parser.error(f"Markdown file does not exist: {source}")
    output = args.output.expanduser().resolve() if args.output else source.with_suffix(".pdf")
    output.parent.mkdir(parents=True, exist_ok=True)
    html_path = output.with_suffix(".render.html")
    title = source.stem.replace("_", " ")
    html_path.write_text(build_html(source.read_text(encoding="utf-8"), title), encoding="utf-8")

    browser = find_browser()
    if not browser:
        print("No Edge/Chrome executable found. HTML was created at: " + str(html_path))
        print("Open the HTML in a browser and print to PDF; do not report a PDF as created.")
        return 2

    command = [
        browser, "--headless", "--disable-gpu", "--no-pdf-header-footer",
        f"--print-to-pdf={output}", Path(html_path).as_uri(),
    ]
    run = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if run.returncode != 0 or not output.is_file() or output.stat().st_size < 1000:
        print(run.stdout)
        print(run.stderr)
        print("PDF export failed; the intermediate HTML is retained at: " + str(html_path))
        return 2

    try:
        import fitz
        document = fitz.open(output)
        page_count = len(document)
        extracted = "\n".join(page.get_text("text") for page in document)
        document.close()
    except Exception as exc:
        print(f"PDF verification failed: {exc}")
        return 2
    if page_count < 1 or len(extracted.strip()) < 80:
        print("PDF was created but failed basic page/text verification.")
        return 2
    print(f"PDF: {output}")
    print(f"Pages: {page_count}")
    print(f"Extracted text characters: {len(extracted)}")
    print(f"Source Markdown SHA-256 is recorded by the caller; HTML: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

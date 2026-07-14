"""
generate_pdfs.py — Convert Markdown docs to PDF
Requires: pip install markdown weasyprint
Run: python generate_pdfs.py
"""

import os
import subprocess
import sys


def md_to_pdf_via_pandoc(md_path: str, pdf_path: str):
    """Uses pandoc if available (recommended)."""
    try:
        subprocess.run(
            ["pandoc", md_path, "-o", pdf_path,
             "--pdf-engine=wkhtmltopdf",
             "-V", "geometry:margin=2cm",
             "-V", "fontsize=11pt"],
            check=True
        )
        print(f"[OK] {os.path.basename(pdf_path)}")
    except FileNotFoundError:
        print("[SKIP] pandoc not found — install from https://pandoc.org/installing.html")
    except subprocess.CalledProcessError as e:
        print(f"[FAIL] {e}")


def md_to_pdf_via_weasyprint(md_path: str, pdf_path: str):
    """Uses Python weasyprint as fallback."""
    try:
        import markdown
        from weasyprint import HTML, CSS
        with open(md_path, "r", encoding="utf-8") as f:
            body = f.read()
        html_body = markdown.markdown(body, extensions=["tables", "fenced_code"])
        full_html = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<style>
  body {{ font-family: 'Calibri', Arial, sans-serif; font-size: 11pt;
          margin: 2cm; color: #1a1a2e; line-height: 1.6; }}
  h1 {{ color: #6366f1; border-bottom: 2px solid #6366f1; padding-bottom: 6px; }}
  h2 {{ color: #4f46e5; margin-top: 24px; }}
  h3 {{ color: #7c3aed; }}
  table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
  th {{ background: #6366f1; color: white; padding: 8px 12px; text-align: left; }}
  td {{ border: 1px solid #e2e8f0; padding: 6px 10px; }}
  tr:nth-child(even) {{ background: #f8fafc; }}
  code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px;
           font-family: monospace; font-size: 10pt; }}
  pre {{ background: #1e293b; color: #e2e8f0; padding: 16px;
          border-radius: 8px; overflow-x: auto; }}
  blockquote {{ border-left: 4px solid #6366f1; margin-left: 0;
                 padding-left: 16px; color: #64748b; }}
</style>
</head><body>{html_body}</body></html>"""
        HTML(string=full_html).write_pdf(pdf_path)
        print(f"[OK] {os.path.basename(pdf_path)}")
    except ImportError:
        print("[SKIP] weasyprint/markdown not installed. Run: pip install weasyprint markdown")
    except Exception as e:
        print(f"[FAIL] {e}")


if __name__ == "__main__":
    base = os.path.dirname(os.path.abspath(__file__))

    conversions = [
        (
            os.path.join(base, "Task1", "Task1_LinkedIn_Content.md"),
            os.path.join(base, "Task1", "Task1_LinkedIn_Content.pdf"),
        ),
        (
            os.path.join(base, "docs", "Approach_Document.md"),
            os.path.join(base, "docs", "Approach_Document.pdf"),
        ),
    ]

    print("Generating PDFs...")
    for md_path, pdf_path in conversions:
        if not os.path.exists(md_path):
            print(f"[SKIP] Source not found: {md_path}")
            continue
        # Try weasyprint first (pure Python), then pandoc
        md_to_pdf_via_weasyprint(md_path, pdf_path)

    print("\nDone. Check Task1/ and docs/ folders for PDF files.")

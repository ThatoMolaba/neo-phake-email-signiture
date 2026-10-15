#!/usr/bin/env python3
"""Fill signature.template.html with values from config.json.

Outputs:
  signature.html          production signature (absolute HTTPS image URL)
  preview/signature.html  same, but pointing at the local assets/ folder for offline preview
"""
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOKEN = re.compile(r"\{\{([A-Z_0-9]+)\}\}")

# URL values are inserted verbatim; everything else is HTML-escaped.
RAW_KEYS = {"ASSET_BASE", "WEBSITE_URL"}


def render(template: str, values: dict) -> str:
    # Drop the template's instruction comment from the production output.
    template = re.sub(r"\A<!--.*?-->\s*", "", template, flags=re.S)
    missing = sorted({m for m in TOKEN.findall(template) if m not in values})
    if missing:
        sys.exit(f"config.json is missing: {', '.join(missing)}")

    def sub(m):
        key = m.group(1)
        val = str(values[key])
        return html.escape(val, quote=True) if key not in RAW_KEYS else val

    return TOKEN.sub(sub, template)


def validate(values: dict) -> None:
    wa = values["WHATSAPP_NUMBER"]
    if not re.fullmatch(r"27[1-9]\d{8}", wa):
        print(f"warning: WHATSAPP_NUMBER '{wa}' should look like 27XXXXXXXXX "
              "(country code, no '+', spaces or leading 0)", file=sys.stderr)
    if not re.fullmatch(r"\+27[1-9]\d{8}", values["PHONE_E164"]):
        print("warning: PHONE_E164 should look like +27XXXXXXXXX", file=sys.stderr)
    for k in ("ASSET_BASE", "WEBSITE_URL"):
        if not values[k].startswith("https://"):
            print(f"warning: {k} should be an absolute https:// URL", file=sys.stderr)


def main() -> None:
    values = json.loads((ROOT / "config.json").read_text())
    validate(values)
    template = (ROOT / "signature.template.html").read_text()

    (ROOT / "signature.html").write_text(render(template, values))

    local = dict(values, ASSET_BASE="../assets")
    (ROOT / "preview").mkdir(exist_ok=True)
    (ROOT / "preview" / "signature.html").write_text(render(template, local))
    print("built signature.html and preview/signature.html")


if __name__ == "__main__":
    main()

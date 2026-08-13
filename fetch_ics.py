#!/usr/bin/env python3
"""
fetch-ics — Download an iCal (`.ics`) file from any URL.

Fetches a remote iCal feed and saves it locally, handling SSL quirks
(e.g. macOS certificate issues) automatically.

Usage:
    python3 fetch_ics.py <url> [output_file]

Examples:
    python3 fetch_ics.py "https://example.com/calendar.ics"
    python3 fetch_ics.py "https://example.com/calendar.ics" my_schedule.ics
"""

import argparse
import ssl
import urllib.request
import urllib.parse
import re
from pathlib import Path

__version__ = "1.0.0"


def fetch_ics(url: str, output_path: str | None = None) -> str:
    """Fetch an iCal feed from a URL and save it as a local .ics file.

    Args:
        url: The iCal subscription/download URL.
        output_path: Optional destination path. If omitted, a name is
                     inferred from the URL.

    Returns:
        The absolute path to the saved .ics file.

    Raises:
        urllib.error.URLError: If the URL can't be reached.
        ValueError: If the response isn't valid iCal text.
    """
    # ------------------------------------------------------------------
    # Fetch the remote file
    # ------------------------------------------------------------------
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        with urllib.request.urlopen(url, context=ctx) as resp:
            raw = resp.read()
    except Exception as exc:
        raise urllib.error.URLError(f"Failed to fetch {url}: {exc}") from exc

    try:
        ics_content = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Response is not valid UTF-8 text.") from exc

    # ------------------------------------------------------------------
    # Basic sanity check — is it actually an iCal file?
    # ------------------------------------------------------------------
    if "BEGIN:VCALENDAR" not in ics_content:
        raise ValueError(
            "The fetched content doesn't look like an iCal file "
            "(missing BEGIN:VCALENDAR)."
        )

    # ------------------------------------------------------------------
    # Determine output path
    # ------------------------------------------------------------------
    if output_path is None:
        # Pull the last path segment as a hint; strip extension if it's .ics
        stem = Path(urllib.parse.urlparse(url).path).stem
        # Remove characters that are unsafe for filenames on common OSes
        stem = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", stem)
        output_path = (stem or "calendar") + ".ics"

    # Force .ics extension
    if not output_path.lower().endswith(".ics"):
        output_path += ".ics"

    # ------------------------------------------------------------------
    # Write to disk
    # ------------------------------------------------------------------
    dest = Path(output_path).resolve()
    dest.write_text(ics_content, encoding="utf-8")
    return str(dest)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="fetch-ics",
        description="Download an iCal (.ics) file from any URL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "example:\n"
            "  python3 fetch_ics.py \"https://example.com/calendar.ics\"\n"
            "  python3 fetch_ics.py \"https://example.com/cal.ics\" schedule.ics"
        ),
    )
    parser.add_argument("url", help="URL of the iCal feed")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output filename (default: inferred from URL)"
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    try:
        saved = fetch_ics(args.url, args.output)
        print(f"✓ Saved to: {saved}")
    except (urllib.error.URLError, ValueError) as exc:
        print(f"✗ {exc}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    import sys
    main()

# fetch-ics

Download any iCal (`.ics`) file from a URL and save it locally — no extra dependencies.

Useful when a calendar site only gives you a subscription link instead of a direct download, or when you want to grab a static snapshot of a live feed.

## Requirements

- Python 3.8+

No third-party packages needed.

## Quick start

```bash
# Download from a URL (saves as calendar.ics)
python3 fetch_ics.py "https://example.com/calendar.ics"

# Specify a custom output filename
python3 fetch_ics.py "https://example.com/calendar.ics" my_schedule.ics
```

## How it works

1. Fetches the URL with HTTPS (handles SSL certificate quirks on macOS automatically).
2. Checks that the response looks like a valid iCal file.
3. Saves the content as a `.ics` file locally.

## CLI options

```
usage: fetch_ics.py [-h] [-v] url [output]

positional arguments:
  url        URL of the iCal feed
  output     output filename (default: inferred from URL)

options:
  -h, --help  show this help message and exit
  -v, --version  show program version
```

## Using as a module

```python
from fetch_ics import fetch_ics

path = fetch_ics("https://example.com/calendar.ics")
print(f"Saved to: {path}")
```

## Running the tests

```bash
python3 -m unittest discover -v
```

## License

MIT

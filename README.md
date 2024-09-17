# paraminer - Web Archive URL Fetcher

## Description

paraminer is a Python script that extracts and cleans URLs from the Wayback Machine (web.archive.org). The script supports fetching URLs for a single domain or a list of domains, cleaning those URLs by removing unnecessary parameters, and saving the results to files.

## Features

- Fetch URLs from the Wayback Machine for specified domains.
- Clean URLs by removing file extensions and query parameters.
- Output results to a global file or separate files for each domain.
- Support for proxy configuration.
- Optional suppression of terminal output.

## Requirements

- Python 3.x
- `colorama`
- `requests` (or a custom client module if provided)

You can install the required packages using `pip`:

```bash
pip install colorama requests
```

## Usage
Command-Line Arguments

`-d, --domain: Domain name to fetch related URLs for.`

`-l, --list: File containing a list of domain names (one per line).`

`-s, --silent: Suppress terminal output and banner.`
`--proxy: Set the proxy address for web requests.`

`-p, --placeholder: Placeholder for parameter values (default: "FUZZ").`

`-g, --global-file: Path to a global file where URLs are appended.`

## Examples
Fetch URLs for a single domain and save to a file:
```bash
python3 main.py -d example.com
```
Fetch URLs for a list of domains and append to a global file:
```bash
python3 main.py -l domains.txt -g global_urls.txt
```
Fetch URLs with a proxy and use a different placeholder:
```bash
python3 main.py -d example.com --proxy http://proxy.example.com -p PLACEHOLDER
```
Suppress terminal output and banner:
```bash
python3 main.py -d example.com -s
```

### Inspired by

[ParamSpider](https://github.com/devanshbatham/ParamSpider)


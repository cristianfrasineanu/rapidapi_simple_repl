## RapidAPI Instagram REPL

Interactive CLI to explore and call your subscribed RapidAPI Instagram endpoints, then export results to JSON or CSV.

### Setup
- Create and activate a virtual env (macOS/Linux):
  - `python3 -m venv .venv && source .venv/bin/activate`
- Install deps:
  - `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and set `RAPIDAPI_KEY`.

### Configure endpoints
- Edit `rapidapi_config.json` and set:
  - `host`: your API host from RapidAPI (e.g., `instagram-scraper-api-host.p.rapidapi.com`).
  - `url`: full URL using that host.
  - `params`: define `path`/`query`/`body` parameters with prompts and defaults.

Example entry:
```json
{
  "name": "Get comments by media URL",
  "method": "GET",
  "host": "instagram-scraper-api-host.p.rapidapi.com",
  "url": "https://instagram-scraper-api-host.p.rapidapi.com/comments",
  "params": [
    {"name": "url", "in": "query", "prompt": "Instagram post URL"},
    {"name": "limit", "in": "query", "prompt": "Max comments", "default": 100}
  ]
}
```

### Run
```bash
python rapidapi_repl.py
```
Follow the menu to:
- Choose an endpoint
- Enter parameters
- Choose output (pretty JSON, save JSON, extract list to CSV)

### Notes
- Set `RAPIDAPI_CONFIG` to point to another config file if needed.
- CSV extraction asks for a dotted JSON path to a list (e.g., `data.comments`).



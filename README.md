## RapidAPI Instagram REPL

Interactive CLI to explore and call your subscribed RapidAPI Instagram endpoints, then export results to JSON or CSV with automatic pagination support.

## Features

- **Multiple output formats**: Pretty JSON, raw JSON files, or structured CSV extraction
- **Automatic pagination**: Fetch all pages automatically and append to a single CSV
- **Rate limiting**: Configurable per-endpoint to respect API quotas
- **Flexible CSV extraction**: Use dotted paths with array notation (e.g., `comments[].text`)
- **Smart pagination detection**: Automatically finds cursor tokens in API responses

### Setup
- Create and activate a virtual env (macOS/Linux):
  - `python3 -m venv .venv && source .venv/bin/activate`
- Install deps:
  - `pip install -r requirements.txt`
- Copy `.env.example` to `.env` and set `RAPIDAPI_KEY`.

### Configure endpoints
Edit `rapidapi_config.json` to define your API endpoints:

```json
{
  "apis": [
    {
      "name": "Instagram Comments API",
      "method": "GET",
      "host": "instagram-scraper-api.p.rapidapi.com",
      "url": "https://instagram-scraper-api.p.rapidapi.com/get_post_comments.php",
      "params": [
        {"name": "media_code", "in": "query", "prompt": "Instagram post code", "default": "DL2G5oIIWya"},
        {"name": "sort_order", "in": "query", "prompt": "Sort order (popular/recent)", "default": "recent"},
        {"name": "pagination_token", "in": "query", "prompt": "Pagination token (leave empty for first page)", "default": ""}
      ],
      "pagination": {
        "cursor_field": "cached_comments_cursor",
        "query_param": "pagination_token"
      },
      "rate_limit": 30
    }
  ]
}
```

#### Configuration Options

**Required fields:**
- `name`: Display name for the endpoint
- `method`: HTTP method (GET, POST, etc.)
- `host`: RapidAPI host header
- `url`: Full endpoint URL
- `params`: Array of parameter definitions

**Parameter definitions:**
- `name`: Parameter name
- `in`: Location - "query", "path", or "body"
- `prompt`: User-friendly prompt text
- `default`: Optional default value

**Optional fields:**
- `pagination`: Pagination configuration
  - `cursor_field`: JSON field containing the next page cursor
  - `query_param`: Parameter name to send cursor in next request
- `rate_limit`: Maximum requests per minute (default: 60)

### Usage

```bash
chmod a+x rapidapi_repl.py && ./rapidapi_repl.py
```

#### Output Options

1. **Pretty JSON**: Formatted display in terminal
2. **Save raw JSON**: Export to `.json` file
3. **Extract to CSV**: Single page with custom field selection
4. **Extract ALL pages to CSV (auto-paginate)**: 🆕 Automatically fetch all pages

#### CSV Extraction

Use dotted paths with array notation to extract nested data:

**Examples:**
- `comments[]`: Extract all comment objects as separate rows
- `comments[].text,comments[].user.username`: Extract specific fields
- `data.posts[].caption,data.posts[].likes_count`: Navigate nested structures

**Pagination workflow:**
1. Choose "Extract ALL pages to CSV (auto-paginate)"
2. Enter dotted paths once (e.g., `comments[].text,comments[].user.username`)
3. Enter CSV filename
4. System automatically fetches all pages and appends to the same file

### Notes
- Set `RAPIDAPI_CONFIG` environment variable to use a different config file
- Rate limiting is especially important during pagination to avoid quota exhaustion
- Large datasets can be extracted efficiently with automatic pagination



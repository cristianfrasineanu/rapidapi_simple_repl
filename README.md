## RapidAPI REPL

Interactive CLI to explore and call your subscribed RapidAPI endpoints, then export results to JSON or CSV with automatic pagination support.

## Features

- **Multiple output formats**: Pretty JSON, raw JSON files, or structured CSV extraction
- **Automatic pagination**: Fetch all pages automatically and append to a single CSV
- **Rate limiting**: Configurable per-endpoint to respect API quotas
- **Flexible CSV extraction**: Use dotted paths with array notation (e.g., `items[].name`)
- **Smart pagination detection**: Automatically finds cursor tokens in API responses
- **Platform agnostic**: Works with any RapidAPI endpoint (social media, e-commerce, data APIs, etc.)

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
      "name": "E-commerce Products API",
      "method": "GET",
      "host": "ecommerce-api.p.rapidapi.com",
      "url": "https://ecommerce-api.p.rapidapi.com/products",
      "params": [
        {"name": "category", "in": "query", "prompt": "Product category", "default": "electronics"},
        {"name": "sort", "in": "query", "prompt": "Sort order (price/rating/date)", "default": "price"},
        {"name": "page_token", "in": "query", "prompt": "Page token (leave empty for first page)", "default": ""}
      ],
      "pagination": {
        "cursor_field": "next_page_token",
        "query_param": "page_token"
      },
      "rate_limit": 30
    },
    {
      "name": "Social Media Posts API",
      "method": "GET", 
      "host": "social-api.p.rapidapi.com",
      "url": "https://social-api.p.rapidapi.com/posts",
      "params": [
        {"name": "user_id", "in": "query", "prompt": "User ID"},
        {"name": "limit", "in": "query", "prompt": "Posts per page", "default": "20"}
      ],
      "rate_limit": 60
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
- `products[]`: Extract all product objects as separate rows  
- `products[].name,products[].price`: Extract specific fields
- `data.items[].title,data.items[].category`: Navigate nested structures
- `results[].user.name,results[].content`: Extract from social media posts

**Pagination workflow:**
1. Choose "Extract ALL pages to CSV (auto-paginate)"
2. Enter dotted paths once (e.g., `products[].name,products[].price`)
3. Enter CSV filename
4. System automatically fetches all pages and appends to the same file

### Notes
- Set `RAPIDAPI_CONFIG` environment variable to use a different config file
- Rate limiting is especially important during pagination to avoid quota exhaustion
- Large datasets can be extracted efficiently with automatic pagination



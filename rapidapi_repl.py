#! /usr/bin/env python3

import json
import os
import sys
from typing import Any, Dict, List, Tuple, Optional

import requests
from dotenv import load_dotenv


def load_config(config_path: str) -> Dict[str, Any]:
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def prompt_choice(prompt: str, choices: List[str]) -> int:
    for idx, label in enumerate(choices, start=1):
        print(f"{idx}. {label}")
    while True:
        raw = input(f"{prompt} [1-{len(choices)}]: ").strip()
        if raw.isdigit():
            val = int(raw)
            if 1 <= val <= len(choices):
                return val - 1
        print("Invalid selection. Try again.")


def resolve_url(template: str, path_params: Dict[str, str]) -> str:
    url = template
    for key, value in path_params.items():
        url = url.replace("{" + key + "}", value)
    return url


def collect_params(
    param_defs: List[Dict[str, Any]],
) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, Any]]:
    path_params: Dict[str, str] = {}
    query_params: Dict[str, str] = {}
    body_json: Dict[str, Any] = {}
    for p in param_defs:
        name = p.get("name")
        location = p.get("in", "query")
        default = p.get("default")
        prompt_label = p.get("prompt") or name
        val = input(
            f"Enter {prompt_label}{' [' + str(default) + ']' if default is not None else ''}: "
        ).strip()
        if not val and default is not None:
            val = str(default)
        if location == "path":
            path_params[name] = val
        elif location == "query":
            query_params[name] = val
        elif location == "body":
            body_json[name] = val
        else:
            query_params[name] = val
    return path_params, query_params, body_json


def pretty_print_json(data: Any) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))


def extract_by_path(data: Any, path: str) -> Any:
    node = data
    for part in [p for p in path.split(".") if p]:
        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None
    return node


def tokenize_path(path: str) -> List[str]:
    return [p.strip() for p in path.split(".") if p.strip()]


def extract_path_values(node: Any, tokens: List[str]) -> List[Any]:
    if not tokens:
        return [node]
    token = tokens[0]
    is_array = token.endswith("[]")
    key = token[:-2] if is_array else token

    current = node
    if key:
        if isinstance(current, dict):
            current = current.get(key, None)
        else:
            current = None

    next_nodes: List[Any]
    if is_array:
        if isinstance(current, list):
            next_nodes = current
        elif current is None:
            next_nodes = []
        else:
            next_nodes = [current]
    else:
        next_nodes = [current]

    results: List[Any] = []
    for n in next_nodes:
        results.extend(extract_path_values(n, tokens[1:]))
    return results


def split_first_array(path: str) -> Tuple[List[str], List[str]]:
    tokens = tokenize_path(path)
    for i, t in enumerate(tokens):
        if t.endswith("[]"):
            return tokens[: i + 1], tokens[i + 1 :]
    return [], tokens


def save_list_as_csv(
    rows: List[Dict[str, Any]], out_path: str, fieldnames: Optional[List[str]] = None
) -> None:
    if not rows:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("")
        return

    if fieldnames is None:
        fieldnames = []
        seen = set()
        for r in rows:
            for k in r.keys():
                if k not in seen:
                    seen.add(k)
                    fieldnames.append(k)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(",".join(fieldnames) + "\n")
        for r in rows:
            values = []
            for k in fieldnames:
                v = r.get(k, "")
                if v is None:
                    v = ""
                text = str(v).replace("\r", " ").replace("\n", " ").replace("\t", " ")
                text = text.replace('"', '""')
                if "," in text or '"' in text or "\n" in text:
                    text = f'"{text}"'
                values.append(text)
            f.write(",".join(values) + "\n")


def interactive_extract_to_csv(data: Any) -> None:
    paths_in = input(
        "Enter one or more dotted paths (comma-separated). Use [] to map arrays, e.g., comments[].text, comments[].user.username: "
    ).strip()
    path_list = [p.strip() for p in paths_in.split(",") if p.strip()]

    try:
        if len(path_list) >= 1 and any("[]" in p for p in path_list):
            base_prefix: List[str] = []
            remainders: List[List[str]] = []
            for p in path_list:
                prefix, rem = split_first_array(p)
                if not prefix:
                    raise ValueError(
                        "Each path must include an array expression '[]', e.g., comments[].text"
                    )
                if not base_prefix:
                    base_prefix = prefix
                elif base_prefix != prefix:
                    raise ValueError(
                        "All paths must share the same array prefix before and including '[]'"
                    )
                remainders.append(rem)

            items = extract_path_values(data, base_prefix)
            rows: List[Dict[str, Any]] = []
            for item in items:
                row: Dict[str, Any] = {}
                for path_str, rem_tokens in zip(path_list, remainders):
                    vals = extract_path_values(item, rem_tokens)
                    if len(vals) == 0:
                        value: Any = ""
                    elif len(vals) == 1:
                        value = vals[0]
                    else:
                        value = " | ".join(
                            [
                                json.dumps(v, ensure_ascii=False)
                                if isinstance(v, (dict, list))
                                else str(v)
                                for v in vals
                            ]
                        )
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    row[path_str] = value
                rows.append(row)
            out = input("CSV output path (e.g., comments.csv): ").strip() or "comments.csv"
            save_list_as_csv(rows, out, fieldnames=path_list)
            print(f"Saved CSV to {out}")
        else:
            if not path_list:
                print("No path provided.")
                return
            path = path_list[0]
            node = extract_by_path(data, path)
            if not isinstance(node, list):
                print("Path did not resolve to a list. Include [] for arrays or point to a list.")
                return
            rows: List[Dict[str, Any]] = []
            for item in node:
                if isinstance(item, dict):
                    rows.append(item)
                else:
                    rows.append({"value": item})
            out = input("CSV output path (e.g., comments.csv): ").strip() or "comments.csv"
            save_list_as_csv(rows, out)
            print(f"Saved CSV to {out}")
    except ValueError as ve:
        print(str(ve))


def build_headers(rapidapi_key: str, host: Optional[str]) -> Dict[str, str]:
    headers = {"X-RapidAPI-Key": rapidapi_key}
    if host:
        headers["X-RapidAPI-Host"] = host
    return headers


def perform_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    query_params: Dict[str, str],
    body_json: Dict[str, Any],
):
    if method == "GET":
        return requests.get(url, headers=headers, params=query_params, timeout=60)
    if method == "POST":
        return requests.post(url, headers=headers, params=query_params, json=body_json, timeout=60)
    return requests.request(
        method, url, headers=headers, params=query_params, json=body_json, timeout=60
    )


def parse_response(resp) -> Any:
    ctype = resp.headers.get("Content-Type", "")
    try:
        return resp.json() if "json" in ctype or resp.text.startswith("{") else {"raw": resp.text}
    except Exception:
        return {"raw": resp.text}


def build_endpoint_labels(apis: List[Dict[str, Any]]) -> List[str]:
    return [f"{api.get('name')} ({api.get('method', 'GET')} {api.get('url')})" for api in apis]


def handle_output_selection(data: Any) -> Optional[str]:
    out_mode = prompt_choice(
        "Choose output",
        [
            "Pretty JSON",
            "Save raw JSON to file",
            "Extract to CSV (by dotted path(s))",
            "Back to endpoints",
            "Exit",
        ],
    )
    if out_mode == 0:
        pretty_print_json(data)
        return None
    if out_mode == 1:
        out = input("Path to save JSON (e.g., output.json): ").strip() or "output.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Saved to {out}")
        return None
    if out_mode == 2:
        interactive_extract_to_csv(data)
        return None
    if out_mode == 3:
        return "back"

    return "exit"


def run_repl(apis: List[Dict[str, Any]], rapidapi_key: str) -> None:
    while True:
        labels = build_endpoint_labels(apis)
        idx = prompt_choice("Select an endpoint", labels)
        sel = apis[idx]

        method = sel.get("method", "GET").upper()
        url_template = sel.get("url")
        host = sel.get("host")
        param_defs = sel.get("params", [])

        path_params, query_params, body_json = collect_params(param_defs)
        url = resolve_url(url_template, path_params)
        headers = build_headers(rapidapi_key, host)

        try:
            resp = perform_request(method, url, headers, query_params, body_json)
        except Exception as e:
            print(f"Request failed: {e}")
            continue

        print(f"HTTP {resp.status_code}")
        data = parse_response(resp)
        action = handle_output_selection(data)
        if action == "back":
            continue
        if action == "exit":
            break


def main() -> None:
    load_dotenv()
    rapidapi_key = os.getenv("RAPIDAPI_KEY", "").strip()
    if not rapidapi_key:
        print("RAPIDAPI_KEY is not set. Create a .env with RAPIDAPI_KEY=<your key>.")
        sys.exit(1)

    config_path = os.getenv("RAPIDAPI_CONFIG", "rapidapi_config.json")
    try:
        config = load_config(config_path)
    except Exception as e:
        print(f"Failed to load {config_path}: {e}")
        sys.exit(1)

    apis = config.get("apis", [])
    if not apis:
        print("No endpoints defined in rapidapi_config.json → 'apis' is empty.")
        sys.exit(1)

    run_repl(apis, rapidapi_key)


if __name__ == "__main__":
    main()

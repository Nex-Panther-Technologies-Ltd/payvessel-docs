#!/usr/bin/env python3
"""Ensure Try it Header section: api-key, api-secret, Content-Type (POST JSON only).

These are OpenAPI header parameters for the playground — not duplicated in MDX.
Narrative auth: API Basics → Authentication.
"""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

OPENAPI = Path(__file__).resolve().parents[1] / "api-reference" / "openapi.json"
AUTH_NAMES = {"api-key", "api-secret", "Content-Type"}
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
SKIP_PATH_PREFIXES = ("/plants",)

API_KEY = {
    "name": "api-key",
    "in": "header",
    "description": "Your Payvessel public API key",
    "required": True,
    "schema": {"type": "string"},
}
API_SECRET = {
    "name": "api-secret",
    "in": "header",
    "description": "Your Payvessel secret",
    "required": True,
    "schema": {"type": "string"},
}
CONTENT_TYPE = {
    "name": "Content-Type",
    "in": "header",
    "description": "Request content type",
    "required": True,
    "schema": {"type": "string", "enum": ["application/json"]},
    "example": "application/json",
}


def has_json_body(op: dict) -> bool:
    body = op.get("requestBody") or {}
    return "application/json" in (body.get("content") or {})


def auth_headers(*, with_content_type: bool) -> list:
    headers = [deepcopy(API_KEY), deepcopy(API_SECRET)]
    if with_content_type:
        headers.append(deepcopy(CONTENT_TYPE))
    return headers


def main() -> None:
    spec = json.loads(OPENAPI.read_text())
    updated = 0
    for path, path_item in spec.get("paths", {}).items():
        if path.startswith(SKIP_PATH_PREFIXES):
            continue
        for method, op in path_item.items():
            if method not in HTTP_METHODS or not isinstance(op, dict):
                continue
            existing = [
                p
                for p in op.get("parameters", [])
                if not (
                    isinstance(p, dict)
                    and p.get("in") == "header"
                    and p.get("name") in AUTH_NAMES
                )
            ]
            op["parameters"] = auth_headers(with_content_type=has_json_body(op)) + existing
            op.pop("security", None)
            updated += 1

    spec["components"].pop("securitySchemes", None)
    if "securitySchemes" in spec["components"].get("schemas", {}):
        del spec["components"]["schemas"]["securitySchemes"]
    spec["security"] = [{}]

    OPENAPI.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"Playground Header fields on {updated} operations")


if __name__ == "__main__":
    main()

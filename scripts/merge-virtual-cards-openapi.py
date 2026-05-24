#!/usr/bin/env python3
"""Insert Virtual Cards paths and schemas into api-reference/openapi.json."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPENAPI_PATH = ROOT / "api-reference" / "openapi.json"
PATCH_PATH = ROOT / "api-reference" / "virtual-cards-openapi-patch.json"

def main() -> None:
    patch = json.loads(PATCH_PATH.read_text())
    spec = json.loads(OPENAPI_PATH.read_text())

    for path, methods in patch["paths"].items():
        if path in spec["paths"]:
            print(f"skip existing path {path}")
            continue
        spec["paths"][path] = methods

    schemas = spec.setdefault("components", {}).setdefault("schemas", {})
    for name, schema in patch["schemas"].items():
        schemas.setdefault(name, schema)

    OPENAPI_PATH.write_text(json.dumps(spec, indent=2) + "\n")
    print(f"Merged {len(patch['paths'])} paths into {OPENAPI_PATH}")


if __name__ == "__main__":
    main()

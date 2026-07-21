#!/usr/bin/env python3
"""Add Virtual Accounts-style descriptions and error responses to Issuing paths."""

import json
from copy import deepcopy
from pathlib import Path

OPENAPI = Path(__file__).resolve().parents[1] / "api-reference" / "openapi.json"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
LIST_CARDS_RESPONSE = json.loads(
    (FIXTURES / "list_virtual_cards_response.json").read_text()
)

ERROR_RESPONSES = {
    "401": {
        "description": "Unauthorized request",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"},
                "examples": {
                    "unauthorized": {
                        "summary": "Invalid credentials",
                        "value": {
                            "error": 401,
                            "message": "Unauthorized. Please check your API key.",
                        },
                    }
                },
            }
        },
    },
    "403": {
        "description": "Forbidden request",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            }
        },
    },
    "404": {
        "description": "Resource not found",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            }
        },
    },
    "500": {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "schema": {"$ref": "#/components/schemas/Error"}
            }
        },
    },
}

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


def auth_headers(*, with_body: bool = False) -> list:
    headers = [deepcopy(API_KEY), deepcopy(API_SECRET)]
    if with_body:
        headers.append(deepcopy(CONTENT_TYPE))
    return headers


def enrich_operation(op: dict, *, with_body: bool = False) -> None:
    op.pop("security", None)
    existing = [
        p
        for p in op.get("parameters", [])
        if not (isinstance(p, dict) and p.get("in") == "header" and p.get("name") in {"api-key", "api-secret", "Content-Type"})
    ]
    op["parameters"] = auth_headers(with_body=with_body) + existing
    for code, resp in ERROR_RESPONSES.items():
        if code not in op.get("responses", {}):
            op.setdefault("responses", {})[code] = resp


def main() -> None:
    spec = json.loads(OPENAPI.read_text())
    paths = spec["paths"]
    schemas = spec["components"]["schemas"]

    # --- Schemas (field explanations in Try it) ---
    schemas["CreateCustomerVirtualCardRequest"] = {
        "type": "object",
        "required": ["brand", "currency"],
        "properties": {
            "first_name": {"type": "string", "description": "Customer first name"},
            "last_name": {"type": "string", "description": "Customer last name"},
            "email": {"type": "string", "format": "email", "description": "Email address"},
            "phone": {"type": "string", "description": "Nigerian phone number"},
            "bvn": {"type": "string", "description": "11-digit Bank Verification Number"},
            "nin": {"type": "string", "description": "11-digit National Identification Number"},
            "dob": {"type": "string", "format": "date", "description": "Date of birth (YYYY-MM-DD)"},
            "image": {"type": "string", "description": "Base64-encoded identity document image"},
            "state": {"type": "string", "description": "State of residence"},
            "lga": {"type": "string", "description": "Local government area"},
            "street": {"type": "string", "description": "Street address"},
            "postal_code": {"type": "string", "description": "Postal code"},
            "brand": {
                "type": "string",
                "enum": ["VISA", "MASTERCARD"],
                "description": "Card network",
            },
            "currency": {
                "type": "string",
                "enum": ["USD"],
                "description": "Must be USD for customer cards",
            },
            "prefund_amount": {
                "type": "string",
                "description": "Optional initial card balance in USD (minimum 1.00 when provided)",
                "example": "10.00",
            },
            "card_name": {
                "type": "string",
                "description": "Optional label on card (max 255 characters)",
            },
        },
    }

    schemas["IssuedCard"] = {
        "type": "object",
        "properties": {
            "id": {"type": "string", "format": "uuid", "description": "PayVessel card ID"},
            "business_id": {"type": "string", "format": "uuid", "description": "Owning business"},
            "kind": {"type": "string", "description": "customer card"},
            "customer_id": {"type": "string", "format": "uuid", "description": "Linked customer ID"},
            "customer_name": {"type": "string", "description": "Customer display name"},
            "card_name": {"type": "string", "description": "Name on card"},
            "masked_pan": {
                "type": "string",
                "description": "Masked PAN (empty while PENDING)",
            },
            "status": {
                "type": "string",
                "enum": ["PENDING", "ACTIVE", "FROZEN", "TERMINATED", "FAILED"],
                "description": "Card lifecycle status",
            },
            "currency": {"type": "string", "description": "USD"},
            "brand": {"type": "string", "description": "VISA or MASTERCARD"},
            "balance": {"type": "string", "description": "Issuer-synced balance in USD"},
            "expiry": {"type": "string", "description": "Card expiry (MM/YY)"},
            "card_number": {
                "type": "string",
                "description": "Full PAN (GET card only, when ACTIVE/FROZEN)",
            },
            "cvv": {
                "type": "string",
                "description": "CVV (GET card only, when ACTIVE/FROZEN)",
            },
            "created_datetime": {"type": "string", "format": "date-time"},
            "updated_datetime": {"type": "string", "format": "date-time"},
        },
    }

    schemas["VirtualCardAmountRequest"] = {
        "type": "object",
        "required": ["amount"],
        "properties": {
            "amount": {
                "type": "string",
                "description": "USD amount (e.g. 25.00). Withdraw minimum 3.00",
                "example": "25.00",
            }
        },
    }

    schemas["VirtualCardFeeQuoteRequest"] = {
        "type": "object",
        "required": ["fee_type"],
        "properties": {
            "fee_type": {
                "type": "string",
                "enum": [
                    "issuance",
                    "funding",
                    "withdrawal",
                    "spend",
                    "maintenance",
                    "cross_border",
                    "chargeback",
                    "decline",
                ],
                "description": "Fee type to calculate",
            },
            "amount_usd": {
                "type": "string",
                "description": "Principal USD amount (required for funding, cross_border)",
            },
        },
    }

    card_id_param = {
        "name": "card_id",
        "in": "path",
        "description": "PayVessel card ID",
        "required": True,
        "schema": {"type": "string", "format": "uuid"},
    }

    # list GET
    list_op = paths["/pms/api/external/request/virtual-cards/"]["get"]
    list_op["parameters"] = auth_headers() + [
        {
            "name": "status",
            "in": "query",
            "required": False,
            "description": "Filter: PENDING, ACTIVE, FROZEN, TERMINATED, FAILED",
            "schema": {
                "type": "string",
                "enum": ["PENDING", "ACTIVE", "FROZEN", "TERMINATED", "FAILED"],
            },
        },
    ]
    list_op.pop("security", None)
    list_op["responses"].update(ERROR_RESPONSES)
    list_op["responses"]["200"]["description"] = "Virtual cards retrieved successfully"
    list_op["responses"]["200"]["content"]["application/json"]["examples"] = {
        "success": {
            "summary": "Issued cards (customer and business)",
            "value": LIST_CARDS_RESPONSE,
        }
    }
    list_op["description"] = (
        "List issued virtual cards for the authenticated business "
        "(customer and business cards). Returns masked_pan only — use Get a Card "
        "for full card_number and cvv on a single card."
    )

    # create POST
    create_op = paths["/pms/api/external/request/virtual-cards/"]["post"]
    enrich_operation(create_op, with_body=True)
    create_op["responses"]["201"]["description"] = "Virtual card creation started"
    create_op["responses"]["201"]["content"]["application/json"]["examples"] = {
        "pending": {
            "summary": "Card creation started",
            "value": {
                "status": True,
                "message": "Virtual card creation started",
                "data": {
                    "id": "7f219a25-d968-4894-9a8b-ba83fa0bf6ec",
                    "status": "PENDING",
                    "masked_pan": "",
                    "balance": "10.00",
                    "currency": "USD",
                    "brand": "VISA",
                },
            },
        }
    }

    for subpath, methods in [
        ("/fees/quote/", {"post": True}),
        ("/{card_id}/", {"get": False}),
        ("/{card_id}/transactions/", {"get": False}),
        ("/{card_id}/fund/", {"post": True}),
        ("/{card_id}/withdraw/", {"post": True}),
        ("/{card_id}/freeze/", {"post": False}),
        ("/{card_id}/unfreeze/", {"post": False}),
        ("/{card_id}/terminate/", {"post": False}),
        ("/{card_id}/mock-transaction/", {"post": True}),
    ]:
        full = f"/pms/api/external/request/virtual-cards{subpath}"
        for method, needs_body in methods.items():
            op = paths[full][method]
            params: list = auth_headers(with_body=needs_body)
            if "{card_id}" in subpath:
                params.append(deepcopy(card_id_param))
            if subpath.endswith("transactions/"):
                params.append(
                    {
                        "name": "size",
                        "in": "query",
                        "required": False,
                        "description": "Max rows (default 50, max 100)",
                        "schema": {"type": "integer", "default": 50, "maximum": 100},
                    }
                )
            op["parameters"] = params
            op.pop("security", None)
            op["responses"].update(ERROR_RESPONSES)

    get_card = paths["/pms/api/external/request/virtual-cards/{card_id}/"]["get"]
    get_card["responses"]["200"]["content"]["application/json"]["examples"] = {
        "active": {
            "summary": "Active card with full credentials",
            "value": {
                "status": True,
                "message": "Virtual card retrieved successfully",
                "data": {
                    "id": "7f219a25-d968-4894-9a8b-ba83fa0bf6ec",
                    "business_id": "8f926b04-e63a-4449-b346-ea922b69e20e",
                    "kind": "customer",
                    "customer_id": "5e6bda15-1090-4cfe-bc1d-861990947bbc",
                    "customer_name": "MUSA GANIYU",
                    "business_name": None,
                    "card_name": "Ganiyu Musa",
                    "status": "ACTIVE",
                    "currency": "USD",
                    "brand": "MASTERCARD",
                    "balance": "3.00",
                    "expiry": "08/31",
                    "card_number": "5573 5078 9962 7848",
                    "cvv": "123",
                    "created_datetime": "2026-05-24T00:38:02.543669",
                    "updated_datetime": "2026-05-24T03:20:19.331923",
                },
            },
        }
    }

    OPENAPI.write_text(json.dumps(spec, indent=2) + "\n")
    print("Enriched Issuing OpenAPI paths and schemas")


if __name__ == "__main__":
    main()

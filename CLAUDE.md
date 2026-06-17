# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

PayVessel API documentation site built with [Mintlify](https://mintlify.com/docs). Content is `.mdx` files; configuration lives in `docs.json`.

## Development Commands

```bash
npm run dev          # Local preview (uses Homebrew Node 22 if available)
npm run dev:docker   # Docker-based preview (no Node version issues)
```

Preview runs at http://localhost:3000. The Mint CLI may log `localStorage`/`Invalid URL` noise in the terminal -- ignore it if the browser preview loads.

**Node version constraint:** Mintlify CLI requires Node < 25. The `npm run dev` script (`scripts/run-mint-dev.cjs`) auto-detects Homebrew Node 22 and uses it. If Node 22 isn't installed and system Node is 25+, it will error and suggest `brew install node@22` or Docker.

## Architecture

- **`docs.json`** -- Central config: navigation structure (two tabs: Guides + API reference), theme, SEO, colors, logo, footer. All page routing is defined here.
- **`api-reference/openapi.json`** -- OpenAPI spec powering the interactive API playground. Endpoint pages under `api-reference/` are auto-generated from this.
- **`api-reference/virtual-cards-openapi-patch.json`** -- Patch file for virtual cards OpenAPI spec.
- **`snippets/`** -- Reusable MDX fragments (e.g., `snippet-intro.mdx`).
- **`scripts/`** -- Python scripts to enrich/merge OpenAPI specs and strip auth header parameters. Run manually when the upstream API spec changes.

### Content Organization

Pages are organized by product domain, each in its own directory:
- `accept-payment/`, `transfer-payout/`, `wallets/`, `virtual-accounts/`, `virtual-cards/`, `identity-verification/` -- Guide-style pages (concepts, flows, integration advice)
- `api-reference/` -- Endpoint reference pages (HTTP methods, schemas, code samples) with subdirectories mirroring the guide structure

To add a new page: create the `.mdx` file, then add its path to the appropriate group in `docs.json` navigation.

## Deployment

Push to the default branch (`main`). Mintlify's GitHub app auto-deploys to production.

## Writing Conventions

- Pages use MDX with Mintlify components (`Card`, `CardGroup`, `CodeGroup`, `Accordion`, `Warning`, `Note`, `Tip`, etc.)
- Frontmatter includes `title`, `description`, `sidebarTitle`, and `keywords` for SEO
- Avoid em dashes in prose

# Mintlify Starter Kit

Use the starter kit to get your docs deployed and ready to customize.

Click the green **Use this template** button at the top of this repo to copy the Mintlify starter kit. The starter kit contains examples with

- Guide pages
- Navigation
- Customizations
- API reference pages
- Use of popular components

**[Follow the full quickstart guide](https://starter.mintlify.com/quickstart)**

## Development

**Prefer `npm run dev`** — it runs **`npx mint@latest dev`** under **Homebrew Node 22** when installed (`brew install node@22`), so a system-wide **Node 25+** does not break the Mint preview (see [mintlify/starter#116](https://github.com/mintlify/starter/issues/116)).

```bash
npm run dev
```

The Mint CLI may still print `localStorage` / `Invalid URL` lines in the terminal; if the preview URL opens in the browser, you can ignore that until Mint fixes it.

**Docker (no local Node version juggling):**

```bash
npm run dev:docker
```

Optional global CLI: `npm i -g mint`. View the preview at **http://localhost:3000** (or the port printed in the terminal).

## Publishing changes

Install our GitHub app from your [dashboard](https://dashboard.mintlify.com/settings/organization/github-app) to propagate changes from your repo to your deployment. Changes are deployed to production automatically after pushing to the default branch.

## Need help?

### Troubleshooting

- If your dev environment isn't running: Run `mint update` to ensure you have the most recent version of the CLI.
- If a page loads as a 404: Make sure you are running in a folder with a valid `docs.json`.

### Resources
- [Mintlify documentation](https://mintlify.com/docs)

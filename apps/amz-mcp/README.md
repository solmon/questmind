# amz-mcp: MCP server for fetching Amazon products

This project is a Node.js-based MCP (Model Context Protocol) server for fetching Amazon products. It uses Express for the API, zod for validation, and is compatible with the pnpm monorepo setup.

## Scripts
- `pnpm dev` — Start the server in development mode
- `pnpm start` — Start the server

## API
- POST `/products` — Query Amazon products (see `src/index.js` for schema)

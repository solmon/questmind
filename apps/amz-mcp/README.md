# amz-mcp: MCP server for fetching Amazon products

This project is a Node.js-based MCP (Model Context Protocol) server for fetching Amazon products using the Amazon Selling Partner API. It uses Express for the API, zod for validation, and is compatible with the pnpm monorepo setup.

## Features
- Search Amazon products by keywords and category
- Get detailed product information by ASIN
- Get product reviews (limited data through SP API)

## Setup

### Prerequisites
1. Amazon Selling Partner API credentials
2. AWS IAM user with appropriate permissions
3. Node.js 18+ and pnpm

### Proxy Configuration (Zscaler/Corporate Proxies)
This application is configured to work behind corporate proxies like Zscaler by disabling SSL certificate verification. This is handled automatically in the `amazonSPClient.js` file.

### Configuration
1. Copy `.env.local` and fill in your Amazon SP API credentials:
   ```bash
   AMAZON_CLIENT_ID=your_client_id_here
   AMAZON_CLIENT_SECRET=your_client_secret_here
   AMAZON_REFRESH_TOKEN=your_refresh_token_here
   AMAZON_MARKETPLACE_ID=ATVPDKIKX0DER
   AMAZON_REGION=us-east-1
   AMAZON_ACCESS_KEY_ID=your_access_key_id_here
   AMAZON_SECRET_ACCESS_KEY=your_secret_access_key_here
   ```

2. Install dependencies:
   ```bash
   pnpm install
   ```

## Scripts
- `pnpm dev` — Start the server in development mode
- `pnpm start` — Start the server

## API
The MCP server exposes the following tools:

### searchAmazonProducts
Search for Amazon products by keywords and optional category.
- **Parameters:**
  - `keywords` (string): Search keywords
  - `category` (string, optional): Browse node ID for category filtering
  - `maxResults` (number, optional): Maximum results to return (1-50, default: 10)

### getProductInfo  
Get detailed product information by ASIN.
- **Parameters:**
  - `id` (string): Amazon ASIN

### getProductReview
Get product reviews by ASIN (limited data available through SP API).
- **Parameters:**
  - `id` (string): Amazon ASIN

## Amazon SP API Setup
To use this MCP server, you need to:

1. Register as an Amazon developer
2. Create a Selling Partner API application
3. Get approval for the required API sections
4. Set up AWS IAM credentials
5. Generate refresh tokens

Refer to [Amazon's SP API documentation](https://developer-docs.amazon.com/sp-api/) for detailed setup instructions.

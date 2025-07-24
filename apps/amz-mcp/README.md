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

To use this MCP server with real Amazon data, you need to set up both SP API application credentials and AWS IAM credentials:

### 1. SP API Application Setup ✅ (You have these)
You already have these credentials configured in your `.env.local`:
- `AMAZON_CLIENT_ID`
- `AMAZON_CLIENT_SECRET` 
- `AMAZON_REFRESH_TOKEN`

### 2. AWS IAM User Setup ❌ (Required - currently using placeholders)

You need to create an AWS IAM user with the proper permissions for the SP API:

#### Step 1: Create IAM User
1. Go to AWS Console → IAM → Users → Add user
2. Username: `sp-api-user` (or any name you prefer)
3. Access type: **Programmatic access** (to get Access Key ID and Secret)

#### Step 2: Attach SP API Policy
Create a custom policy with these permissions:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "execute-api:Invoke"
            ],
            "Resource": "arn:aws:execute-api:*:*:*"
        }
    ]
}
```

#### Step 3: Get Credentials
After creating the user, AWS will provide:
- **Access Key ID** → Use for `AMAZON_ACCESS_KEY_ID`
- **Secret Access Key** → Use for `AMAZON_SECRET_ACCESS_KEY`

#### Step 4: Update .env.local
Replace the placeholder values:
```bash
AMAZON_ACCESS_KEY_ID=AKIA... # Your actual AWS Access Key ID
AMAZON_SECRET_ACCESS_KEY=... # Your actual AWS Secret Access Key
```

### 3. Testing with Sandbox
The server is currently configured for sandbox mode (`AMAZON_SANDBOX=true`). This is perfect for testing, but you still need valid AWS IAM credentials even in sandbox mode.

### 4. Troubleshooting
- **"Access to requested resource is denied"** → Usually means missing/invalid AWS IAM credentials
- **SSL/TLS errors** → Already handled with Zscaler proxy bypass
- **Mock data being used** → Check that all credentials are properly set (no placeholders)

For detailed Amazon SP API setup, refer to [Amazon's SP API documentation](https://developer-docs.amazon.com/sp-api/).

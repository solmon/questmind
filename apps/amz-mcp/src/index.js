import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { randomUUID } from "node:crypto";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js"
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";
import express from "express";
import AmazonSPClient from "./amazonSPClient.js";

const app = express();
app.use(express.json());

// Initialize Amazon SP API client
const amazonClient = new AmazonSPClient();

// Create MCP Server instance once
const mcpServer = new McpServer({
    name: 'amz-mcp',
    version: '1.0.0',
});

// Register tools once
mcpServer.tool(
    'searchAmazonProducts',
    'Search for Amazon products by keywords and category',
    {
        keywords: z.string(),
        category: z.string().optional(),
        maxResults: z.number().int().min(1).max(50).default(10)
    },
    async (args) => {
        try {
            const products = await amazonClient.searchProducts(
                args.keywords,
                args.category,
                args.maxResults
            );
            
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(products, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: `Error searching Amazon products: ${error.message}`
                    }
                ],
                isError: true
            };
        }
    }
);

mcpServer.tool(
    'getProductInfo',
    'Get product details by product ID (ASIN)',
    {
        id: z.string()
    },
    async ({ id }) => {
        try {
            const product = await amazonClient.getProductInfo(id);
            
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(product, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: `Error getting product info: ${error.message}`
                    }
                ],
                isError: true
            };
        }
    }
);

mcpServer.tool(
    'getProductReview',
    'Get product reviews by product ID (ASIN) - Note: Limited data available through SP API',
    {
        id: z.string()
    },
    async ({ id }) => {
        try {
            const reviews = await amazonClient.getProductReviews(id);
            
            return {
                content: [
                    {
                        type: "text",
                        text: JSON.stringify(reviews, null, 2)
                    }
                ]
            };
        } catch (error) {
            return {
                content: [
                    {
                        type: "text",
                        text: `Error getting product reviews: ${error.message}`
                    }
                ],
                isError: true
            };
        }
    }
);

app.post('/mcp', async (req, res) => {
    try {
        const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: undefined,
        });
        
        res.on('close', () => {
            console.log('Request closed');
            transport.close();
            mcpServer.close();
        });

        await mcpServer.connect(transport);
        await transport.handleRequest(req, res, req.body);
    } catch (error) {
        console.error('Error handling MCP request:', error);
        if (!res.headersSent) {
            res.status(500).json({
                jsonrpc: '2.0',
                error: {
                    code: -32603,
                    message: 'Internal server error',
                },
                id: null,
            });
        }
    }
});

// Reusable handler for GET and DELETE requests
const handleSessionRequest = async (req, res) => {
    res.status(400).send('Invalid or missing session ID');
};

// SSE notifications not supported in stateless mode
app.get('/mcp', async (req, res) => {
    console.log('Received GET MCP request');
    res.writeHead(405).end(JSON.stringify({
        jsonrpc: "2.0",
        error: {
            code: -32000,
            message: "Method not allowed."
        },
        id: null
    }));
});

// Session termination not needed in stateless mode
app.delete('/mcp', async (req, res) => {
    console.log('Received DELETE MCP request');
    res.writeHead(405).end(JSON.stringify({
        jsonrpc: "2.0",
        error: {
            code: -32000,
            message: "Method not allowed."
        },
        id: null
    }));
});


// Start the server
const PORT = 3000;

app.listen(PORT, (error) => {
    if (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
    console.log(`MCP Stateless Streamable HTTP Server listening on port ${PORT}`);
});

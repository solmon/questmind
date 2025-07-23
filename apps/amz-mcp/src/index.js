import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp.js";
import { randomUUID } from "node:crypto";
// import { McpServer, ResourceTemplate } from "@modelcontextprotocol/sdk/server/mcp";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
// import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio";
// import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { isInitializeRequest } from "@modelcontextprotocol/sdk/types.js"
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { z } from "zod";
import express from "express";

const app = express();
app.use(express.json());
// const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};
// const transports = {};
// --- Schemas ---
const ProductQuerySchema = z.object({
    keywords: z.string(),
    category: z.string().optional(),
    maxResults: z.number().int().min(1).max(50).default(10)
});

const ProductIdSchema = z.object({
    id: z.string()
});

const ProductSchema = z.object({
    id: z.string(),
    title: z.string(),
    price: z.string().optional(),
    url: z.string(),
    image: z.string().optional()
});

const ProductReviewSchema = z.object({
    productId: z.string(),
    reviews: z.array(z.object({
        author: z.string(),
        rating: z.number().min(1).max(5),
        text: z.string()
    }))
});

app.post('/mcp', async (req, res) => {
    // Check for existing session ID
    // const sessionId = req.headers['mcp-session-id'];
    // let transport;

    // if (sessionId && transports[sessionId]) {
    //     // Reuse existing transport
    //     transport = transports[sessionId];
    // } else if (!sessionId && isInitializeRequest(req.body)) {
    // New initialization request

    try {

        const mcpServer = new McpServer({
            name: 'amz-mcp',
            version: '1.0.0',
        });
        // const server = getServer();
        const transport = new StreamableHTTPServerTransport({
            sessionIdGenerator: undefined,
        });
        res.on('close', () => {
            console.log('Request closed');
            transport.close();
            mcpServer.close();
        });

        // transport = new StreamableHTTPServerTransport({
        //     sessionIdGenerator: () => randomUUID(),
        //     onsessioninitialized: (sessionId) => {
        //         // Store the transport by session ID
        //         transports[sessionId] = transport;
        //     },
        //     // DNS rebinding protection is disabled by default for backwards compatibility. If you are running this server
        //     // locally, make sure to set:
        //     // enableDnsRebindingProtection: true,
        //     // allowedHosts: ['127.0.0.1'],
        // });

        // Clean up transport when closed
        // transport.onclose = () => {
        //     if (transport.sessionId) {
        //         delete transports[transport.sessionId];
        //     }
        // };

        // --- MCP Server Setup ---
        // const mcpServer = new McpServer({
        //     name: 'amz-mcp',
        //     version: '1.0.0',
        // });

        mcpServer.registerTool('searchAmazonProducts', {
            title: 'Search Amazon Products',
            description: 'Search for Amazon products by keywords and category',
            inputSchema: ProductQuerySchema.shape,
            outputSchema: z.array(ProductSchema).element,
        }, async (args) => {
            // TODO: Integrate with Amazon Product API or scraping logic
            return {
                structuredContent: [
                    {
                        id: 'B000123',
                        title: 'Sample Product',
                        price: '$19.99',
                        url: 'https://amazon.com/dp/B000123',
                        image: null
                    }
                ]
            };
        });

        mcpServer.registerTool('getProductInfo', {
            title: 'Get Product Info',
            description: 'Get product details by product ID',
            inputSchema: ProductIdSchema.shape,
            outputSchema: ProductSchema.shape,
        }, async ({ id }) => {
            // TODO: Integrate with Amazon Product API or scraping logic
            return {
                structuredContent: {
                    id,
                    title: 'Sample Product',
                    price: '$19.99',
                    url: `https://amazon.com/dp/${id}`,
                    image: null
                }
            };
        });

        mcpServer.registerTool('getProductReview', {
            title: 'Get Product Review',
            description: 'Get product reviews by product ID',
            inputSchema: ProductIdSchema.shape,
            outputSchema: ProductReviewSchema.shape,
        }, async ({ id }) => {
            // TODO: Integrate with Amazon Product API or scraping logic
            return {
                structuredContent: {
                    productId: id,
                    reviews: [
                        {
                            author: 'John Doe',
                            rating: 5,
                            text: 'Great product!'
                        },
                        {
                            author: 'Jane Smith',
                            rating: 4,
                            text: 'Good value for money.'
                        }
                    ]
                }
            };
        });

        await mcpServer.connect(transport);
        // } else {
        //     // Invalid request
        //     res.status(400).json({
        //         jsonrpc: '2.0',
        //         error: {
        //             code: -32000,
        //             message: 'Bad Request: No valid session ID provided',
        //         },
        //         id: null,
        //     });
        //     return;
        // }

        // Handle the request
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
// Start receiving messages on stdin and sending messages on stdout
// const transport = new StdioServerTransport();
// await mcpServer.connect(transport);
// await mcpServer.connect(new StreamableHTTPServerTransport({ port: 3000 }));

// Reusable handler for GET and DELETE requests
const handleSessionRequest = async (req, res) => {
    const sessionId = req.headers['mcp-session-id'];
    if (!sessionId || !transports[sessionId]) {
        res.status(400).send('Invalid or missing session ID');
        return;
    }

    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
};

// // Handle GET requests for server-to-client notifications via SSE
// app.get('/mcp', handleSessionRequest);

// // Handle DELETE requests for session termination
// app.delete('/mcp', handleSessionRequest);


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

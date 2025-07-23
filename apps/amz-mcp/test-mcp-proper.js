#!/usr/bin/env node

import fetch from 'node-fetch';

const MCP_SERVER_URL = 'http://localhost:3000/mcp';

// Helper function to make MCP requests with proper headers
async function mcpRequest(method, params = {}) {
    const payload = {
        jsonrpc: '2.0',
        id: Math.random().toString(36).substring(7),
        method: method,
        params: params
    };

    try {
        const response = await fetch(MCP_SERVER_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/event-stream',
                'User-Agent': 'MCP-Test-Client/1.0'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            console.error(`HTTP ${response.status}: ${response.statusText}`);
            const errorText = await response.text();
            console.error('Response:', errorText);
            return;
        }

        const contentType = response.headers.get('content-type');
        
        if (contentType && contentType.includes('text/event-stream')) {
            // Handle SSE response
            const text = await response.text();
            return parseSSEResponse(text);
        } else {
            // Handle JSON response
            const result = await response.json();
            return result;
        }
    } catch (error) {
        console.error('Request failed:', error.message);
        return null;
    }
}

// Parse Server-Sent Events response
function parseSSEResponse(text) {
    const lines = text.split('\n');
    let data = '';
    
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            data += line.substring(6);
        }
    }
    
    if (data) {
        try {
            return JSON.parse(data);
        } catch (error) {
            console.error('Failed to parse SSE data:', error.message);
            console.error('Raw data:', data);
            return null;
        }
    }
    
    return null;
}

// Test functions
async function testInitialize() {
    console.log('\n🔄 Testing initialize...');
    const result = await mcpRequest('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
            tools: {}
        },
        clientInfo: {
            name: 'test-client',
            version: '1.0.0'
        }
    });
    
    if (result) {
        console.log('✅ Initialize successful');
        console.log('Server capabilities:', JSON.stringify(result.result?.capabilities, null, 2));
    } else {
        console.log('❌ Initialize failed');
    }
    return result;
}

async function testListTools() {
    console.log('\n🔄 Testing tools/list...');
    const result = await mcpRequest('tools/list', {});
    
    if (result && result.result) {
        console.log('✅ List tools successful');
        console.log('Available tools:');
        result.result.tools?.forEach(tool => {
            console.log(`  - ${tool.name}: ${tool.description}`);
        });
    } else {
        console.log('❌ List tools failed');
        if (result?.error) {
            console.log('Error:', result.error);
        }
    }
    return result;
}

async function testSearchProducts() {
    console.log('\n🔄 Testing searchAmazonProducts...');
    const result = await mcpRequest('tools/call', {
        name: 'searchAmazonProducts',
        arguments: {
            keywords: 'laptop',
            maxResults: 3
        }
    });
    
    if (result && result.result) {
        console.log('✅ Search products successful');
        console.log('Result:', result.result.content?.[0]?.text || 'No content');
    } else {
        console.log('❌ Search products failed');
        if (result?.error) {
            console.log('Error:', result.error);
        }
    }
    return result;
}

async function testGetProductInfo() {
    console.log('\n🔄 Testing getProductInfo...');
    const result = await mcpRequest('tools/call', {
        name: 'getProductInfo',
        arguments: {
            id: 'B08N5WRWNW'
        }
    });
    
    if (result && result.result) {
        console.log('✅ Get product info successful');
        console.log('Result:', result.result.content?.[0]?.text || 'No content');
    } else {
        console.log('❌ Get product info failed');
        if (result?.error) {
            console.log('Error:', result.error);
        }
    }
    return result;
}

async function testGetProductReviews() {
    console.log('\n🔄 Testing getProductReview...');
    const result = await mcpRequest('tools/call', {
        name: 'getProductReview',
        arguments: {
            id: 'B08N5WRWNW'
        }
    });
    
    if (result && result.result) {
        console.log('✅ Get product reviews successful');
        console.log('Result:', result.result.content?.[0]?.text || 'No content');
    } else {
        console.log('❌ Get product reviews failed');
        if (result?.error) {
            console.log('Error:', result.error);
        }
    }
    return result;
}

// Run all tests
async function runTests() {
    console.log('🚀 Starting MCP Server Tests...');
    console.log('Server URL:', MCP_SERVER_URL);
    
    // Test initialization first
    const initResult = await testInitialize();
    if (!initResult || initResult.error) {
        console.log('\n❌ Initialization failed, skipping other tests');
        return;
    }
    
    // Test listing tools
    await testListTools();
    
    // Test tool calls
    await testSearchProducts();
    await testGetProductInfo();
    await testGetProductReviews();
    
    console.log('\n🎉 All tests completed!');
}

// Handle graceful shutdown
process.on('SIGINT', () => {
    console.log('\n👋 Test interrupted by user');
    process.exit(0);
});

// Run tests
runTests().catch(error => {
    console.error('Test runner failed:', error);
    process.exit(1);
});

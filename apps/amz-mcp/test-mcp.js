#!/usr/bin/env node

import fetch from 'node-fetch';

const BASE_URL = 'http://localhost:3000';

// Test MCP protocol requests
async function testMCPEndpoint(method, params = {}) {
    const payload = {
        jsonrpc: '2.0',
        method: method,
        params: params,
        id: Math.floor(Math.random() * 1000)
    };

    console.log(`\n🧪 Testing ${method}...`);
    console.log('📤 Request:', JSON.stringify(payload, null, 2));

    try {
        const response = await fetch(`${BASE_URL}/mcp`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        console.log('📥 Response:', JSON.stringify(result, null, 2));
        
        if (result.error) {
            console.log('❌ Error:', result.error.message);
        } else {
            console.log('✅ Success!');
        }
        
        return result;
    } catch (error) {
        console.log('💥 Network Error:', error.message);
        return null;
    }
}

async function runTests() {
    console.log('🚀 Starting MCP Server Tests\n');

    // Test 1: Initialize the MCP connection
    await testMCPEndpoint('initialize', {
        protocolVersion: '2024-11-05',
        capabilities: {
            tools: {}
        },
        clientInfo: {
            name: 'test-client',
            version: '1.0.0'
        }
    });

    // Test 2: List available tools
    await testMCPEndpoint('tools/list', {});

    // Test 3: Call searchAmazonProducts tool
    await testMCPEndpoint('tools/call', {
        name: 'searchAmazonProducts',
        arguments: {
            keywords: 'wireless headphones',
            maxResults: 3
        }
    });

    // Test 4: Call getProductInfo tool
    await testMCPEndpoint('tools/call', {
        name: 'getProductInfo',
        arguments: {
            id: 'B08N5WRWNW'
        }
    });

    // Test 5: Call getProductReview tool
    await testMCPEndpoint('tools/call', {
        name: 'getProductReview',
        arguments: {
            id: 'B08N5WRWNW'
        }
    });

    console.log('\n🏁 All tests completed!');
}

// Run the tests
runTests().catch(console.error);

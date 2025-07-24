import dotenv from 'dotenv';
import SellingPartner from 'amazon-sp-api';
import https from 'https';

// Load environment variables
dotenv.config({ path: '.env.local' });

console.log('🔐 Amazon SP API Credential Verification\n');

// Check all required environment variables
const requiredCredentials = [
    'AMAZON_CLIENT_ID',
    'AMAZON_CLIENT_SECRET',
    'AMAZON_REFRESH_TOKEN',    
    'AMAZON_MARKETPLACE_ID'
];

console.log('📋 Checking environment variables...');
let allPresent = true;

for (const cred of requiredCredentials) {
    const value = process.env[cred];
    const isPresent = value && !value.includes('your_') && !value.includes('_here');

    console.log(`  ${isPresent ? '✅' : '❌'} ${cred}: ${isPresent ? 'SET' : 'MISSING/PLACEHOLDER'}`);

    if (!isPresent) {
        allPresent = false;
    }
}

if (!allPresent) {
    console.log('\n❌ Some credentials are missing or still using placeholder values.');
    console.log('Please update your .env.local file with actual AWS IAM credentials.');
    console.log('\nSee README.md for detailed setup instructions.');
    process.exit(1);
}

console.log('\n✅ All credentials are present!');
console.log('\n🔄 Testing SP API connection...');

try {
    // Disable SSL verification for proxy environments
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

    const sellingPartner = new SellingPartner({
        region: 'na', // North America
        refresh_token: process.env.AMAZON_REFRESH_TOKEN,
        credentials: {
            SELLING_PARTNER_APP_CLIENT_ID: process.env.AMAZON_CLIENT_ID,
            SELLING_PARTNER_APP_CLIENT_SECRET: process.env.AMAZON_CLIENT_SECRET
        },
        options: {
            https_agent: new https.Agent({
                rejectUnauthorized: false
            }),
            use_sandbox: process.env.AMAZON_SANDBOX === 'true'
        }
    });

    console.log(`  Environment: ${process.env.AMAZON_SANDBOX === 'true' ? 'SANDBOX' : 'PRODUCTION'}`);
    console.log(`  Region: ${process.env.AMAZON_REGION || 'us-east-1'}`);
    console.log(`  Marketplace: ${process.env.AMAZON_MARKETPLACE_ID}`);

    // Try a simple API call (get marketplace participations)
    console.log('\n🧪 Testing API access...');

    
    let response = await sellingPartner.callAPI({
      operation: 'getMarketplaceParticipations',
      endpoint: 'sellers'
    });

    // let response = await sellingPartner.callAPI({
    //   operation: 'getAccount',
    //   endpoint: 'sellers'
    // });



    // const response = await sellingPartner.callAPI({
    //             operation: 'searchListingsItems',
    //             endpoint: 'listingsItems',
    //             version: 'v0',                
    //             path: {
    //                 sellerId: 'YOUR_SELLER_ID' // Correctly placed in the path
    //             },
    //             query: {
    //                 MarketplaceId: 'ATVPDKIKX0DER',
    //                 Keywords: 'wireless headphones'
    //             }
    //         });

    console.log('✅ SP API connection successful!');
    console.log('Response:', JSON.stringify(response, null, 2));

} catch (error) {
    console.log('❌ SP API connection failed:');
    console.log(`  Error: ${error.message}`);

    if (error.message.includes('Access to requested resource is denied')) {
        console.log('\n💡 This usually means:');
        console.log('  1. AWS IAM credentials are invalid');
        console.log('  2. IAM user lacks proper SP API permissions');
        console.log('  3. SP API application needs approval for this operation');
    }

    console.log('\n📖 Check the README.md for troubleshooting steps.');
}

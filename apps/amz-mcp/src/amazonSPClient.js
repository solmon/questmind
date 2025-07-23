import SellingPartner from 'amazon-sp-api';
import dotenv from 'dotenv';
import https from 'https';

// Load environment variables
dotenv.config({ path: '.env.local' });

// Disable SSL certificate verification for proxy environments
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

class AmazonSPClient {
    constructor() {
        // Check if credentials are provided
        if (!process.env.AMAZON_CLIENT_ID || !process.env.AMAZON_CLIENT_SECRET) {
            console.warn('Amazon SP API credentials not configured. Using mock data.');
            this.useMockData = true;
            return;
        }
        
        try {
            // Map AWS regions to SP API regions
            const regionMap = {
                'us-east-1': 'na',
                'us-west-2': 'na',
                'eu-west-1': 'eu',
                'ap-northeast-1': 'fe'
            };
            
            const awsRegion = process.env.AMAZON_REGION || 'us-east-1';
            const spRegion = regionMap[awsRegion] || 'na';
            
            this.sellingPartner = new SellingPartner({
                region: spRegion,
                refresh_token: process.env.AMAZON_REFRESH_TOKEN,
                credentials: {
                    SELLING_PARTNER_APP_CLIENT_ID: process.env.AMAZON_CLIENT_ID,
                    SELLING_PARTNER_APP_CLIENT_SECRET: process.env.AMAZON_CLIENT_SECRET,
                    AWS_ACCESS_KEY_ID: process.env.AMAZON_ACCESS_KEY_ID,
                    AWS_SECRET_ACCESS_KEY: process.env.AMAZON_SECRET_ACCESS_KEY,
                },
                // Configure for sandbox environment
                sandbox: process.env.AMAZON_SANDBOX === 'true',
                // Disable SSL verification for proxy environments
                options: {
                    https_agent: new https.Agent({
                        rejectUnauthorized: false
                    })
                }
            });
            this.marketplaceId = process.env.AMAZON_MARKETPLACE_ID || 'ATVPDKIKX0DER';
            this.useMockData = false;
        } catch (error) {
            console.warn('Failed to initialize Amazon SP API client:', error.message);
            console.warn('Using mock data instead.');
            this.useMockData = true;
        }
    }

    async searchProducts(keywords, category = null, maxResults = 10) {
        if (this.useMockData) {
            return this.getMockSearchResults(keywords, maxResults);
        }
        
        try {
            // Use Catalog Items API to search for products
            const searchParams = {
                marketplaceIds: [this.marketplaceId],
                keywords: keywords,
                pageSize: Math.min(maxResults, 20), // Amazon limits to 20 per page
            };

            if (category) {
                searchParams.browseNodeId = category;
            }

            const response = await this.sellingPartner.callAPI({
                operation: 'searchCatalogItems',
                endpoint: 'catalogItems',
                query: searchParams
            });

            return this.formatSearchResults(response.items || []);
        } catch (error) {
            console.error('Error searching products:', error);
            throw new Error(`Amazon SP API search failed: ${error.message}`);
        }
    }

    async getProductInfo(asin) {
        if (this.useMockData) {
            return this.getMockProductInfo(asin);
        }
        
        try {
            const response = await this.sellingPartner.callAPI({
                operation: 'getCatalogItem',
                endpoint: 'catalogItems',
                path: {
                    asin: asin
                },
                query: {
                    marketplaceIds: [this.marketplaceId],
                    includedData: ['attributes', 'images', 'productTypes', 'relationships', 'salesRanks']
                }
            });

            return this.formatProductInfo(response);
        } catch (error) {
            console.error('Error getting product info:', error);
            throw new Error(`Amazon SP API product info failed: ${error.message}`);
        }
    }

    async getProductReviews(asin) {
        if (this.useMockData) {
            return this.getMockProductReviews(asin);
        }
        
        try {
            // Note: Amazon SP API doesn't provide customer reviews directly
            // This is a placeholder that could be enhanced with Product Advertising API
            // or web scraping (with proper compliance to Amazon's terms)
            return {
                productId: asin,
                reviews: [
                    {
                        author: 'SP API User',
                        rating: 4,
                        text: 'Reviews not available through SP API. Consider using Product Advertising API or other approved methods.'
                    }
                ]
            };
        } catch (error) {
            console.error('Error getting product reviews:', error);
            throw new Error(`Amazon SP API reviews failed: ${error.message}`);
        }
    }

    // Mock data methods
    getMockSearchResults(keywords, maxResults) {
        const mockProducts = [];
        for (let i = 1; i <= Math.min(maxResults, 5); i++) {
            mockProducts.push({
                id: `B00MOCK${i.toString().padStart(3, '0')}`,
                title: `Mock Product ${i} for "${keywords}"`,
                price: `$${(19.99 + i * 5).toFixed(2)}`,
                url: `https://amazon.com/dp/B00MOCK${i.toString().padStart(3, '0')}`,
                image: null
            });
        }
        return mockProducts;
    }

    getMockProductInfo(asin) {
        return {
            id: asin,
            title: `Mock Product for ASIN ${asin}`,
            price: '$29.99',
            url: `https://amazon.com/dp/${asin}`,
            image: null,
            brand: 'Mock Brand',
            features: ['Mock feature 1', 'Mock feature 2', 'Mock feature 3'],
            dimensions: { length: 10, width: 8, height: 2, unit: 'inches' },
            weight: { value: 1.5, unit: 'pounds' }
        };
    }

    getMockProductReviews(asin) {
        return {
            productId: asin,
            reviews: [
                {
                    author: 'Mock Reviewer 1',
                    rating: 5,
                    text: 'Great mock product! Works as expected in demo mode.'
                },
                {
                    author: 'Mock Reviewer 2',
                    rating: 4,
                    text: 'Good value for a mock product. Configure real Amazon SP API for actual data.'
                }
            ]
        };
    }

    formatSearchResults(items) {
        return items.map(item => ({
            id: item.asin,
            title: item.attributes?.item_name?.[0]?.value || 'Unknown Product',
            price: this.formatPrice(item.attributes?.list_price?.[0]),
            url: `https://amazon.com/dp/${item.asin}`,
            image: item.images?.[0]?.images?.[0]?.link || null
        }));
    }

    formatProductInfo(product) {
        return {
            id: product.asin,
            title: product.attributes?.item_name?.[0]?.value || 'Unknown Product',
            price: this.formatPrice(product.attributes?.list_price?.[0]),
            url: `https://amazon.com/dp/${product.asin}`,
            image: product.images?.[0]?.images?.[0]?.link || null,
            brand: product.attributes?.brand?.[0]?.value || null,
            features: product.attributes?.bullet_point?.map(bp => bp.value) || [],
            dimensions: product.attributes?.item_dimensions || null,
            weight: product.attributes?.item_weight || null
        };
    }

    formatPrice(priceData) {
        if (!priceData) return null;
        return `${priceData.currency_code} ${priceData.amount}`;
    }
}

export default AmazonSPClient;

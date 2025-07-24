import SellingPartner from 'amazon-sp-api';
import dotenv from 'dotenv';
import https from 'https';

// Load environment variables
dotenv.config({ path: '.env.local' });

// Disable SSL certificate verification for proxy environments
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

class AmazonSPClient {
    constructor() {
        // Check if all required credentials are provided
        const requiredCredentials = [
            'AMAZON_CLIENT_ID',
            'AMAZON_CLIENT_SECRET', 
            'AMAZON_REFRESH_TOKEN',
            'AMAZON_ACCESS_KEY_ID',
            'AMAZON_SECRET_ACCESS_KEY'
        ];
        
        const missingCredentials = requiredCredentials.filter(cred => 
            !process.env[cred] || 
            process.env[cred].includes('your_') || 
            process.env[cred].includes('_here')
        );
        
        if (missingCredentials.length > 0) {
            console.warn(`Missing Amazon SP API credentials: ${missingCredentials.join(', ')}`);
            console.warn('Using mock data. Please configure all required credentials.');
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
                    SELLING_PARTNER_APP_CLIENT_SECRET: process.env.AMAZON_CLIENT_SECRET                    
                },
                // Configure for sandbox environment
                sandbox: process.env.AMAZON_SANDBOX === 'true',
                // Disable SSL verification for proxy environments
                options: {
                    https_agent: new https.Agent({
                        rejectUnauthorized: false
                    }),
                    use_sandbox: process.env.AMAZON_SANDBOX === 'true'
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
            console.log(`Searching for products with keywords: "${keywords}"`);
            console.log(`Marketplace: ${this.marketplaceId}`);
            console.log(`Sandbox mode: ${process.env.AMAZON_SANDBOX === 'true'}`);
            
            // Use the correct API structure for amazon-sp-api library
            const response = await this.sellingPartner.callAPI({
                operation: 'searchCatalogItems',
                endpoint: 'catalog',
                version: 'v0',
                query: {
                    MarketplaceId: this.marketplaceId,
                    Keywords: keywords,
                    MaxResultsPerPage: Math.min(maxResults, 20)
                }
            });

            console.log('SP API Response:', JSON.stringify(response, null, 2));
            return this.formatSearchResults(response.payload?.Items || []);
        } catch (error) {
            console.error('Error searching products:', error);
            console.error('Error details:', JSON.stringify(error, null, 2));
            
            // Fallback: Try with different API version
            try {
                console.log('Retrying with catalogItems v2022-04-01...');
                const fallbackResponse = await this.sellingPartner.callAPI({
                    operation: 'searchCatalogItems',
                    endpoint: 'catalogItems',
                    version: '2022-04-01',
                    query: {
                        marketplaceIds: [this.marketplaceId],
                        keywords: keywords,
                        pageSize: Math.min(maxResults, 20)
                    }
                });
                console.log('Fallback SP API Response:', JSON.stringify(fallbackResponse, null, 2));
                return this.formatSearchResults(fallbackResponse.items || []);
            } catch (fallbackError) {
                console.error('Fallback also failed:', fallbackError);
                throw new Error(`Amazon SP API search failed: ${error.message}`);
            }
        }
    }

    async getProductInfo(asin) {
        if (this.useMockData) {
            return this.getMockProductInfo(asin);
        }
        
        try {
            console.log(`Attempting to get product info for ASIN: ${asin}`);
            console.log(`Using marketplace: ${this.marketplaceId}`);
            console.log(`Sandbox mode: ${process.env.AMAZON_SANDBOX === 'true'}`);
            
            // Try the v0 catalog API first
            const response = await this.sellingPartner.callAPI({
                operation: 'getCatalogItem',
                endpoint: 'catalog',
                version: 'v0',
                path: {
                    asin: asin
                },
                query: {
                    MarketplaceId: this.marketplaceId
                }
            });

            console.log('SP API Response:', JSON.stringify(response, null, 2));
            return this.formatProductInfoV0(response.payload || {});
        } catch (error) {
            console.error('Error getting product info (v0):', error);
            console.error('Error details:', JSON.stringify(error, null, 2));
            
            // Try the newer catalogItems API as fallback
            try {
                console.log('Retrying with catalogItems v2022-04-01...');
                const fallbackResponse = await this.sellingPartner.callAPI({
                    operation: 'getCatalogItem',
                    endpoint: 'catalogItems',
                    version: '2022-04-01',
                    path: {
                        asin: asin
                    },
                    query: {
                        marketplaceIds: [this.marketplaceId],
                        includedData: ['attributes', 'images', 'productTypes']
                    }
                });
                console.log('Fallback SP API Response:', JSON.stringify(fallbackResponse, null, 2));
                return this.formatProductInfo(fallbackResponse);
            } catch (fallbackError) {
                console.error('Fallback also failed:', fallbackError);
                
                // Final attempt with minimal parameters for sandbox
                if (process.env.AMAZON_SANDBOX === 'true') {
                    try {
                        console.log('Final attempt with minimal parameters...');
                        const minimalResponse = await this.sellingPartner.callAPI({
                            operation: 'getCatalogItem',
                            endpoint: 'catalogItems',
                            version: '2022-04-01',
                            path: {
                                asin: asin
                            },
                            query: {
                                marketplaceIds: [this.marketplaceId]
                            }
                        });
                        return this.formatProductInfo(minimalResponse);
                    } catch (minimalError) {
                        console.error('All attempts failed:', minimalError);
                        throw new Error(`Amazon SP API product info failed: ${error.message}`);
                    }
                }
                
                throw new Error(`Amazon SP API product info failed: ${error.message}`);
            }
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
        return items.map(item => {
            // Handle both v0 and v2022-04-01 API response formats
            if (item.Identifiers) {
                // v0 format
                return {
                    id: item.Identifiers.MarketplaceASIN?.ASIN || 'unknown',
                    title: item.AttributeSets?.[0]?.Title || 'Unknown Product',
                    price: this.formatPriceV0(item.AttributeSets?.[0]?.ListPrice),
                    url: item.DetailPageURL || `https://amazon.com/dp/${item.Identifiers.MarketplaceASIN?.ASIN}`,
                    image: item.AttributeSets?.[0]?.SmallImage?.URL || null
                };
            } else {
                // v2022-04-01 format
                return {
                    id: item.asin,
                    title: item.attributes?.item_name?.[0]?.value || 'Unknown Product',
                    price: this.formatPrice(item.attributes?.list_price?.[0]),
                    url: `https://amazon.com/dp/${item.asin}`,
                    image: item.images?.[0]?.images?.[0]?.link || null
                };
            }
        });
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

    formatProductInfoV0(product) {
        // Format for the older v0 catalog API response structure
        return {
            id: product.Identifiers?.MarketplaceASIN?.ASIN || 'unknown',
            title: product.AttributeSets?.[0]?.Title || 'Unknown Product',
            price: this.formatPriceV0(product.AttributeSets?.[0]?.ListPrice),
            url: product.DetailPageURL || `https://amazon.com/dp/${product.Identifiers?.MarketplaceASIN?.ASIN}`,
            image: product.AttributeSets?.[0]?.SmallImage?.URL || null,
            brand: product.AttributeSets?.[0]?.Brand || null,
            features: product.AttributeSets?.[0]?.Feature || [],
            dimensions: product.AttributeSets?.[0]?.PackageDimensions || null,
            weight: product.AttributeSets?.[0]?.ItemDimensions?.Weight || null
        };
    }

    formatPrice(priceData) {
        if (!priceData) return null;
        return `${priceData.currency_code} ${priceData.amount}`;
    }

    formatPriceV0(priceData) {
        if (!priceData) return null;
        return `${priceData.CurrencyCode} ${priceData.Amount}`;
    }
}

export default AmazonSPClient;

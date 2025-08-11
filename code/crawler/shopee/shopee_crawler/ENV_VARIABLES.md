# Environment Variables Documentation

## Shopee API Configuration

### Base URLs
- `SHOPEE_AUTH_BASEURL`: Base URL for Shopee authentication endpoints
- `SHOPEE_AUTH_LINK`: Full URL for shop authorization
- `SHOPEE_SHOP_AUTH_CALLBACK`: Callback URL after successful authorization
- `SHOPEE_OPEN_API_BASEURL`: Base URL for Shopee Open API endpoints

### Partner Credentials
- `SHOPEE_PARTNER_ID`: Your Shopee Partner ID
- `SHOPEE_PARTNER_KEY`: Your Shopee Partner Key (keep secret!)

### Domain Configuration
These variables control which domains are used for different environments:

#### Production Environment
- `SHOPEE_PRODUCTION_API_DOMAIN`: Production API domain (`partner.shopeemobile.com`)
- `SHOPEE_PRODUCTION_AUTH_DOMAIN`: Production auth domain (`open.shopeemobile.com`)

#### Sandbox Environment
- `SHOPEE_SANDBOX_API_DOMAIN`: Sandbox API domain (`openplatform.sandbox.test-stable.shopee.sg`)
- `SHOPEE_SANDBOX_AUTH_DOMAIN`: Sandbox auth domain (`open.sandbox.test-stable.shopee.com`)

## Environment-specific Configuration

### Local Development (.env.local)
```bash
# Uses sandbox environment for testing
SHOPEE_SANDBOX_API_DOMAIN=openplatform.sandbox.test-stable.shopee.sg
SHOPEE_SANDBOX_AUTH_DOMAIN=open.sandbox.test-stable.shopee.com
```

### Production (compose.yaml)
```yaml
# Uses production environment or staging environment
SHOPEE_PRODUCTION_API_DOMAIN: partner.shopeemobile.com
SHOPEE_SANDBOX_API_DOMAIN: partner.test-stable.shopeemobile.com
```

## Migration from Hardcoded URLs

Previously hardcoded URLs have been moved to environment variables:

1. **API Domain** (`utils/utils.py` line 55): 
   - From: `"openplatform.sandbox.test-stable.shopee.sg"`
   - To: `settings.SHOPEE_SANDBOX_API_DOMAIN`

2. **Auth Domain** (`utils/utils.py` line 66):
   - From: `'open.sandbox.test-stable.shopee.com'`  
   - To: `settings.SHOPEE_SANDBOX_AUTH_DOMAIN`

This allows for easy switching between sandbox and production environments by changing environment variables instead of modifying code.

# Paycrypt Client API Integration Credentials System

## Overview

You're absolutely correct! For client self-service API integration, each client needs access to their complete set of API credentials. I've implemented a comprehensive system that provides each client with:

1. **API Key** (`PAYCRYPT_API_KEY`)
2. **Secret Key** (`PAYCRYPT_SECRET_KEY`) 
3. **Webhook Secret** (`PAYCRYPT_WEBHOOK_SECRET`)
4. **Base URL** (`PAYCRYPT_BASE_URL`)

## Implementation

### 1. Database Schema Enhancement
- Added `secret_key` column to `client_api_keys` table
- Enhanced existing `webhook_secret` column functionality
- Updated API key creation methods to generate all credentials

### 2. Client Web Interface Routes
- **API Keys List**: `http://127.0.0.1:8000/client/api-keys`
- **API Key Credentials**: `http://127.0.0.1:8000/client/api-keys/<key_id>/details`
- **API Documentation**: `http://127.0.0.1:8000/client/api-docs`

### 3. Complete Credentials Display
Each client can now access a beautifully designed credentials page showing:

#### For SmartBetslip (SBS) Client:
```env
PAYCRYPT_API_KEY=pk_bAfM0swfeiwU8yrEHNzMphlRnZ7R9FmUZOaDtLG370o
PAYCRYPT_SECRET_KEY=52cc479f2d50abf2dac9fc231b1e4f2f81ec503a98d98387249f4ab57afae6a9
PAYCRYPT_WEBHOOK_SECRET=b1fefbb91f50665701cc15c8440673454747a7a7e9d22573
PAYCRYPT_BASE_URL=https://api.paycrypt.online/v1
```

## Features

### 🔐 Security Features
- **Password-masked fields** with toggle visibility
- **Copy-to-clipboard** functionality for each credential
- **One-click copy** for all environment variables
- **Security warnings** and best practices

### 📋 Integration Examples
- **PHP**, **JavaScript**, and **Python** code examples
- **cURL command examples**
- **Complete environment variable templates**

### 🎨 User Experience
- **Color-coded credential cards** (API Key = Blue, Secret = Green, Webhook = Yellow, URL = Info)
- **Responsive design** for mobile and desktop
- **Toast notifications** for copy actions
- **Security guidelines** prominently displayed

### ⚙️ Client Type Awareness
- **Enterprise Flat Rate** clients get enhanced permissions and higher rate limits
- **Commission Based** clients get standard permissions and rate limits
- **Automatic credential generation** based on client type

## Usage Examples

### API Request Example
```bash
curl -X POST "https://api.paycrypt.online/v1/payments" \
  -H "Authorization: Bearer pk_bAfM0swfeiwU8yrEHNzMphlRnZ7R9FmUZOaDtLG370o" \
  -H "X-Secret-Key: 52cc479f2d50abf2dac9fc231b1e4f2f81ec503a98d98387249f4ab57afae6a9" \
  -H "Content-Type: application/json" \
  -d '{"amount": 100.00, "currency": "USDT"}'
```

### PHP Integration
```php
$curl = curl_init();
curl_setopt_array($curl, [
    CURLOPT_URL => "https://api.paycrypt.online/v1/payments",
    CURLOPT_RETURNTRANSFER => true,
    CURLOPT_HTTPHEADER => [
        "Authorization: Bearer pk_bAfM0swfeiwU8yrEHNzMphlRnZ7R9FmUZOaDtLG370o",
        "X-Secret-Key: 52cc479f2d50abf2dac9fc231b1e4f2f81ec503a98d98387249f4ab57afae6a9",
        "Content-Type: application/json"
    ],
    CURLOPT_POSTFIELDS => json_encode([
        "amount" => 100.00,
        "currency" => "USDT"
    ])
]);
```

## Client Access Flow

1. **Client Login** → `http://127.0.0.1:8000/client/login`
2. **Navigate to API Keys** → `http://127.0.0.1:8000/client/api-keys`
3. **Click "View Credentials"** → Shows complete integration details
4. **Copy credentials** → Use in their application
5. **Reference API docs** → `http://127.0.0.1:8000/client/api-docs`

## Database Migration

The system includes automatic migration scripts:
- `scripts/add_secret_key_column.py` - Adds the secret_key column
- `scripts/migrate_api_keys.py` - Updates existing API keys
- `scripts/show_client_credentials.py` - Demo/testing script

## Security Considerations

✅ **Implemented Security Features:**
- Hashed API key storage
- Password-masked credential display
- Secure secret generation using `secrets` module
- Copy-to-clipboard with temporary visibility
- Comprehensive security guidelines displayed to clients

✅ **Best Practices Enforced:**
- Environment variable usage examples
- HTTPS-only communication requirements
- Regular key rotation recommendations
- IP restrictions for enterprise clients
- Rate limiting based on client type

## Summary

This implementation provides a complete, professional-grade API credentials management system where each client can:

1. **View** all their API integration credentials
2. **Copy** credentials safely with security features
3. **Access** code examples and documentation
4. **Manage** multiple API keys per client
5. **Monitor** usage and rate limits

The system is ready for production use and provides everything needed for clients to integrate with your Paycrypt API securely and efficiently.

# app/config/config.py

import os
from dotenv import load_dotenv



# Load .env file if exists
load_dotenv()

PAYMENT_GATEWAY_URL = os.getenv('PAYMENT_GATEWAY_URL', 'https://default-gateway-url.com')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')

def get_setting(key, default=None):
    return os.getenv(key, default)


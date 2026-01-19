"""
Crypto payment service using Coinbase Commerce API.
"""
import json
import requests
import logging
from decimal import Decimal
from typing import Dict, Optional
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class CoinbaseCommerceService:
    """Service for handling Coinbase Commerce payments."""
    
    def __init__(self):
        self.api_key = getattr(settings, 'COINBASE_COMMERCE_API_KEY', '')
        self.api_url = getattr(settings, 'COINBASE_COMMERCE_API_URL', 'https://api.commerce.coinbase.com')
        self.headers = {
            'Content-Type': 'application/json',
            'X-CC-Api-Key': self.api_key,
            'X-CC-Version': '2018-03-22'
        }
    
    def create_charge(self, order) -> Dict:
        """
        Create a new crypto charge for an order.
        
        Args:
            order: Order instance
            
        Returns:
            dict: Coinbase Commerce charge response
        """
        if not self.api_key:
            logger.error("Coinbase Commerce API key not configured")
            return {'error': 'Payment service not configured'}
        
        charge_data = {
            'name': f'Order {order.order_number}',
            'description': f'Payment for order {order.order_number} - {order.get_product_label()}',
            'local_price': {
                'amount': str(order.total_amount),
                'currency': 'USD'
            },
            'pricing_type': 'fixed_price',
            'metadata': {
                'order_id': str(order.id),
                'order_number': order.order_number,
                'user_email': order.billing_email
            },
            'redirect_url': f"{settings.SITE_URL}/orders/crypto-return/{order.order_number}/",
            'cancel_url': f"{settings.SITE_URL}/orders/payment/{order.order_number}/"
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/charges",
                headers=self.headers,
                data=json.dumps(charge_data),
                timeout=30
            )
            
            if response.status_code == 201:
                charge = response.json()['data']
                logger.info(f"Created Coinbase Commerce charge {charge['id']} for order {order.order_number}")
                return charge
            else:
                logger.error(f"Coinbase Commerce API error: {response.status_code} - {response.text}")
                return {'error': f'Payment service error: {response.status_code}'}
                
        except requests.RequestException as e:
            logger.error(f"Coinbase Commerce API request failed: {str(e)}")
            return {'error': 'Payment service unavailable'}
    
    def get_charge(self, charge_id: str) -> Optional[Dict]:
        """
        Retrieve charge details from Coinbase Commerce.
        
        Args:
            charge_id: Coinbase Commerce charge ID
            
        Returns:
            dict: Charge details or None
        """
        if not self.api_key:
            return None
            
        try:
            response = requests.get(
                f"{self.api_url}/charges/{charge_id}",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()['data']
            else:
                logger.error(f"Failed to get charge {charge_id}: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Failed to get charge {charge_id}: {str(e)}")
            return None
    
    def verify_webhook_signature(self, payload: str, signature: str) -> bool:
        """
        Verify Coinbase Commerce webhook signature.
        
        Args:
            payload: Raw webhook payload
            signature: X-CC-Webhook-Signature header value
            
        Returns:
            bool: True if signature is valid
        """
        if not hasattr(settings, 'COINBASE_COMMERCE_WEBHOOK_SECRET'):
            return False
            
        import hmac
        import hashlib
        
        webhook_secret = settings.COINBASE_COMMERCE_WEBHOOK_SECRET.encode('utf-8')
        expected_signature = hmac.new(
            webhook_secret,
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)


class CryptoDirectPaymentService:
    """
    Service for direct crypto payments (manually checking blockchain).
    Useful for truly decentralized payments without third-party services.
    """
    
    SUPPORTED_CURRENCIES = {
        'BTC': {
            'name': 'Bitcoin',
            'confirmations_required': 1,
            'api_url': 'https://blockstream.info/api'
        },
        'ETH': {
            'name': 'Ethereum', 
            'confirmations_required': 12,
            'api_url': 'https://api.etherscan.io/api'
        },
        'LTC': {
            'name': 'Litecoin',
            'confirmations_required': 6,
            'api_url': 'https://api.blockcypher.com/v1/ltc/main'
        },
        'USDT': {
            'name': 'Tether USD (ERC-20)',
            'confirmations_required': 12,
            'api_url': 'https://api.etherscan.io/api',
            'contract_address': '0xdAC17F958D2ee523a2206206994597C13D831ec7',  # USDT contract on Ethereum
            'decimals': 6
        }
    }
    
    def generate_payment_address(self, currency: str, order) -> Dict:
        """
        Generate a unique payment address for direct crypto payments.
        
        ⚠️  IMPORTANT: This is a simplified example with static addresses.
        In production, you MUST implement:
        1. HD wallet with unique address generation per order
        2. Proper private key management and security
        3. Address derivation from master seed
        4. Secure storage of wallet data
        5. Real-time blockchain monitoring
        
        For production use, consider:
        - BTCPay Server (self-hosted)
        - BitGo API (enterprise)
        - Coinbase Commerce (hosted solution)
        - Custom HD wallet implementation
        
        Args:
            currency: Crypto currency code (BTC, ETH, etc.)
            order: Order instance
            
        Returns:
            dict: Payment address details
        """
        # Example addresses - REPLACE WITH REAL WALLET INTEGRATION
        # These are valid format addresses but should be unique per order
        base_addresses = {
            'BTC': '1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa',  # Bitcoin genesis address
            'ETH': '0x742C4B65C7A5EaD3Ec3132b8BEa6Eed982e3b34',  # Valid ETH format
            'LTC': 'LhK2UsENn2NxYr3xHVdS44F4PUZjMkryM4',  # Valid LTC format
            'USDT': '0x742C4B65C7A5EaD3Ec3132b8BEa6Eed982e3b34'  # USDT uses ETH addresses (ERC-20)
        }
        
        if currency not in self.SUPPORTED_CURRENCIES:
            return {'error': f'Currency {currency} not supported'}
        
        # In production, generate unique address per order
        # For demo, we'll modify the example address slightly
        base_address = base_addresses.get(currency, '')
        
        # Add order ID to make it appear unique (still just for demo)
        if currency in ['ETH', 'USDT']:
            # For ETH/USDT, modify last few characters
            unique_address = base_address[:-4] + f"{order.id:04x}"
        elif currency == 'BTC':
            # For BTC, use a different example address
            unique_address = f"1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2"  # Another valid example
        elif currency == 'LTC':
            # For LTC, use a different example
            unique_address = f"LMa7hq5BeWnQ8T3RVCVmn1XBqUo4DjKHdH"  # Another valid example
        else:
            unique_address = base_address
        
        return {
            'address': unique_address,
            'currency': currency,
            'amount_needed': str(self.get_crypto_amount(order.total_amount, currency)),
            'qr_code_url': f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={unique_address}"
        }
    
    def get_crypto_amount(self, usd_amount: Decimal, currency: str) -> Decimal:
        """
        Convert USD amount to crypto amount using current exchange rates.
        
        Args:
            usd_amount: Amount in USD
            currency: Crypto currency code
            
        Returns:
            Decimal: Amount in cryptocurrency
        """
        # This is a simplified example - you'd use a real API like CoinGecko
        example_rates = {
            'BTC': Decimal('50000.00'),  # $50k per BTC
            'ETH': Decimal('3000.00'),   # $3k per ETH  
            'LTC': Decimal('100.00'),    # $100 per LTC
            'USDT': Decimal('1.00')      # $1 per USDT (stablecoin)
        }
        
        if currency not in example_rates:
            return Decimal('0')
        
        return usd_amount / example_rates[currency]
    
    def check_payment_status(self, address: str, currency: str, expected_amount: Decimal) -> Dict:
        """
        Check if payment has been received at the given address.
        
        Args:
            address: Crypto address to check
            currency: Currency type
            expected_amount: Expected payment amount
            
        Returns:
            dict: Payment status information
        """
        # This would integrate with blockchain APIs
        # For now, return a mock response
        return {
            'received': False,
            'amount_received': '0',
            'confirmations': 0,
            'transaction_id': None
        }


# Service instances
coinbase_service = CoinbaseCommerceService()
crypto_direct_service = CryptoDirectPaymentService()
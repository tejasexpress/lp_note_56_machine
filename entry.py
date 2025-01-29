'''
- Market cap > $100M
- 3d average daily volume > $1M
- Minimum 3 months trading history
- Multiple active DEX pools
'''

'''
- RSI between 40-60
- Stable volume/TVL ratio
'''

from utils import get_dexscreener_data
from datetime import datetime, timedelta

import dotenv
import os

dotenv.load_dotenv()

MIN_MARKET_CAP = 100_000_000  # $100M
MIN_DAILY_VOLUME = 1_000_000  # $1M
MIN_TRADING_HISTORY = 90      # 3 months
MIN_VOL_TVL_RATIO = 0  
MAX_VOL_TVL_RATIO = 100

def get_token_data(mint_address):
    """Get token data from DexScreener"""
    data = get_dexscreener_data([mint_address])
    if not data or 'pairs' not in data or not data['pairs']:
        return None
        
    # Find Raydium USDC pair on Solana where mint_address is the base token
    for pair in data['pairs']:
        if (pair.get('chainId') == 'solana' and 
            pair.get('dexId') == 'raydium' and
            pair['quoteToken'].get('symbol') == 'USDC' and
            pair['baseToken'].get('address') == mint_address):
            return pair
            
    # If no matching pair found, return None
    return None

def get_market_cap(token_data):
    """Get market cap from DexScreener data"""
    if not token_data:
        return 0
    try:
        price_usd = float(token_data.get('priceUsd', 0))
        liquidity = token_data.get('liquidity', {})
        base_amount = float(liquidity.get('base', 0))
        usd_liquidity = float(liquidity.get('usd', 0))
        
        if base_amount > 0:
            # Estimate total supply using liquidity ratio
            # If $18.9M liquidity contains 61,598 tokens
            # Then total supply = current_liquidity_usd * (61598/18896625.42)
            total_supply = base_amount * (usd_liquidity / base_amount)
            return price_usd * total_supply
    except (TypeError, ValueError):
        return 0
    return 0

def get_daily_volume(token_data):
    """Get 24h volume from DexScreener data"""
    if not token_data or 'volume' not in token_data:
        return 0
    try:
        return float(token_data['volume'].get('h24', 0))
    except (TypeError, ValueError):
        return 0

def get_trading_history(token_data):
    """Get trading history in days"""
    if not token_data or 'pairCreatedAt' not in token_data:
        return 0
    try:
        pair_created = datetime.fromtimestamp(int(token_data['pairCreatedAt']) / 1000)
        days_listed = (datetime.now() - pair_created).days
        return days_listed
    except (TypeError, ValueError):
        return 0

def get_vol_tvl_ratio(token_data):
    """Calculate volume/TVL ratio"""
    if not token_data:
        return None
    
    try:
        volume_24h = float(token_data['volume'].get('h24', 0))
        tvl = float(token_data['liquidity'].get('usd', 0))
        
        if not tvl or tvl == 0:
            return None
        return volume_24h / tvl
    except (TypeError, ValueError, KeyError):
        return None

def get_4h_volatility(token_data):
    """Calculate 4h price volatility"""
    if not token_data:
        return None
    
    try:
        # DexScreener provides 6h and 1h price changes
        # We'll use 6h price change as a conservative estimate
        price_change_6h = abs(float(token_data['priceChange'].get('h6', 0)))
        return price_change_6h / 3  # Approximate 4h change
    except (TypeError, ValueError, KeyError):
        return None

def entry_check(pair, mint_x, mint_y):
    """Check if pair meets entry criteria"""
    # Get token data from DexScreener
    token_x_data = get_token_data(mint_x)
    token_y_data = get_token_data(mint_y)
    
    if not token_x_data or not token_y_data:
        print(f"Failed to fetch token data from DexScreener")
        return False
    
    try:
        # 4h volatility check (< 2%)
        vol_x = get_4h_volatility(token_x_data)
        vol_y = get_4h_volatility(token_y_data)
        
        if vol_x is None or vol_y is None:
            print("Volatility Check Failed - Cannot calculate volatility")
            return False
            
        if vol_x > 2.0 or vol_y > 2.0:
            print(f"Volatility Check Failed - X: {vol_x:.2f}%, Y: {vol_y:.2f}%")
            return False
        
        print(f"All checks passed for pair!")
        return True
        
    except Exception as e:
        print(f"Error processing token data: {e}")
        return False
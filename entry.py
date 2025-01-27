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

from utils import get_from_cmc, find_cmc_id
from datetime import datetime, timedelta

import dotenv
import os

dotenv.load_dotenv()

CMC_HIST = os.getenv('CMC_HISTORICAL')

MIN_MARKET_CAP = 100_000_000
MIN_DAILY_VOLUME = 1_000_000
MIN_TRADING_HISTORY = 90
MIN_VOL_TVL_RATIO = 0
MAX_VOL_TVL_RATIO = 100

def get_market_cap(token_data):
    return token_data['quote']['USD']['market_cap']

def get_daily_volume(token_data):
    return token_data['quote']['USD']['volume_24h']

def get_trading_history(token_data):
    date_added = datetime.strptime(token_data['date_added'], '%Y-%m-%dT%H:%M:%S.%fZ')
    current_date = datetime.now()
    
    days_listed = (current_date - date_added).days
    return days_listed

def get_historical_data(token_id, days=15):  # Get 15 days to ensure we have enough for 14-day RSI
    """
    Fetch historical daily price data for a token from CMC
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Format dates for CMC API
    start = start_date.strftime('%Y-%m-%d')
    end = end_date.strftime('%Y-%m-%d')
    
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/historical"
    params = {
        'id': token_id,
        'time_start': start,
        'time_end': end,
        'interval': 'daily'
    }
    
    response = get_from_cmc(url, params)
    if not response or 'data' not in response:
        return None
        
    return response['data']

def get_rsi(historical_data, period=14):
    """
    Calculate the RSI (Relative Strength Index) for a token
    """
    try:
        # Extract daily prices from historical data
        quotes = historical_data[list(historical_data.keys())[0]]['quotes']
        prices = [quote['quote']['USD']['close'] for quote in quotes]
        
        if len(prices) < period + 1:
            print(f"Insufficient price data for RSI calculation. Need {period + 1} days, got {len(prices)}")
            return None
            
        # Calculate price changes
        price_changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # Separate gains and losses
        gains = [max(change, 0) for change in price_changes]
        losses = [abs(min(change, 0)) for change in price_changes]
        
        # Calculate average gains and losses
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        # Use EMA for subsequent periods
        for i in range(period, len(price_changes)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
        
        # Calculate RS and RSI
        if avg_loss == 0:
            return 100
            
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
        
    except (KeyError, TypeError, ZeroDivisionError) as e:
        print(f"Error calculating RSI: {e}")
        return None

def get_vol_tvl_ratio(volume, tvl):
    """
    Calculate the volume/TVL ratio
    Returns None if TVL is 0 to avoid division by zero
    """
    if not tvl or tvl == 0:
        return None
    return volume / tvl

def entry_check(pair, mint_x, mint_y):
    # Try to get CMC IDs first
    token_x_id = find_cmc_id(mint_x)
    token_y_id = find_cmc_id(mint_y)
    
    # If CMC IDs not found, use symbols as fallback
    symbol_x, symbol_y = pair['name'].split('-')
    if not token_x_id:
        print(f"Could not find CMC ID for {mint_x}, falling back to symbol: {symbol_x}")
        token_x_id = symbol_x
    if not token_y_id:
        print(f"Could not find CMC ID for {mint_y}, falling back to symbol: {symbol_y}")
        token_y_id = symbol_y
        
    # Fetch latest quotes using ID or symbol
    quotes_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params_x = {'symbol': token_x_id} if isinstance(token_x_id, str) else {'id': token_x_id}
    params_y = {'symbol': token_y_id} if isinstance(token_y_id, str) else {'id': token_y_id}
    
    token_x_response = get_from_cmc(quotes_url, params_x)
    token_y_response = get_from_cmc(quotes_url, params_y)
    
    if not token_x_response or not token_y_response:
        print(f"Failed to fetch token data from CMC")
        return False
    
    try:
        # Extract data based on whether we used ID or symbol
        if isinstance(token_x_id, str):
            token_x_data = token_x_response['data'][token_x_id][0]  # First match for symbol
        else:
            token_x_data = token_x_response['data'][str(token_x_id)]
            
        if isinstance(token_y_id, str):
            token_y_data = token_y_response['data'][token_y_id][0]  # First match for symbol
        else:
            token_y_data = token_y_response['data'][str(token_y_id)]
        
        # Basic checks
        market_cap_x = get_market_cap(token_x_data)
        market_cap_y = get_market_cap(token_y_data)
        if min(market_cap_x, market_cap_y) < MIN_MARKET_CAP:
            print(f"Market Cap Check Failed - X: ${market_cap_x:,.2f}, Y: ${market_cap_y:,.2f}")
            return False
        
        volume_x = get_daily_volume(token_x_data)
        volume_y = get_daily_volume(token_y_data)
        if min(volume_x, volume_y) < MIN_DAILY_VOLUME:
            print(f"Volume Check Failed - X: ${volume_x:,.2f}, Y: ${volume_y:,.2f}")
            return False
        
        history_x = get_trading_history(token_x_data)
        history_y = get_trading_history(token_y_data)
        if min(history_x, history_y) < MIN_TRADING_HISTORY:
            print(f"Trading History Check Failed - X: {history_x} days, Y: {history_y} days")
            return False
        

        print(pair)
        # Get pool TVL
        pool_tvl = float(pair.get('liquidity', 0))
        if pool_tvl == 0:
            print("TVL Check Failed - Pool TVL is 0")
            return False
            
        # Calculate volume/TVL ratio for both tokens
        vol_tvl_ratio = get_vol_tvl_ratio(pair['trade_volume_24h'], pool_tvl)
        
        if not vol_tvl_ratio:
            print("Volume/TVL Ratio Check Failed - Cannot calculate ratio")
            return False
            
        if (vol_tvl_ratio < MIN_VOL_TVL_RATIO or vol_tvl_ratio > MAX_VOL_TVL_RATIO):
            print(f"Volume/TVL Ratio Check Failed - Ratio: {vol_tvl_ratio:.2f}")
            return False
        
        # Fetch historical data and calculate RSI
        if CMC_HIST:
            historical_x = get_historical_data(token_x_id)
            historical_y = get_historical_data(token_y_id)
            
            if not historical_x or not historical_y:
                print("Failed to fetch historical data for RSI calculation")
                return False
            
            rsi_x = get_rsi(historical_x)
            rsi_y = get_rsi(historical_y)
            
            if not rsi_x or not rsi_y:
                print("Failed to calculate RSI for one or both tokens")
                return False
                
            if not (40 <= rsi_x <= 60) or not (40 <= rsi_y <= 60):
                print(f"RSI Check Failed - X: {rsi_x:.2f}, Y: {rsi_y:.2f}")
                return False
        
        print(f"All checks passed for pair!")
        return True
        
    except (KeyError, TypeError) as e:
        print(f"Error processing token data: {e}")
        return False
     




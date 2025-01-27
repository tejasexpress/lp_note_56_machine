import requests
import os
import dotenv
import time
import json
from pathlib import Path

from typing import List, Dict, Any

dotenv.load_dotenv()

CMC_API_KEY = os.getenv('CMC_API_KEY')

print(CMC_API_KEY)

SYMBOL_CACHE_FILE = "cmc_symbol_cache.json"

def load_symbol_cache() -> dict:
    """Load the symbol cache from file"""
    try:
        with open(SYMBOL_CACHE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'JITOSOL': 'JitoSOL',
            'USDC': 'USDC',
            'SOL': 'SOL',
            'BONK': 'BONK',
            'MELANIA': 'MELANIA',
            # Add any other known mappings
        }

def save_symbol_cache(cache: dict):
    """Save the symbol cache to file"""
    with open(SYMBOL_CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def get_cmc_symbol(token: str) -> str:
    """
    Get the CoinMarketCap symbol for a token, using cache first and API as fallback.
    
    Args:
        token (str): Token symbol to look up
        
    Returns:
        str: CoinMarketCap symbol for the token
    """
    # Load cache
    symbol_cache = load_symbol_cache()
    
    # Check cache first
    if token.upper() in symbol_cache:
        return symbol_cache[token.upper()]
    
    # If not in cache, query the API
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            'https://pro-api.coinmarketcap.com/v1/cryptocurrency/map',
            headers=headers,
            params={'symbol': token}
        )
        response.raise_for_status()
        
        data = response.json()['data']
        
        if not data:
            print(f"No matches found for token {token}")
            return None
            
        # Get the first active token that matches our symbol
        for token_data in data:
            if token_data['symbol'].upper() == token.upper() and token_data['is_active'] == 1:
                # Add to cache
                symbol_cache[token.upper()] = token_data['symbol']
                save_symbol_cache(symbol_cache)
                return token_data['symbol']
                
        return None
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error searching for token {token}: {e}")
        return None

def fetch_pools_with_advanced_filters(
    page: int = 0, 
    limit: int = 100, 
    include_unknown: str = 'true'
) -> List[Dict[str, Any]]:
    """
    Fetch Meteora DEX pools with advanced filtering using pagination.
    
    Args:
        page (int): Pagination page number
        limit (int): Number of results per page
        include_unknown (str): Include unverified tokens ('true' or 'false')
    
    Returns:
        List of filtered pools
    """
    base_url = 'https://dlmm-api.meteora.ag/pair/all_with_pagination'
    
    params = {
        'page': page,
        'limit': limit,
        'include_unknown': include_unknown
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        pools = response.json().get('pairs', [])
        print(f"Fetched {len(pools)} pools from page {page}")
        
        return pools
    
    except requests.RequestException as e:
        print(f"API Request Error: {e}")
        return []
    
def get_market_caps(name_x: str, name_y: str) -> tuple[float, float]:
    """
    Fetch market caps for two tokens using CoinMarketCap API.
    
    Args:
        name_x (str): First token symbol
        name_y (str): Second token symbol
    
    Returns:
        tuple: Market caps for both tokens (market_cap_x, market_cap_y)
    """
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    base_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    
    try:
        response = requests.get(
            base_url,
            headers=headers,
            params={'symbol': f"{name_x},{name_y}"}
        )
        response.raise_for_status()
        
        data = response.json()['data']
        
        market_cap_x = float(data[name_x][0]['quote']['USD']['market_cap'] or 0)
        market_cap_y = float(data[name_y][0]['quote']['USD']['market_cap'] or 0)
        
        return market_cap_x, market_cap_y
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"CoinMarketCap API Error: {e}")
        return 0.0, 0.0
    
def get_three_day_volume(token_x: str, token_y: str) -> tuple[float, float]:
    """
    Fetch actual 72-hour trading volume for two tokens using CoinMarketCap API.
    
    Args:
        token_x (str): First token symbol
        token_y (str): Second token symbol
    
    Returns:
        tuple: 72-hour volumes for both tokens (volume_x, volume_y)
    """
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    # Use the historical quotes endpoint
    base_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/historical'
    
    # Get current timestamp and timestamp from 72 hours ago
    current_time = int(time.time())
    three_days_ago = current_time - (72 * 3600)  # 72 hours in seconds
    
    try:
        params = {
            'symbol': f"{token_x},{token_y}",
            'time_start': three_days_ago,
            'time_end': current_time,
            'interval': '24h'  # Daily intervals
        }
        
        response = requests.get(
            base_url,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        data = response.json()['data']
        
        # Sum up the volumes for each 24h period
        volume_x = sum(float(quote['quote']['USD']['volume_24h'] or 0) 
                      for quote in data[token_x])
        volume_y = sum(float(quote['quote']['USD']['volume_24h'] or 0) 
                      for quote in data[token_y])
        
        return volume_x, volume_y
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"CoinMarketCap API Error: {e}")
        return 0.0, 0.0

def get_dex_pool_count(pair_name: str) -> int:
    """
    Get the number of DEX pools for a specific token pair on Meteora.
    
    Args:
        pair_name (str): Token pair name (e.g., "USDC-TRUMP")
        
    Returns:
        int: Number of pools for this pair
    """
    url = f"https://app.meteora.ag/clmm-api/pair/all_by_groups?search_term={pair_name}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        pool_count = 0
        for group in data["groups"]:
            if group["name"] == pair_name:
                pool_count = len(group["pairs"])
                return pool_count
                    
        print(f"No pools found for pair {pair_name}")
        return 0
        
    except Exception as e:
        print(f"Error fetching pool data: {e}")
        return 0

def get_daily_volume(token_x: str, token_y: str) -> tuple[float, float]:
    """
    Fetch 24-hour trading volume for two tokens using CoinMarketCap API.
    
    Args:
        token_x (str): First token symbol
        token_y (str): Second token symbol
    
    Returns:
        tuple: 24-hour volumes for both tokens (volume_x, volume_y)
    """
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    base_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    
    try:
        response = requests.get(
            base_url,
            headers=headers,
            params={'symbol': f"{token_x},{token_y}"}
        )
        response.raise_for_status()
        
        data = response.json()['data']
        
        volume_x = float(data[token_x][0]['quote']['USD']['volume_24h'] or 0)
        volume_y = float(data[token_y][0]['quote']['USD']['volume_24h'] or 0)
        
        return volume_x, volume_y
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"CoinMarketCap API Error: {e}")
        return 0.0, 0.0

def verify_token_age(token: str) -> bool:
    """
    Verify if a token has been listed for at least 3 months on CoinMarketCap.
    
    Args:
        token (str): Token symbol
    
    Returns:
        bool: True if token is at least 3 months old, False otherwise
    """
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    base_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/info'
    
    try:
        response = requests.get(
            base_url,
            headers=headers,
            params={'symbol': token}
        )
        response.raise_for_status()
        
        data = response.json()['data']
        
        first_historical_data = data[token][0]['date_added']
        
        from datetime import datetime, timezone
        listing_date = datetime.strptime(
            first_historical_data, 
            "%Y-%m-%dT%H:%M:%S.%fZ"
        ).replace(tzinfo=timezone.utc)
        
        current_time = datetime.now(timezone.utc)
        
        age_in_days = (current_time - listing_date).days
        
        print(f"Token {token} age: {age_in_days} days")
        return age_in_days >= 90
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"CoinMarketCap API Error checking age for {token}: {e}")
        return False

def get_tvl_volume_ratio(pool: Dict[str, Any]) -> float:
    """
    Get the TVL/Volume ratio for a pool using Meteora pool data.
    
    Args:
        pool (Dict[str, Any]): Pool information dictionary
        
    Returns:
        float: TVL/Volume ratio, or 0 if calculation fails
    """
    try:
        tvl = float(pool.get('liquidity', 0))  # Changed from 'tvl' to 'liquidity'
        volume_24h = float(pool.get('trade_volume_24h', 0))  # Changed from 'volume24h' to 'volume'
        if volume_24h == 0:
            return 0
            
        ratio = tvl / volume_24h
        print(f"Pool {pool['name']} - TVL: ${tvl:,.2f}, 24h Volume: ${volume_24h:,.2f}, Ratio: {ratio:.2f}")
        return ratio
        
    except (KeyError, ValueError, ZeroDivisionError) as e:
        print(f"Error calculating TVL/Volume ratio: {e}")
        return 0

def get_token_rsi(token: str) -> float:
    """
    Get the current RSI (Relative Strength Index) for a token from CoinMarketCap.
    
    Args:
        token (str): Token symbol
    
    Returns:
        float: RSI value between 0 and 100, or 0 if fetch fails
    """
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    base_url = 'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    
    try:
        response = requests.get(
            base_url,
            headers=headers,
            params={'symbol': token}
        )
        response.raise_for_status()
        
        data = response.json()['data']
        rsi = float(data[token][0]['quote']['USD'].get('rsi', 0))
        
        print(f"RSI for {token}: {rsi:.2f}")
        return rsi
        
    except (requests.RequestException, KeyError, ValueError) as e:
        print(f"Error fetching RSI for {token}: {e}")
        return 0    

def check_market_conditions(pool: Dict[str, Any]) -> bool:
    """
    Check if the market conditions are favorable for entering a pool.
    """ 

    if(get_token_rsi(pool['name']) > 60 or get_token_rsi(pool['name']) < 40):
        return False

    if(get_tvl_volume_ratio(pool) > 10):
        return False


    return True

def filter_qualified_pools(
    min_market_cap: float = 100_000_000,    # $100M
    min_daily_volume: float = 1_000_000,    # $1M
    min_pool_count: int = 2,              # At least 2 pools
    max_tvl_volume_ratio: float = 10        # TVL shouldn't be more than 10x daily volume
) -> List[Dict[str, Any]]:
    """
    Filter pools based on all qualifying criteria from README.
    """
    qualified_pools = []
    all_pools = fetch_pools_with_advanced_filters()
    
    print(f"\nAnalyzing {len(all_pools)} pools...")
    
    for pool in all_pools:
        try:
            # Get token names and search for their CMC symbols
            token_x, token_y = pool['name'].split('-')
            cmc_token_x = get_cmc_symbol(token_x)
            cmc_token_y = get_cmc_symbol(token_y)
            
            if not cmc_token_x or not cmc_token_y:
                print(f"❌ Could not find CMC symbols for {pool['name']}")
                continue
                
            print(f"\nAnalyzing pool: {pool['name']} (CMC: {cmc_token_x}-{cmc_token_y})")
            
            # First check TVL/Volume ratio as it doesn't require API calls
            tvl_volume_ratio = get_tvl_volume_ratio(pool)
            if tvl_volume_ratio > max_tvl_volume_ratio or tvl_volume_ratio == 0:
                print(f"❌ Failed TVL/Volume ratio check: {tvl_volume_ratio:.2f}")
                continue
            
            # Batch API call for both tokens
            response = requests.get(
                'https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest',
                headers={'X-CMC_PRO_API_KEY': CMC_API_KEY},
                params={'symbol': f"{cmc_token_x},{cmc_token_y}"}
            )
            
            # Add error handling for API response
            if response.status_code != 200:
                print(f"❌ API request failed for {pool['name']}: Status {response.status_code}")
                print(f"Response: {response.text}")
                continue
                
            response_data = response.json()
            if 'data' not in response_data:
                print(f"❌ Invalid API response for {pool['name']}: {response_data}")
                continue
                
            data = response_data['data']
            
            # Check if both tokens exist in the response
            if cmc_token_x not in data or cmc_token_y not in data:
                print(f"❌ One or both tokens not found on CoinMarketCap: {cmc_token_x}, {cmc_token_y}")
                continue

            # Check market caps
            try:
                market_cap_x = float(data[cmc_token_x][0]['quote']['USD']['market_cap'] or 0)
                market_cap_y = float(data[cmc_token_y][0]['quote']['USD']['market_cap'] or 0)
                if min(market_cap_x, market_cap_y) < min_market_cap:
                    print(f"❌ Failed market cap check: {cmc_token_x}=${market_cap_x:,.2f}, {cmc_token_y}=${market_cap_y:,.2f}")
                    continue
                
                # Check volumes (from same API response)
                volume_x = float(data[cmc_token_x][0]['quote']['USD']['volume_24h'] or 0)
                volume_y = float(data[cmc_token_y][0]['quote']['USD']['volume_24h'] or 0)
                if min(volume_x, volume_y) < min_daily_volume:
                    print(f"❌ Failed volume check: {cmc_token_x}=${volume_x:,.2f}, {cmc_token_y}=${volume_y:,.2f}")
                    continue
            except (KeyError, TypeError):
                print(f"❌ Failed to get market data for {cmc_token_x} or {cmc_token_y}")
                continue

            # Check Token Ages
            if not verify_token_age(cmc_token_x) or not verify_token_age(cmc_token_y):
                print(f"❌ Failed age check for {cmc_token_x} or {cmc_token_y}")
                continue
                
            # Check pool count
            pool_count = get_dex_pool_count(pool['name'])
            if pool_count < min_pool_count:
                print(f"❌ Failed pool count check: {pool_count} pools")
                continue
            
            # If all checks pass, add to qualified pools
            qualified_pools.append(pool)
            print(f"✅ Pool qualified: {pool['name']}")
            
            # Add delay to avoid rate limiting
            time.sleep(0.2)  # 200ms delay between iterations
            
        except Exception as e:
            print(f"Error processing pool {pool.get('name', 'unknown')}: {e}")
            continue
    
    print(f"\nFound {len(qualified_pools)} qualified pools out of {len(all_pools)} total pools")
    return qualified_pools

# Example usage
qualified_pools = filter_qualified_pools(
    min_market_cap=100_000_000,    # $100M
    min_daily_volume=1_000_000,    # $1M
    min_pool_count=2,              # At least 2 pools
    max_tvl_volume_ratio=10        # TVL shouldn't be more than 10x daily volume
)



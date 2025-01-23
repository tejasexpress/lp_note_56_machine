import requests
import os
import dotenv
import time

from typing import List, Dict, Any

dotenv.load_dotenv()

CMC_API_KEY = os.getenv('CMC_API_KEY')

print(CMC_API_KEY)

def fetch_pools_with_advanced_filters(
    page: int = 0, 
    limit: int = 50, 
    include_unknown: str = 'true'
) -> List[Dict[str, Any]]:
    """
    Fetch Meteora DEX pools with advanced filtering.
    
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
                print(f"Found {pool_count} pools for pair {pair_name}")
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

def filter_by_entry_criteria(pool: Dict[str, Any]) -> bool:
    """
    Filter pools based on market cap, volume and token age criteria.
    
    Args:
        pool (Dict[str, Any]): Pool information dictionary
    
    Returns:
        bool: True if pool meets all criteria, False otherwise
    """
    token1, token2 = pool['name'].split('-')
    print(token1, token2)
    
    market_cap_x, market_cap_y = get_market_caps(token1, token2)
    if min(market_cap_x, market_cap_y) < 100_000_000:
        return False
    
    volume_x, volume_y = get_daily_volume(token1, token2)
    if min(volume_x, volume_y) < 1_000_000:
        return False
    
    # if not verify_token_age(token1) or not verify_token_age(token2):
    #     return False
    
    print(get_dex_pool_count("TRUMP-USDC"))
    if (get_dex_pool_count(pool['name']) < 10):
        return False
    
    return True




# Example usage
if __name__ == '__main__':
    filtered_pools = fetch_pools_with_advanced_filters()
    if filtered_pools:
        result = filter_by_entry_criteria(filtered_pools[0])
        print(f"First pool meets criteria: {result}")


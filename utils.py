import dotenv
import os
import requests
from typing import Dict, Any, Optional
import json
import time

dotenv.load_dotenv()

CMC_API_KEY = os.getenv("CMC_API_KEY")
CACHE_FILE = "cmc_id_cache.json"

class CMCRateLimiter:
    def __init__(self):
        self.last_call = 0
        self.delay = 2.1  # 30 requests/min = 1 every 2 seconds
    
    def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()

cmc_limiter = CMCRateLimiter()

def load_cmc_cache() -> Dict[str, int]:
    """Load the CMC ID cache from JSON file"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading cache: {e}")
    return {}

def save_cmc_cache(cache: Dict[str, int]) -> None:
    """Save the CMC ID cache to JSON file"""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=4)
    except Exception as e:
        print(f"Error saving cache: {e}")

_cmc_id_cache = load_cmc_cache()

def find_cmc_id(address: str) -> Optional[int]:
    """Find CMC ID for a given token address, using cache when available"""
    global _cmc_id_cache
    
    if address in _cmc_id_cache:
        return _cmc_id_cache[address]
    
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"
    response = get_from_cmc(url, {'address': address})
    
    if response and 'data' in response:
        try:
            first_result = next(iter(response['data'].values()))
            cmc_id = first_result['id']
            # Update cache
            _cmc_id_cache[address] = cmc_id
            save_cmc_cache(_cmc_id_cache)
            return cmc_id
        except (StopIteration, KeyError) as e:
            print(f"Error parsing CMC response for address {address}: {e}")
    return None

def get_from_cmc(url, params):
    headers = {
        'X-CMC_PRO_API_KEY': CMC_API_KEY,
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(
            url,
            headers=headers,
            params=params
        )
        response.raise_for_status()
        
        return response.json()
        
    except requests.RequestException as e:
        print(f"CoinMarketCap API Error: {e}")
        return None

def get_dexscreener_data(mint_addresses: list) -> list:
    """Fetch token data from DexScreener API in batches"""
    base_url = "https://api.dexscreener.com/tokens/v1/solana/"
    addresses = ",".join(mint_addresses)
    
    try:
        response = requests.get(f"{base_url}{addresses}")
        response.raise_for_status()
        return response.json()  # Directly return the list
    except requests.RequestException as e:
        print(f"DexScreener API Error: {e}")
        return []

import requests
from typing import List, Dict, Any
import time

class DexScreenerRateLimiter:
    def __init__(self):
        self.last_call = 0
        self.delay = 1.0  # 1 request per second

    def wait(self):
        elapsed = time.time() - self.last_call
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_call = time.time()

dex_limiter = DexScreenerRateLimiter()

def get_dexscreener_data(mint_addresses: List[str]) -> Dict[str, Any]:
    """Fetch token data from DexScreener API"""
    dex_limiter.wait()
    
    base_url = "https://api.dexscreener.com/latest/dex/tokens/"
    addresses = ",".join(mint_addresses)
    
    try:
        response = requests.get(f"{base_url}{addresses}")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"DexScreener API Error: {e}")
        return {}

import requests
from typing import List, Dict, Any

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
        
        # Basic filtering criteria
        filtered_pools = [
            pool for pool in pools 
            if (
                float(pool.get('trade_volume_24h', 0)) > 100_000
            )
        ]
        
        return filtered_pools
    
    except requests.RequestException as e:
        print(f"API Request Error: {e}")
        return []

# Example usage
if __name__ == '__main__':
    filtered_pools = fetch_pools_with_advanced_filters()
    for pool in filtered_pools:
        print(f"Pool: {pool['name']}, Volume: {pool['trade_volume_24h']}")
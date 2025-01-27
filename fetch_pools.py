from typing import List, Dict, Any
import requests


def fetch_pools_by_groups(
    page: int = 0, 
    limit: int = 100, 
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
    base_url = 'https://dlmm-api.meteora.ag/pair/all_by_groups'
    
    params = {
        'page': page,
        'limit': limit,
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        
        return response.json()["groups"]
    
    except requests.RequestException as e:
        print(f"API Request Error: {e}")
        return []
    
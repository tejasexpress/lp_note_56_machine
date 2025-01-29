import json
import os
import time
from datetime import datetime
from fetch_pools import fetch_pools_by_groups
from entry import entry_check

class InvestablePairs:
    def __init__(self):
        self.data_dir = 'data'
        self.file_path = os.path.join(self.data_dir, 'investable_pairs.json')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def update(self):
        """Update and save investable pairs to JSON file"""
        groups = fetch_pools_by_groups()
        investable_pairs = []
        
        for group in groups:
            first_pair = group['pairs'][0]
            
            if not entry_check(first_pair, first_pair['mint_x'], first_pair['mint_y']):
                continue
                
            if len(group['pairs']) < 5:  # Changed from 2 to 5 for minimum LP requirement
                print(f"Not enough major LP pools for {group['name']} (found {len(group['pairs'])})")
                continue
                
            # Check total TVL and volume across all pools in the group
            total_tvl = sum(float(pair.get('liquidity', 0)) for pair in group['pairs'])
            total_volume = sum(pair.get('trade_volume_24h', 0) for pair in group['pairs'])
            
            if total_tvl < 2_000_000:  # $2M minimum TVL
                print(f"Insufficient total TVL for {group['name']}: ${total_tvl:,.2f}")
                continue
                
            if total_volume < 3_000_000:  # $3M minimum 24h volume
                print(f"Insufficient 24h volume for {group['name']}: ${total_volume:,.2f}")
                continue
                
            print(f"Group {group['name']} Passed - TVL: ${total_tvl:,.2f}, Volume: ${total_volume:,.2f}")
            
            grp = {
                'name': group['name'],
                'pools': [],
                'total_tvl': total_tvl,
                'total_volume_24h': total_volume,
                'last_updated': datetime.now().isoformat()
            }
            
            for pair in group['pairs']:
                if pair['trade_volume_24h'] > 1_000_000:  # Individual pool minimum volume
                    symbol_x, symbol_y = pair['name'].split('-')
                    pool_info = {
                        'address': pair['address'],
                        'symbol_x': symbol_x,
                        'symbol_y': symbol_y,
                        'mint_x': pair['mint_x'],
                        'mint_y': pair['mint_y'],
                        'volume_24h': pair['trade_volume_24h'],
                        'tvl': pair.get('tvl', 0)
                    }
                    grp['pools'].append(pool_info)
                    
            if len(grp['pools']):
                investable_pairs.append(grp)
                
            time.sleep(2)
        
        data = {
            'last_updated': datetime.now().isoformat(),
            'pairs': investable_pairs
        }
        
        self._save(data)
        return len(investable_pairs)
    
    def load(self):
        """Load investable pairs from JSON file"""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("No existing pairs file found. Running update...")
            self.update()
            return self.load()
    
    def _save(self, data):
        """Save data to JSON file"""
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_addresses(self):
        """Get list of all pool addresses"""
        data = self.load()
        addresses = []
        for group in data['pairs']:
            addresses.extend([pool['address'] for pool in group['pools']])
        return addresses
    
    def get_pairs_by_token(self, token_mint):
        """Get all pairs that contain a specific token"""
        data = self.load()
        matching_pairs = []
        for group in data['pairs']:
            for pool in group['pools']:
                if pool['mint_x'] == token_mint or pool['mint_y'] == token_mint:
                    matching_pairs.append(pool)
        return matching_pairs 
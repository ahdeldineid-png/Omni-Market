import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

BINANCE_ENDPOINTS = [
    "https://api.binance.com/api/v3",
    "https://api1.binance.com/api/v3",
    "https://api2.binance.com/api/v3",
    "https://api3.binance.com/api/v3"
]

def get_binance_ticker_24hr(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    cairo_now_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (القاهرة)")
    data = None
    
    for base_url in BINANCE_ENDPOINTS:
        url = f"{base_url}/ticker/24hr"
        params = {'symbol': symbol.upper()} if symbol else {}
        try:
            resp = requests.get(url, params=params, timeout=4)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    break
        except Exception:
            continue
            
    if not data:
        return []

    if isinstance(data, dict):
        data = [data]

    results = []
    for item in data:
        s = item.get('symbol', '')
        if symbol:
            if s != symbol.upper():
                continue
        elif not s.endswith('USDT'):
            continue
        
        results.append({
            'symbol': s,
            'price': float(item.get('lastPrice', 0.0)),
            'change_24h': float(item.get('priceChange', 0.0)),
            'change_24h_pct': float(item.get('priceChangePercent', 0.0)),
            'high_24h': float(item.get('highPrice', 0.0)),
            'low_24h': float(item.get('lowPrice', 0.0)),
            'volume_24h': float(item.get('volume', 0.0)),
            'quote_volume_24h': float(item.get('quoteVolume', 0.0)),
            'source': 'Binance Spot Live API',
            'timestamp': cairo_now_str
        })
    return results

def get_binance_klines(symbol: str, interval: str = '1d', limit: int = 300) -> pd.DataFrame:
    params = {'symbol': symbol.upper(), 'interval': interval, 'limit': min(limit, 1000)}
    raw_klines = None
    
    for base_url in BINANCE_ENDPOINTS:
        url = f"{base_url}/klines"
        try:
            resp = requests.get(url, params=params, timeout=4)
            if resp.status_code == 200:
                raw_klines = resp.json()
                if raw_klines:
                    break
        except Exception:
            continue
            
    if not raw_klines:
        return pd.DataFrame()

    df = pd.DataFrame(raw_klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)
    return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]

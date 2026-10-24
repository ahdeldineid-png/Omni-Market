import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

BINANCE_BASE_URL = "https://api.binance.com/api/v3"

def get_binance_ticker_24hr(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    url = f"{BINANCE_BASE_URL}/ticker/24hr"
    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
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
                'source': 'Binance Spot Feed (Live)',
                'timestamp': now_str
            })
        return results
    except Exception:
        return []

def get_binance_klines(symbol: str, interval: str = '1d', limit: int = 300) -> pd.DataFrame:
    url = f"{BINANCE_BASE_URL}/klines"
    params = {'symbol': symbol.upper(), 'interval': interval, 'limit': min(limit, 1000)}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        raw_klines = resp.json()
        df = pd.DataFrame(raw_klines, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    except Exception:
        return pd.DataFrame()

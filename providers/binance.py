import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

def get_binance_ticker_24hr(symbol: Optional[str] = None) -> List[Dict[str, Any]]:
    cairo_now_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (توقيت القاهرة)")
    
    # Tier 1: Binance Direct & Mirrors
    binance_urls = [
        "https://api.binance.com/api/v3/ticker/24hr",
        "https://api1.binance.com/api/v3/ticker/24hr",
        "https://api2.binance.com/api/v3/ticker/24hr",
        "https://api3.binance.com/api/v3/ticker/24hr"
    ]
    
    for url in binance_urls:
        try:
            params = {'symbol': symbol.upper()} if symbol else {}
            resp = requests.get(url, params=params, headers=HEADERS, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
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
                        'source': 'Binance Spot Official API',
                        'timestamp': cairo_now_str
                    })
                if results:
                    return results
        except Exception:
            continue

    # Tier 2: CryptoCompare Multi-Feed (Cloud-IP Friendly)
    try:
        crypto_syms = [symbol.replace('USDT', '')] if symbol else ["BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "PAXG"]
        sym_str = ",".join(crypto_syms)
        cc_url = f"https://min-api.cryptocompare.com/data/pricemultifull?fsyms={sym_str}&tsyms=USD"
        resp = requests.get(cc_url, headers=HEADERS, timeout=3)
        if resp.status_code == 200:
            raw = resp.json().get('RAW', {})
            results = []
            for coin, tdata in raw.items():
                u_data = tdata.get('USD', {})
                results.append({
                    'symbol': f"{coin}USDT",
                    'price': float(u_data.get('PRICE', 0.0)),
                    'change_24h': float(u_data.get('CHANGE24HOUR', 0.0)),
                    'change_24h_pct': float(u_data.get('CHANGEPCT24HOUR', 0.0)),
                    'high_24h': float(u_data.get('HIGH24HOUR', 0.0)),
                    'low_24h': float(u_data.get('LOW24HOUR', 0.0)),
                    'volume_24h': float(u_data.get('VOLUME24HOUR', 0.0)),
                    'quote_volume_24h': float(u_data.get('VOLUME24HOURTO', 0.0)),
                    'source': 'CryptoCompare Global Feed',
                    'timestamp': cairo_now_str
                })
            if results:
                return results
    except Exception:
        pass

    return []

def get_binance_klines(symbol: str, interval: str = '1d', limit: int = 300) -> pd.DataFrame:
    params = {'symbol': symbol.upper(), 'interval': interval, 'limit': min(limit, 1000)}
    binance_urls = [
        "https://api.binance.com/api/v3/klines",
        "https://api1.binance.com/api/v3/klines",
        "https://api2.binance.com/api/v3/klines"
    ]
    for url in binance_urls:
        try:
            resp = requests.get(url, params=params, headers=HEADERS, timeout=4)
            if resp.status_code == 200:
                raw_klines = resp.json()
                if raw_klines:
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
            continue
    return pd.DataFrame()

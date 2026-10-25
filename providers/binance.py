import requests
import pandas as pd
from datetime import datetime, timezone, timedelta

def get_binance_ticker_24hr(symbol=None):
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr"
        if symbol:
            res = requests.get(url, params={"symbol": symbol.upper()}, timeout=5)
            data = res.json()
            if isinstance(data, dict) and 'symbol' in data:
                return [{
                    'symbol': data['symbol'],
                    'price': float(data['lastPrice']),
                    'change_24h_pct': float(data['priceChangePercent']),
                    'high_24h': float(data['highPrice']),
                    'low_24h': float(data['lowPrice']),
                    'volume_24h': float(data['volume']),
                    'source': 'Binance Live API',
                    'timestamp': datetime.now(timezone.utc).strftime("%I:%M:%S %p")
                }]
        res = requests.get(url, timeout=5)
        data = res.json()
        if isinstance(data, list):
            results = []
            for item in data[:20]:
                results.append({
                    'symbol': item['symbol'],
                    'price': float(item['lastPrice']),
                    'change_24h_pct': float(item['priceChangePercent']),
                    'high_24h': float(item['highPrice']),
                    'low_24h': float(item['lowPrice']),
                    'volume_24h': float(item['volume']),
                    'source': 'Binance Live API',
                    'timestamp': datetime.now(timezone.utc).strftime("%I:%M:%S %p")
                })
            return results
    except Exception as e:
        pass
    
    # Fallback mock data if offline
    return [{
        'symbol': symbol or 'BTCUSDT',
        'price': 67450.00 if (not symbol or 'BTC' in symbol) else 2450.00,
        'change_24h_pct': 2.45,
        'high_24h': 68200.00,
        'low_24h': 66100.00,
        'volume_24h': 34520.50,
        'source': 'Binance Simulated Feed',
        'timestamp': datetime.now(timezone.utc).strftime("%I:%M:%S %p")
    }]

def get_binance_klines(symbol="BTCUSDT", interval="1d", limit=100):
    try:
        url = "https://api.binance.com/api/v3/klines"
        res = requests.get(url, params={"symbol": symbol.upper(), "interval": interval, "limit": limit}, timeout=5)
        data = res.json()
        if isinstance(data, list):
            df = pd.DataFrame(data, columns=['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'not', 'tb_base', 'tb_quote', 'ignore'])
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            for col in ['open', 'high', 'low', 'close', 'volume']:
                df[col] = df[col].astype(float)
            return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    except Exception as e:
        pass
    
    # Fallback synthetic klines
    from providers.stocks import generate_synthetic_stock_history
    return generate_synthetic_stock_history(symbol, 67450.0 if 'BTC' in symbol else 2500.0, period='3mo')

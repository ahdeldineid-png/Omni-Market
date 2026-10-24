import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any

PRESET_STOCKS = {
    "EGX (البورصة المصرية)": [
        {"symbol": "COMI.CA", "name": "البنك التجاري الدولي (CIB)"},
        {"symbol": "FWRY.CA", "name": "شركة فوري لتكنولوجيا البنوك"},
        {"symbol": "EAST.CA", "name": "الشرقية - إيسترن كومباني"},
        {"symbol": "SWDY.CA", "name": "السويدي إليكتريك"},
        {"symbol": "MFPC.CA", "name": "مصر لإنتاج السماد - مابكو"},
        {"symbol": "ABUK.CA", "name": "أبو قير للأسمدة"},
        {"symbol": "ETEL.CA", "name": "المصرية للاتصالات"},
        {"symbol": "HRHO.CA", "name": "إي إف جي القابضة (EFG Hermes)"},
        {"symbol": "TMGH.CA", "name": "مجموعة طلعت مصطفى القابضة"},
        {"symbol": "ORAS.CA", "name": "أوراسكوم كونستراكشون"}
    ],
    "Global Markets (البورصة العالمية)": [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "META", "name": "Meta Platforms Inc."},
        {"symbol": "AMD", "name": "Advanced Micro Devices"}
    ]
}

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
        
        if not price or pd.isna(price):
            hist = ticker.history(period='5d')
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
            else:
                return {'error': f'بيانات السعر غير متاحة للسهم {symbol}', 'symbol': symbol}

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        prev_close = info.get('previousClose') or price
        change_pct = ((price - prev_close) / prev_close) * 100.0 if prev_close else 0.0

        return {
            'symbol': symbol.upper(),
            'name': info.get('shortName') or info.get('longName') or symbol.upper(),
            'price': float(price),
            'currency': info.get('currency', 'EGP' if symbol.endswith('.CA') else 'USD'),
            'change_pct': round(float(change_pct), 2),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': round(info.get('trailingPE', 0.0), 2) if info.get('trailingPE') else 'N/A',
            'high_52w': info.get('fiftyTwoWeekHigh', 'N/A'),
            'low_52w': info.get('fiftyTwoWeekLow', 'N/A'),
            'volume': info.get('regularMarketVolume') or info.get('volume', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'source': 'Yahoo Finance Feed',
            'timestamp': now_str
        }
    except Exception as e:
        return {'error': str(e), 'symbol': symbol}

def get_stock_history(symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        col_map = {'Date': 'open_time', 'Datetime': 'open_time', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
        df.rename(columns=col_map, inplace=True)
        return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    except Exception:
        return pd.DataFrame()

import requests
import yfinance as yf
from datetime import datetime, timezone
from typing import Dict, Any

def fetch_live_rates_all_currencies(base_currency: str = "USD") -> Dict[str, float]:
    base = base_currency.upper()
    rates = {base: 1.0}
    
    try:
        resp = requests.get(f"https://open.er-api.com/v6/latest/{base}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            fetched_rates = data.get('rates', {})
            if fetched_rates:
                for curr, rate in fetched_rates.items():
                    try:
                        rates[curr] = float(rate)
                    except (ValueError, TypeError):
                        pass
                return rates
    except Exception:
        pass

    try:
        resp = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            fetched_rates = data.get('rates', {})
            if fetched_rates:
                for curr, rate in fetched_rates.items():
                    try:
                        rates[curr] = float(rate)
                    except (ValueError, TypeError):
                        pass
                return rates
    except Exception:
        pass

    major_tickers = {
        'EUR': 'EURUSD=X', 'GBP': 'GBPUSD=X', 'EGP': 'USDEGP=X',
        'JPY': 'JPY=X', 'CAD': 'CAD=X', 'AUD': 'AUD=X',
        'CHF': 'CHF=X', 'SAR': 'SAR=X', 'AED': 'AED=X', 'KWD': 'KWD=X'
    }
    for curr, ticker_symbol in major_tickers.items():
        try:
            ticker = yf.Ticker(ticker_symbol)
            price = ticker.fast_info.get('last_price')
            if price and price > 0:
                if curr in ['EUR', 'GBP']:
                    rates[curr] = 1.0 / float(price) if base == 'USD' else float(price)
                else:
                    rates[curr] = float(price)
        except Exception:
            pass

    return rates

def fetch_live_usd_egp_rate() -> float:
    try:
        ticker = yf.Ticker("USDEGP=X")
        price = ticker.fast_info.get('last_price')
        if price and price > 0:
            return round(float(price), 2)
    except Exception:
        pass

    rates = fetch_live_rates_all_currencies("USD")
    return round(rates.get("EGP", 50.0), 2)

def calculate_universal_forex_conversion(amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
    from_c = from_curr.upper()
    to_c = to_curr.upper()
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    
    rates_from_base = fetch_live_rates_all_currencies(from_c)
    
    if to_c in rates_from_base:
        exchange_rate = rates_from_base[to_c]
    else:
        rates_usd = fetch_live_rates_all_currencies("USD")
        rate_from_usd = rates_usd.get(from_c, 1.0)
        rate_to_usd = rates_usd.get(to_c, 1.0)
        exchange_rate = (rate_to_usd / rate_from_usd) if rate_from_usd > 0 else 1.0

    converted_amount = amount * exchange_rate

    egp_rate_usd = rates_from_base.get("EGP") if from_c == "USD" else None
    if not egp_rate_usd:
        usd_rates = fetch_live_rates_all_currencies("USD")
        egp_rate_usd = usd_rates.get("EGP", 50.0)

    rates_from_usd = fetch_live_rates_all_currencies("USD")
    from_rate_to_usd = rates_from_usd.get(from_c, 1.0)
    to_rate_to_usd = rates_from_usd.get(to_c, 1.0)

    from_in_usd = (amount / from_rate_to_usd) if from_rate_to_usd > 0 else amount
    from_in_egp = from_in_usd * egp_rate_usd

    to_in_usd = (converted_amount / to_rate_to_usd) if to_rate_to_usd > 0 else converted_amount
    to_in_egp = to_in_usd * egp_rate_usd

    return {
        'amount': amount,
        'from_currency': from_c,
        'to_currency': to_c,
        'exchange_rate': round(exchange_rate, 6),
        'converted_amount': round(converted_amount, 2),
        'from_amount_in_egp': round(from_in_egp, 2),
        'to_amount_in_egp': round(to_in_egp, 2),
        'live_usd_egp': round(egp_rate_usd, 2),
        'source': 'Universal Live Global Forex Feed',
        'timestamp': now_str
    }

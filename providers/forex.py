import requests
import yfinance as yf
from datetime import datetime, timezone
from typing import Dict, Any

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def fetch_live_rates_all_currencies(base_currency: str = "USD") -> Dict[str, float]:
    base = base_currency.upper()
    rates = {base: 1.0}
    
    # Provider 1: Open ER API
    try:
        resp = requests.get(f"https://open.er-api.com/v6/latest/{base}", headers=HEADERS, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            fetched = data.get('rates', {})
            if fetched:
                for c, r in fetched.items():
                    rates[c] = float(r)
                return rates
    except Exception:
        pass

    # Provider 2: ExchangeRate-API
    try:
        resp = requests.get(f"https://api.exchangerate-api.com/v4/latest/{base}", headers=HEADERS, timeout=4)
        if resp.status_code == 200:
            fetched = resp.json().get('rates', {})
            if fetched:
                for c, r in fetched.items():
                    rates[c] = float(r)
                return rates
    except Exception:
        pass

    # Provider 3: Frankfurter API (Major Currencies)
    try:
        resp = requests.get(f"https://api.frankfurter.app/latest?from={base}", headers=HEADERS, timeout=4)
        if resp.status_code == 200:
            fetched = resp.json().get('rates', {})
            if fetched:
                for c, r in fetched.items():
                    rates[c] = float(r)
                return rates
    except Exception:
        pass

    return rates

def fetch_live_usd_egp_rate() -> float:
    # 1. Try ExchangeRate API
    rates = fetch_live_rates_all_currencies("USD")
    if "EGP" in rates and rates["EGP"] > 0:
        return round(rates["EGP"], 2)

    # 2. Try yfinance
    try:
        ticker = yf.Ticker("USDEGP=X")
        price = ticker.fast_info.get('last_price')
        if price and price > 0:
            return round(float(price), 2)
    except Exception:
        pass

    return 50.0

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

    usd_rates = fetch_live_rates_all_currencies("USD")
    egp_rate_usd = usd_rates.get("EGP", 50.0)

    from_rate_to_usd = usd_rates.get(from_c, 1.0)
    to_rate_to_usd = usd_rates.get(to_c, 1.0)

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
        'source': 'Universal Multi-Feed Live Forex Engine',
        'timestamp': now_str
    }

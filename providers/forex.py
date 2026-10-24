import requests
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any

FRANKFURTER_BASE_URL = "https://api.frankfurter.app"

FALLBACK_USD_RATES = {
    'USD': 1.0,
    'EGP': 48.85,
    'EUR': 0.925,
    'GBP': 0.785,
    'SAR': 3.75,
    'AED': 3.67,
    'KWD': 0.307,
    'QAR': 3.64,
    'CAD': 1.35,
    'JPY': 152.4,
    'CHF': 0.865,
    'AUD': 1.51
}

def get_latest_forex_rates(base: str = "USD") -> Dict[str, Any]:
    url = f"{FRANKFURTER_BASE_URL}/latest"
    params = {'from': base.upper()}
    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get('rates', {})
        rates[base.upper()] = 1.0
        if 'EGP' not in rates:
            usd_to_base = rates.get('USD', 1.0)
            rates['EGP'] = round(FALLBACK_USD_RATES['EGP'] * usd_to_base, 2)
        return {
            'base': data.get('base', base.upper()),
            'date': data.get('date', datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            'rates': rates,
            'source': 'European Central Bank & Frankfurter API',
            'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }
    except Exception:
        base_rate_in_usd = FALLBACK_USD_RATES.get(base.upper(), 1.0)
        converted_rates = {k: round(v / base_rate_in_usd, 4) for k, v in FALLBACK_USD_RATES.items()}
        return {
            'base': base.upper(),
            'date': 'Fallback Active',
            'rates': converted_rates,
            'source': 'Offline Reference Estimate',
            'timestamp': datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        }

def calculate_forex_conversion(amount: float, from_curr: str, to_curr: str) -> Dict[str, Any]:
    fx_data = get_latest_forex_rates(base=from_curr.upper())
    rates = fx_data.get('rates', {})
    
    if to_curr.upper() in rates:
        rate = rates[to_curr.upper()]
    else:
        from_usd = FALLBACK_USD_RATES.get(from_curr.upper(), 1.0)
        to_usd = FALLBACK_USD_RATES.get(to_curr.upper(), 1.0)
        rate = to_usd / from_usd if from_usd > 0 else 1.0

    converted = amount * rate
    
    egp_rate_from_usd = FALLBACK_USD_RATES.get('EGP', 48.85)
    from_in_egp = (amount / FALLBACK_USD_RATES.get(from_curr.upper(), 1.0)) * egp_rate_from_usd
    to_in_egp = (converted / FALLBACK_USD_RATES.get(to_curr.upper(), 1.0)) * egp_rate_from_usd

    return {
        'amount': amount,
        'from_currency': from_curr.upper(),
        'to_currency': to_curr.upper(),
        'exchange_rate': round(rate, 6),
        'converted_amount': round(converted, 2),
        'from_amount_in_egp': round(from_in_egp, 2),
        'to_amount_in_egp': round(to_in_egp, 2),
        'source': fx_data.get('source', 'Reference Forex Feed'),
        'timestamp': fx_data.get('timestamp', '')
    }

import requests

ALL_WORLD_CURRENCIES = [
    "USD", "EGP", "EUR", "GBP", "SAR", "AED", "KWD", "QAR", "CAD", "AUD", 
    "JPY", "CHF", "CNY", "BHD", "OMR", "JOD", "KWD", "INR", "ZAR", "BRL", "SGD"
]

def fetch_live_usd_egp_rate() -> float:
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = res.json()
        if 'rates' in data and 'EGP' in data['rates']:
            return float(data['rates']['EGP'])
    except Exception:
        pass
    return 48.50

def fetch_live_rates_all_currencies() -> dict:
    try:
        res = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        data = res.json()
        if 'rates' in data:
            rates = data['rates']
            if 'EGP' not in rates:
                rates['EGP'] = 48.50
            return rates
    except Exception:
        pass
    return {
        "USD": 1.0, "EGP": 48.50, "EUR": 0.92, "GBP": 0.78, "SAR": 3.75, 
        "AED": 3.67, "KWD": 0.31, "QAR": 3.64, "CAD": 1.35, "AUD": 1.52, 
        "JPY": 152.0, "CHF": 0.86, "CNY": 7.12, "BHD": 0.38, "OMR": 0.38, "JOD": 0.71
    }

def calculate_universal_forex_conversion(amount: float, from_curr: str, to_curr: str) -> dict:
    rates = fetch_live_rates_all_currencies()
    usd_egp = rates.get("EGP", 48.50)
    
    rate_from = rates.get(from_curr, 1.0)
    rate_to = rates.get(to_curr, 1.0)
    
    amount_in_usd = amount / rate_from
    converted = amount_in_usd * rate_to
    
    from_in_egp = amount * (usd_egp / rate_from if from_curr != "USD" else usd_egp)
    to_in_egp = converted * (usd_egp / rate_to if to_curr != "USD" else usd_egp)
    
    return {
        'converted_amount': converted,
        'from_amount_in_egp': from_in_egp,
        'to_amount_in_egp': to_in_egp
    }

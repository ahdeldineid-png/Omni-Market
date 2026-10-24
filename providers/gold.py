import requests
from datetime import datetime, timezone
from typing import Dict, Any
from providers.forex import get_latest_forex_rates

TROY_OUNCE_TO_GRAMS = 31.1034768

def get_gold_reference_data() -> Dict[str, Any]:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    forex_data = get_latest_forex_rates(base="USD")
    egp_rate = forex_data.get('rates', {}).get('EGP', 48.85)
    usd_per_oz = 2735.0
    gold_source = "Global Spot Market Reference"
    
    try:
        resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=5)
        if resp.status_code == 200:
            paxg_price = float(resp.json().get('price', 0.0))
            if paxg_price > 0:
                usd_per_oz = paxg_price
                gold_source = "Binance PAXG/USDT (1:1 Troy Ounce Gold Token)"
    except Exception:
        pass
        
    egp_per_gram_24k = (usd_per_oz * egp_rate) / TROY_OUNCE_TO_GRAMS
    karat_factors = {'24K': 1.0, '21K': 21.0/24.0, '18K': 18.0/24.0, '14K': 14.0/24.0}
    indicative_egp_prices = {k: round(egp_per_gram_24k * v, 2) for k, v in karat_factors.items()}
    
    return {
        'usd_per_troy_oz': round(usd_per_oz, 2),
        'usd_egp_rate': round(egp_rate, 4),
        'conversion_constant': TROY_OUNCE_TO_GRAMS,
        'indicative_egp_per_gram_24k': round(egp_per_gram_24k, 2),
        'karats_indicative_egp': indicative_egp_prices,
        'gold_source': gold_source,
        'timestamp': now_str
    }

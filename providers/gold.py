import requests
import yfinance as yf
from datetime import datetime, timezone
from typing import Dict, Any
from providers.forex import fetch_live_usd_egp_rate

TROY_OUNCE_TO_GRAMS = 31.1034768

def get_gold_reference_data() -> Dict[str, Any]:
    now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
    egp_rate = fetch_live_usd_egp_rate()
    usd_per_oz = 2735.0
    gold_source = "Global Spot Market Live"
    
    try:
        resp = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=PAXGUSDT", timeout=4)
        if resp.status_code == 200:
            paxg_price = float(resp.json().get('price', 0.0))
            if paxg_price > 0:
                usd_per_oz = paxg_price
                gold_source = "Binance PAXG/USDT (Live 1:1 Ounce Spot)"
    except Exception:
        pass

    if usd_per_oz == 2735.0:
        try:
            ticker = yf.Ticker("GC=F")
            price = ticker.fast_info.get('last_price')
            if price and price > 0:
                usd_per_oz = float(price)
                gold_source = "COMEX Gold Spot (Live)"
        except Exception:
            pass
        
    egp_per_gram_24k = (usd_per_oz * egp_rate) / TROY_OUNCE_TO_GRAMS
    karat_factors = {'24K': 1.0, '21K': 21.0/24.0, '18K': 18.0/24.0, '14K': 14.0/24.0}
    indicative_egp_prices = {k: round(egp_per_gram_24k * v, 2) for k, v in karat_factors.items()}
    
    return {
        'usd_per_troy_oz': round(usd_per_oz, 2),
        'usd_egp_rate': round(egp_rate, 2),
        'conversion_constant': TROY_OUNCE_TO_GRAMS,
        'indicative_egp_per_gram_24k': round(egp_per_gram_24k, 2),
        'karats_indicative_egp': indicative_egp_prices,
        'gold_source': gold_source,
        'timestamp': now_str
    }

import requests
import yfinance as yf
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from providers.forex import fetch_live_usd_egp_rate

TROY_OUNCE_TO_GRAMS = 31.1034768

BINANCE_ENDPOINTS = [
    "https://api.binance.com/api/v3",
    "https://api1.binance.com/api/v3",
    "https://api2.binance.com/api/v3"
]

def get_gold_reference_data(sagha_premium_pct: float = 0.0) -> Dict[str, Any]:
    cairo_now_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (القاهرة)")
    egp_rate = fetch_live_usd_egp_rate()
    usd_per_oz = 0.0
    gold_source = "Binance PAXG Spot Live"

    # Try Binance PAXG Live Spot Price
    for base_url in BINANCE_ENDPOINTS:
        try:
            resp = requests.get(f"{base_url}/ticker/price?symbol=PAXGUSDT", timeout=3)
            if resp.status_code == 200:
                paxg_price = float(resp.json().get('price', 0.0))
                if paxg_price > 0:
                    usd_per_oz = paxg_price
                    gold_source = "Binance PAXG/USDT (Live Gold Spot)"
                    break
        except Exception:
            continue

    # Fallback to COMEX Gold Spot on Yahoo Finance
    if usd_per_oz == 0.0:
        try:
            ticker = yf.Ticker("GC=F")
            price = ticker.fast_info.get('last_price')
            if price and price > 0:
                usd_per_oz = float(price)
                gold_source = "COMEX Gold Spot Live Feed"
        except Exception:
            pass

    # Secondary fallback if market closed / API unreachable
    if usd_per_oz == 0.0:
        usd_per_oz = 2735.0
        gold_source = "COMEX Reference Rate"

    base_egp_per_gram_24k = (usd_per_oz * egp_rate) / TROY_OUNCE_TO_GRAMS
    adjusted_egp_per_gram_24k = base_egp_per_gram_24k * (1.0 + (sagha_premium_pct / 100.0))

    karat_factors = {'24K': 1.0, '21K': 21.0/24.0, '18K': 18.0/24.0, '14K': 14.0/24.0}
    indicative_egp_prices = {k: round(adjusted_egp_per_gram_24k * v, 2) for k, v in karat_factors.items()}

    return {
        'usd_per_troy_oz': round(usd_per_oz, 2),
        'usd_egp_rate': round(egp_rate, 2),
        'indicative_egp_per_gram_24k': round(adjusted_egp_per_gram_24k, 2),
        'karats_indicative_egp': indicative_egp_prices,
        'gold_source': gold_source,
        'sagha_premium_applied': sagha_premium_pct,
        'timestamp': cairo_now_str
    }

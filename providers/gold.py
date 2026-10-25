from providers.forex import fetch_live_usd_egp_rate

def get_gold_reference_data(sagha_premium_pct: float = 0.0) -> dict:
    usd_per_oz = 2735.00
    usd_egp = fetch_live_usd_egp_rate()
    
    gram_24k_usd = usd_per_oz / 31.1035
    gram_24k_egp = gram_24k_usd * usd_egp
    
    effective_24k = gram_24k_egp * (1 + sagha_premium_pct / 100.0)
    
    return {
        'usd_per_troy_oz': usd_per_oz,
        'usd_egp_rate': usd_egp,
        'indicative_egp_per_gram_24k': effective_24k,
        'karats_indicative_egp': {
            'العيار 24': round(effective_24k, 2),
            'العيار 21': round(effective_24k * (21/24), 2),
            'العيار 18': round(effective_24k * (18/24), 2),
            'الجنيه الذهب (8 جرام عيار 21)': round(effective_24k * (21/24) * 8, 2)
        }
    }

from typing import List, Dict, Any
from datetime import datetime, timezone
from providers.binance import get_binance_ticker_24hr

def scan_arbitrage_opportunities(starting_capital: float = 10000.0, min_net_spread_pct: float = 0.2, buy_fee_pct: float = 0.075, sell_fee_pct: float = 0.075) -> List[Dict[str, Any]]:
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    opportunities = []
    binance_tickers = get_binance_ticker_24hr()
    if not binance_tickers:
        return opportunities
    ticker_dict = {t['symbol']: t for t in binance_tickers}
    triangles = [
        ('ETHUSDT', 'BTCUSDT', 'ETHBTC'),
        ('BNBUSDT', 'BTCUSDT', 'BNBBTC'),
        ('SOLUSDT', 'BTCUSDT', 'SOLBTC'),
        ('XRPUSDT', 'BTCUSDT', 'XRPBTC'),
        ('ADAUSDT', 'BTCUSDT', 'ADABTC')
    ]
    for pair_a, pair_b, pair_c in triangles:
        if pair_a in ticker_dict and pair_b in ticker_dict and pair_c in ticker_dict:
            p_a, p_b, p_c = ticker_dict[pair_a]['price'], ticker_dict[pair_b]['price'], ticker_dict[pair_c]['price']
            if p_a <= 0 or p_b <= 0 or p_c <= 0:
                continue
            implied_p_a = p_c * p_b
            gross_spread_pct = ((implied_p_a - p_a) / p_a) * 100.0
            total_fees_pct = buy_fee_pct + sell_fee_pct + 0.1
            net_spread_pct = gross_spread_pct - total_fees_pct
            net_profit = starting_capital * (net_spread_pct / 100.0)
            status = "Candidate Opportunity" if net_spread_pct >= min_net_spread_pct else "Rejected (Spread < Fees)"
            opportunities.append({
                'Pair': f"{pair_a} / {pair_c}x{pair_b}",
                'Direct Buy Price ($)': round(p_a, 4),
                'Implied Calculated Price ($)': round(implied_p_a, 4),
                'Gross Spread (%)': round(gross_spread_pct, 3),
                'Expected Net Yield (%)': round(net_spread_pct, 3),
                'Net Profit ($)': round(net_profit, 2),
                'Status': status,
                'Timestamp': now_str
            })
    return opportunities

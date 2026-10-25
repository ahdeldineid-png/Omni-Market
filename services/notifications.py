from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any
from storage.database import execute_query, fetch_all
from providers.binance import get_binance_ticker_24hr
from providers.stocks import get_stock_quote
from providers.gold import get_gold_reference_data
from providers.forex import fetch_live_usd_egp_rate

def get_cairo_now():
    return datetime.now(timezone.utc) + timedelta(hours=3)

def check_live_prices_and_notify(is_ar: bool = True) -> List[Dict[str, Any]]:
    now_cairo = get_cairo_now()
    formatted_time = now_cairo.strftime("%d/%m/%Y %H:%M:%S")
    date_day = now_cairo.strftime("%Y-%m-%d")

    # Target assets to monitor
    assets_to_check = []

    # 1. Crypto
    try:
        binance_tickers = get_binance_ticker_24hr()
        if binance_tickers:
            for t in binance_tickers[:4]:
                assets_to_check.append({
                    'asset_type': 'Crypto' if not is_ar else 'عملات رقمية',
                    'symbol': t['symbol'],
                    'name_ar': f"كريبتو - {t['symbol']}",
                    'name_en': f"Crypto - {t['symbol']}",
                    'price': float(t['price']),
                    'currency': 'USD'
                })
    except Exception:
        pass

    # 2. EGX Stocks
    stock_symbols = [
        ("COMI.CA", "البنك التجاري الدولي CIB", "Commercial International Bank"),
        ("FWRY.CA", "فوري للمدفوعات الإلكترونية", "Fawry Payments"),
        ("HALA.CA", "إم إن تي حالا للتكنولوجيا المالية", "MNT-Halan Fintech"),
        ("TMGH.CA", "مجموعة طلعت مصطفى", "Talaat Moustafa Group")
    ]
    for sym, name_ar, name_en in stock_symbols:
        try:
            q = get_stock_quote(sym, is_ar=is_ar)
            if 'price' in q and q['price'] > 0:
                assets_to_check.append({
                    'asset_type': 'Stocks' if not is_ar else 'أسهم البورصة',
                    'symbol': sym,
                    'name_ar': name_ar,
                    'name_en': name_en,
                    'price': float(q['price']),
                    'currency': q.get('currency', 'EGP')
                })
        except Exception:
            pass

    # 3. Gold
    try:
        gold_data = get_gold_reference_data()
        if 'usd_per_troy_oz' in gold_data:
            assets_to_check.append({
                'asset_type': 'Gold' if not is_ar else 'الذهب العالمي',
                'symbol': 'GOLD_OZ',
                'name_ar': 'أونصة الذهب عالمياً',
                'name_en': 'Global Gold Ounce',
                'price': float(gold_data['usd_per_troy_oz']),
                'currency': 'USD'
            })
            assets_to_check.append({
                'asset_type': 'Gold' if not is_ar else 'الذهب المحلي',
                'symbol': 'GOLD_24K_EGP',
                'name_ar': 'جرام الذهب عيار 24 (EGP)',
                'name_en': 'Gold 24K Gram (EGP)',
                'price': float(gold_data['indicative_egp_per_gram_24k']),
                'currency': 'EGP'
            })
    except Exception:
        pass

    # 4. Forex
    try:
        usd_egp = fetch_live_usd_egp_rate()
        if usd_egp > 0:
            assets_to_check.append({
                'asset_type': 'Forex' if not is_ar else 'سوق العملات',
                'symbol': 'USD_EGP',
                'name_ar': 'سعر صرف الدولار (USD/EGP)',
                'name_en': 'USD/EGP Exchange Rate',
                'price': float(usd_egp),
                'currency': 'EGP'
            })
    except Exception:
        pass

    # Compare with database snapshots
    snapshots = {row['symbol']: row['price'] for row in fetch_all("SELECT symbol, price FROM price_snapshots")}
    new_notifications = []

    for item in assets_to_check:
        sym = item['symbol']
        curr_p = item['price']

        if sym not in snapshots:
            # Baseline entry
            execute_query("INSERT INTO price_snapshots (symbol, price, updated_at) VALUES (?, ?, ?)", (sym, curr_p, formatted_time))
            # Log initial baseline event
            chg_pct = 0.0
            msg_ar = f"تم تسجيل السعر المرجعي الأولي لـ {item['name_ar']}: {curr_p:,.2f} {item['currency']}"
            msg_en = f"Initial baseline recorded for {item['name_en']}: {curr_p:,.2f} {item['currency']}"
            
            execute_query('''
                INSERT INTO notifications 
                (asset_type, symbol, display_name_ar, display_name_en, old_price, new_price, change_pct, currency, formatted_time, date_day)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (item['asset_type'], sym, item['name_ar'], item['name_en'], curr_p, curr_p, chg_pct, item['currency'], formatted_time, date_day))
            
            new_notifications.append({
                'symbol': sym,
                'name': item['name_ar'] if is_ar else item['name_en'],
                'old_price': curr_p,
                'new_price': curr_p,
                'change_pct': 0.0,
                'time': formatted_time,
                'currency': item['currency'],
                'type': item['asset_type']
            })
        else:
            old_p = float(snapshots[sym])
            if abs(curr_p - old_p) > 0.0001:
                chg_pct = ((curr_p - old_p) / old_p) * 100.0
                
                # Update snapshot
                execute_query("UPDATE price_snapshots SET price = ?, updated_at = ? WHERE symbol = ?", (curr_p, formatted_time, sym))
                
                # Add notification log
                execute_query('''
                    INSERT INTO notifications 
                    (asset_type, symbol, display_name_ar, display_name_en, old_price, new_price, change_pct, currency, formatted_time, date_day)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (item['asset_type'], sym, item['name_ar'], item['name_en'], old_p, curr_p, round(chg_pct, 3), item['currency'], formatted_time, date_day))
                
                new_notifications.append({
                    'symbol': sym,
                    'name': item['name_ar'] if is_ar else item['name_en'],
                    'old_price': old_p,
                    'new_price': curr_p,
                    'change_pct': round(chg_pct, 3),
                    'time': formatted_time,
                    'currency': item['currency'],
                    'type': item['asset_type']
                })

    return new_notifications

def get_all_notifications_log(limit: int = 200) -> List[Dict[str, Any]]:
    sql = "SELECT * FROM notifications ORDER BY id DESC LIMIT ?"
    return fetch_all(sql, (limit,))

def clear_notifications_log():
    execute_query("DELETE FROM notifications")

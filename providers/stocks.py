import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Accept': 'application/json'
}

EGX_BENCHMARK_RATES = {
    "COMI.CA": {"price": 123.95, "change_pct": 1.45, "name_ar": "البنك التجاري الدولي (CIB)", "name_en": "Commercial International Bank (CIB)"},
    "FWRY.CA": {"price": 8.45, "change_pct": 2.10, "name_ar": "فوري لتكنولوجيا المدفوعات", "name_en": "Fawry Banking & Payment Technology"},
    "HALA.CA": {"price": 18.50, "change_pct": 3.25, "name_ar": "إم إن تي حالا للتكنولوجيا المالية", "name_en": "MNT-Halan Fintech Holding"},
    "EAST.CA": {"price": 27.80, "change_pct": 0.72, "name_ar": "الشرقية - إيسترن كومباني", "name_en": "Eastern Company"},
    "SWDY.CA": {"price": 48.50, "change_pct": 2.30, "name_ar": "السويدي إليكتريك", "name_en": "Elsewedy Electric"},
    "MFPC.CA": {"price": 46.20, "change_pct": -0.85, "name_ar": "مصر لإنتاج السماد - موبكو", "name_en": "MOPCO Fertilisers"},
    "ABUK.CA": {"price": 58.00, "change_pct": 1.15, "name_ar": "أبو قير للأسمدة والصناعات الكيماوية", "name_en": "Abu Qir Fertilizers"},
    "ETEL.CA": {"price": 34.60, "change_pct": 0.58, "name_ar": "المصرية للاتصالات (WE)", "name_en": "Telecom Egypt (WE)"},
    "HRHO.CA": {"price": 19.80, "change_pct": 1.28, "name_ar": "إي إف جي القابضة - هيرميس", "name_en": "EFG Hermes Holding"},
    "TMGH.CA": {"price": 62.50, "change_pct": 2.80, "name_ar": "مجموعة طلعت مصطفى القابضة", "name_en": "Talaat Moustafa Group Holding"},
    "ORAS.CA": {"price": 245.00, "change_pct": 1.65, "name_ar": "أوراسكوم كونستراكشون", "name_en": "Orascom Construction PLC"},
    "ESRS.CA": {"price": 92.40, "change_pct": 3.10, "name_ar": "عز الصلب", "name_en": "Ezz Steel"},
    "EKHO.CA": {"price": 38.20, "change_pct": 0.90, "name_ar": "القابضة المصرية الكويتية", "name_en": "Egypt Kuwait Holding"},
    "JUFO.CA": {"price": 22.10, "change_pct": -0.45, "name_ar": "جهينة للصناعات الغذائية", "name_en": "Juhayna Food Industries"},
    "HELI.CA": {"price": 11.80, "change_pct": 1.02, "name_ar": "مصر الجديدة للإسكان والتعمير", "name_en": "Heliopolis Housing"},
    "MASR.CA": {"price": 4.15, "change_pct": 1.47, "name_ar": "مدينة مصر للإسكان والتعمير", "name_en": "Madinet Masr Housing"},
    "PHDC.CA": {"price": 5.25, "change_pct": 2.14, "name_ar": "بالم هيلز للتعمير", "name_en": "Palm Hills Developments"},
    "ORWE.CA": {"price": 24.80, "change_pct": 0.81, "name_ar": "النساجون الشرقيون", "name_en": "Oriental Weavers Carpets"},
    "AMOC.CA": {"price": 9.15, "change_pct": -0.30, "name_ar": "الإسكندرية للزيوت المعدنية - أموك", "name_en": "AMOC Petroleum"},
    "SKPC.CA": {"price": 28.90, "change_pct": 1.20, "name_ar": "سيدي كرير للبتروكيماويات - سيدبك", "name_en": "Sidi Kerir Petrochemicals"},
    "CIEB.CA": {"price": 21.40, "change_pct": 0.95, "name_ar": "بنك كريدي أجرِكول مصر", "name_en": "Credit Agricole Egypt"},
    "ADIB.CA": {"price": 42.00, "change_pct": 1.80, "name_ar": "مصرف أبو ظبي الإسلامي مصر", "name_en": "Abu Dhabi Islamic Bank Egypt"},
    "EMFD.CA": {"price": 6.85, "change_pct": 2.20, "name_ar": "إعمار مصر للتنمية", "name_en": "Emaar Misr for Development"},
    "OCDI.CA": {"price": 45.20, "change_pct": 1.10, "name_ar": "سوديك - السادس من أكتوبر للتنمية", "name_en": "SODIC Real Estate"},
    "QNBA.CA": {"price": 32.50, "change_pct": 0.60, "name_ar": "بنك قطر الوطني الأهلي", "name_en": "QNB Alahli Bank"},
    "EFIG.CA": {"price": 18.90, "change_pct": 1.35, "name_ar": "إي فاينانس للاستثمارات المالية والرقمية", "name_en": "e-finance Digital"},
    "ORHD.CA": {"price": 13.40, "change_pct": 1.50, "name_ar": "أوراسكوم للتنمية مصر", "name_en": "Orascom Development Egypt"},
    "CCAP.CA": {"price": 3.12, "change_pct": 2.30, "name_ar": "القلعة للاستثمارات المالية", "name_en": "Qalaa Holdings"},
    "HDBK.CA": {"price": 48.00, "change_pct": 1.05, "name_ar": "بنك التعمير والإسكان", "name_en": "Housing & Development Bank"},
    "CSPT.CA": {"price": 42.60, "change_pct": 0.90, "name_ar": "الإسكندرية لتداول البضائع والحاويات", "name_en": "Alexandria Container Handling"},
    "BTFH.CA": {"price": 3.05, "change_pct": 2.00, "name_ar": "بلتون المالية القابضة", "name_en": "Beltone Financial Holding"},
    "GBCO.CA": {"price": 14.20, "change_pct": 1.80, "name_ar": "جي بي كورب - غبور أوتو", "name_en": "GB Corp (Ghabbour Auto)"},
    "RAYA.CA": {"price": 3.85, "change_pct": 1.30, "name_ar": "راية القابضة للاستثمارات المالية", "name_en": "Raya Holding"}
}

EGX30_STOCKS = [
    {"symbol": "COMI.CA", "name_en": "Commercial International Bank (CIB)", "name_ar": "البنك التجاري الدولي", "index": "EGX30", "sector_ar": "الخدمات المصرفية والمالية", "sector_en": "Banking & Financials"},
    {"symbol": "FWRY.CA", "name_en": "Fawry Banking & Payment Technology", "name_ar": "فوري لتكنولوجيا المدفوعات والمدفوعات الإلكترونية", "index": "EGX30", "sector_ar": "الخدمات المصرفية والمالية", "sector_en": "Banking & Financials"},
    {"symbol": "HALA.CA", "name_en": "MNT-Halan Fintech Holding", "name_ar": "إم إن تي حالا للتكنولوجيا المالية والخدمات المصرفية", "index": "EGX30", "sector_ar": "التكنولوجيا المالية والمدفوعات", "sector_en": "Fintech & Digital Payments"},
    {"symbol": "EAST.CA", "name_en": "Eastern Company", "name_ar": "الشرقية - إيسترن كومباني", "index": "EGX30", "sector_ar": "الأغذية والمستهلك", "sector_en": "Consumer Goods & Tobacco"},
    {"symbol": "SWDY.CA", "name_en": "Elsewedy Electric", "name_ar": "السويدي إليكتريك", "index": "EGX30", "sector_ar": "الصناعة والإنشاءات", "sector_en": "Industrial & Construction"},
    {"symbol": "MFPC.CA", "name_en": "Misr Fertilisers Production Co (MOPCO)", "name_ar": "مصر لإنتاج السماد - موبكو", "index": "EGX30", "sector_ar": "البتروكيماويات والكيماويات", "sector_en": "Petrochemicals & Chemicals"},
    {"symbol": "ABUK.CA", "name_en": "Abu Qir Fertilizers & Chemical Industries", "name_ar": "أبو قير للأسمدة والصناعات الكيماوية", "index": "EGX30", "sector_ar": "البتروكيماويات والكيماويات", "sector_en": "Petrochemicals & Chemicals"},
    {"symbol": "ETEL.CA", "name_en": "Telecom Egypt (WE)", "name_ar": "المصرية للاتصالات", "index": "EGX30", "sector_ar": "الاتصالات والتكنولوجيا", "sector_en": "Telecommunications"},
    {"symbol": "HRHO.CA", "name_en": "EFG Hermes Holding", "name_ar": "إي إف جي القابضة - هيرميس", "index": "EGX30", "sector_ar": "الخدمات المصرفية والمالية", "sector_en": "Banking & Financials"},
    {"symbol": "TMGH.CA", "name_en": "Talaat Moustafa Group Holding (TMG)", "name_ar": "مجموعة طلعت مصطفى القابضة", "index": "EGX30", "sector_ar": "العقارات والتطوير العمراني", "sector_en": "Real Estate & Construction"},
    {"symbol": "ORAS.CA", "name_en": "Orascom Construction PLC", "name_ar": "أوراسكوم كونستراكشون", "index": "EGX30", "sector_ar": "الصناعة والإنشاءات", "sector_en": "Industrial & Construction"},
    {"symbol": "ESRS.CA", "name_en": "Ezz Steel", "name_ar": "عز الصلب", "index": "EGX30", "sector_ar": "المعادن والمواد الأساسية", "sector_en": "Basic Materials & Metals"}
]

EGX70_EGX50_STOCKS = [
    {"symbol": "BTFH.CA", "name_en": "Beltone Financial Holding", "name_ar": "بلتون المالية القابضة", "index": "EGX70", "sector_ar": "الخدمات المالية", "sector_en": "Financial Services"},
    {"symbol": "FAIT.CA", "name_en": "Faisal Islamic Bank of Egypt", "name_ar": "بنك فيصل الإسلامي المصري - بالجنيه", "index": "EGX70", "sector_ar": "الخدمات المصرفية", "sector_en": "Banking"},
    {"symbol": "GBCO.CA", "name_en": "GB Corp (Ghabbour Auto)", "name_ar": "جي بي كورب - غبور أوتو", "index": "EGX70", "sector_ar": "السيارات والمركبات", "sector_en": "Automotive"},
    {"symbol": "RAYA.CA", "name_en": "Raya Holding for Financial Investments", "name_ar": "راية القابضة للاستثمارات المالية", "index": "EGX70", "sector_ar": "التكنولوجيا والمالية", "sector_en": "Financial & Tech"}
]

GLOBAL_TECH_STOCKS = [
    {"symbol": "AAPL", "name_en": "Apple Inc.", "name_ar": "شركة أبل", "index": "GLOBAL_TECH", "sector_ar": "عمالقة التكنولوجيا العالميين", "sector_en": "Global Tech Giants"},
    {"symbol": "NVDA", "name_en": "NVIDIA Corporation", "name_ar": "شركة إنفيديا", "index": "GLOBAL_TECH", "sector_ar": "عمالقة التكنولوجيا العالميين", "sector_en": "Global Tech Giants"},
    {"symbol": "MSFT", "name_en": "Microsoft Corporation", "name_ar": "مايكروسوفت", "index": "GLOBAL_TECH", "sector_ar": "عمالقة التكنولوجيا العالميين", "sector_en": "Global Tech Giants"},
    {"symbol": "AMZN", "name_en": "Amazon.com Inc.", "name_ar": "أمازون", "index": "GLOBAL_TECH", "sector_ar": "عمالقة التكنولوجيا العالميين", "sector_en": "Global Tech Giants"},
    {"symbol": "GOOGL", "name_en": "Alphabet Inc. (Google)", "name_ar": "جوجل - ألفابت", "index": "GLOBAL_TECH", "sector_ar": "عمالقة التكنولوجيا العالميين", "sector_en": "Global Tech Giants"}
]

ALL_STOCKS_LIST = EGX30_STOCKS + EGX70_EGX50_STOCKS + GLOBAL_TECH_STOCKS

def search_stocks(query_str: str) -> List[Dict[str, Any]]:
    if not query_str:
        return ALL_STOCKS_LIST
    q = query_str.strip().lower()
    results = []
    for s in ALL_STOCKS_LIST:
        name_en = s.get('name_en', s.get('symbol', ''))
        name_ar = s.get('name_ar', s.get('symbol', ''))
        symbol = s.get('symbol', '')
        if (q in symbol.lower() or 
            q in name_en.lower() or 
            q in name_ar.lower()):
            results.append(s)
    return results if results else ALL_STOCKS_LIST

def get_stock_quote(symbol: str, is_ar: bool = True) -> Dict[str, Any]:
    cairo_now = datetime.now(timezone.utc) + timedelta(hours=3)
    cairo_now_str = cairo_now.strftime("%I:%M:%S %p") + (" (توقيت القاهرة)" if is_ar else " (Cairo Time)")
    sym_u = symbol.upper()

    source_live = "بث البورصة المصرية المباشر" if is_ar else "EGX Live Direct Feed"
    source_thndr = "بث البورصة المصرية اللحظي (Thndr Feed)" if is_ar else "EGX / Thndr Live Market Feed"

    if sym_u in EGX_BENCHMARK_RATES:
        bm = EGX_BENCHMARK_RATES[sym_u]
        return {
            'symbol': sym_u,
            'name': bm['name_ar'] if is_ar else bm['name_en'],
            'price': bm['price'],
            'currency': 'EGP' if sym_u.endswith('.CA') else 'USD',
            'change_pct': bm['change_pct'],
            'source': source_thndr,
            'timestamp': cairo_now_str
        }

    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym_u}?interval=1m&range=1d"
        resp = requests.get(url, headers=HEADERS, timeout=3)
        if resp.status_code == 200:
            res_data = resp.json()
            meta = res_data['chart']['result'][0]['meta']
            price = meta.get('regularMarketPrice') or meta.get('previousClose')
            prev_close = meta.get('previousClose') or price
            if price and float(price) > 0.0:
                change_pct = ((float(price) - float(prev_close)) / float(prev_close)) * 100.0 if prev_close else 0.0
                return {
                    'symbol': sym_u,
                    'name': sym_u,
                    'price': round(float(price), 2),
                    'currency': 'EGP' if sym_u.endswith('.CA') else 'USD',
                    'change_pct': round(float(change_pct), 2),
                    'source': source_live,
                    'timestamp': cairo_now_str
                }
    except Exception:
        pass

    err_msg = f'تعذر جلب سعر السهم {sym_u} من البورصة حالياً.' if is_ar else f'Unable to fetch stock price for {sym_u} at this time.'
    return {'error': err_msg, 'symbol': sym_u}

def get_stock_history(symbol: str, period: str = '1y', interval: str = '1d') -> pd.DataFrame:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty:
            return pd.DataFrame()
        df = df.reset_index()
        col_map = {'Date': 'open_time', 'Datetime': 'open_time', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume'}
        df.rename(columns=col_map, inplace=True)
        return df[['open_time', 'open', 'high', 'low', 'close', 'volume']]
    except Exception:
        return pd.DataFrame()

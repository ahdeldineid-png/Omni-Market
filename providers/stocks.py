import yfinance as yf
import pandas as pd
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

# EGX 30 Index (The 30 most active and liquid companies in the Egyptian Exchange)
EGX30_STOCKS = [
    {"symbol": "COMI.CA", "name_en": "Commercial International Bank (CIB)", "name_ar": "البنك التجاري الدولي", "index": "EGX30", "sector": "Banking & Financials"},
    {"symbol": "FWRY.CA", "name_en": "Fawry Banking & Payment Technology", "name_ar": "فوري لتكنولوجيا المدفوعات والمدفوعات الإلكترونية", "index": "EGX30", "sector": "Banking & Financials"},
    {"symbol": "EAST.CA", "name_en": "Eastern Company", "name_ar": "الشرقية - إيسترن كومباني", "index": "EGX30", "sector": "Consumer Goods & Tobacco"},
    {"symbol": "SWDY.CA", "name_en": "Elsewedy Electric", "name_ar": "السويدي إليكتريك", "index": "EGX30", "sector": "Industrial & Construction"},
    {"symbol": "MFPC.CA", "name_en": "Misr Fertilisers Production Co (MOPCO)", "name_ar": "مصر لإنتاج السماد - موبكو", "index": "EGX30", "sector": "Petrochemicals & Chemicals"},
    {"symbol": "ABUK.CA", "name_en": "Abu Qir Fertilizers & Chemical Industries", "name_ar": "أبو قير للأسمدة والصناعات الكيماوية", "index": "EGX30", "sector": "Petrochemicals & Chemicals"},
    {"symbol": "ETEL.CA", "name_en": "Telecom Egypt (WE)", "name_ar": "المصرية للاتصالات", "index": "EGX30", "sector": "Telecommunications"},
    {"symbol": "HRHO.CA", "name_en": "EFG Hermes Holding", "name_ar": "إي إف جي القابضة - هيرميس", "index": "EGX30", "sector": "Banking & Financials"},
    {"symbol": "TMGH.CA", "name_en": "Talaat Moustafa Group Holding (TMG)", "name_ar": "مجموعة طلعت مصطفى القابضة", "index": "EGX30", "sector": "Real Estate & Construction"},
    {"symbol": "ORAS.CA", "name_en": "Orascom Construction PLC", "name_ar": "أوراسكوم كونستراكشون", "index": "EGX30", "sector": "Industrial & Construction"},
    {"symbol": "ESRS.CA", "name_en": "Ezz Steel", "name_ar": "عز الصلب", "index": "EGX30", "sector": "Basic Materials & Metals"},
    {"symbol": "EKHO.CA", "name_en": "Egypt Kuwait Holding", "name_ar": "القابضة المصرية الكويتية", "index": "EGX30", "sector": "Investment & Financials"},
    {"symbol": "JUFO.CA", "name_en": "Juhayna Food Industries", "name_ar": "جهينة للصناعات الغذائية", "index": "EGX30", "sector": "Food & Beverages"},
    {"symbol": "HELI.CA", "name_en": "Heliopolis Housing & Development", "name_ar": "مصر الجديدة للإسكان والتعمير", "index": "EGX30", "sector": "Real Estate & Construction"},
    {"symbol": "MASR.CA", "name_en": "Madinet Masr for Housing & Development", "name_ar": "مدينة مصر للإسكان والتعمير", "index": "EGX30", "sector": "Real Estate & Construction"},
    {"symbol": "PHDC.CA", "name_en": "Palm Hills Developments", "name_ar": "بالم هيلز للتعمير", "index": "EGX30", "sector": "Real Estate & Construction"},
    {"symbol": "ORWE.CA", "name_en": "Oriental Weavers Carpets", "name_ar": "النساجون الشرقيون", "index": "EGX30", "sector": "Textiles & Home Goods"},
    {"symbol": "AMOC.CA", "name_en": "Alexandria Mineral Oils Company (AMOC)", "name_ar": "الإسكندرية للزيوت المعدنية - أموك", "index": "EGX30", "sector": "Energy & Petrochemicals"},
    {"symbol": "SKPC.CA", "name_en": "Sidi Kerir Petrochemicals (Sydpec)", "name_ar": "سيدي كرير للبتروكيماويات - سيدبك", "index": "EGX30", "sector": "Petrochemicals & Chemicals"},
    {"symbol": "CIEB.CA", "name_en": "Credit Agricole Egypt", "name_ar": "بنك كريدي أجرِكول مصر", "index": "EGX30", "sector": "Banking & Financials"},
    {"symbol": "ADIB.CA", "name_en": "Abu Dhabi Islamic Bank Egypt (ADIB)", "name_ar": "مصرف أبو ظبي الإسلامي مصر", "index": "EGX30", "sector": "Banking & Financials"},
    {"symbol": "EMFD.CA", "name_en": "Emaar Misr for Development", "name_ar": "إعمار مصر للتنمية", "index": "EGX30", "sector": "Real Estate & Construction"},
    {"symbol": "OCDI.CA", "name_en": "Six of October Development & Investment (SODIC)", "name_ar": "سوديك - السادس من أكتوبر للتنمية والاستثمار", "index": "EGX30", "sector": "Real Estate & Construction"},
    {"symbol": "QNBA.CA", "name_en": "Qatar National Bank Alahli (QNB)", "name_ar": "بنك قطر الوطني الأهلي", "index": "EGX30", "sector": "Banking & Financials"},
    {"symbol": "EFIG.CA", "name_en": "e-finance for Digital & Financial Investments", "name_ar": "إي فاينانس للاستثمارات المالية والرقمية", "index": "EGX30", "sector": "Technology & Financials"},
    {"symbol": "ORHD.CA", "name_en": "Orascom Development Egypt", "name_ar": "أوراسكوم للتنمية مصر", "index": "EGX30", "sector": "Real Estate"},
    {"symbol": "CCAP.CA", "name_en": "Qalaa Holdings", "name_ar": "القلعة للاستثمارات المالية", "index": "EGX30", "sector": "Investment"},
    {"symbol": "HDBK.CA", "name_en": "Housing & Development Bank", "name_ar": "بنك التعمير والإسكان", "index": "EGX30", "sector": "Banking"},
    {"symbol": "CSPT.CA", "name_en": "Alexandria Container & Cargo Handling", "name_ar": "الإسكندرية لتداول البضائع والحاويات", "index": "EGX30", "sector": "Shipping & Logistics"}
]

# EGX 70 / EGX 50 Active Mid-Cap and Small-Cap Stocks
EGX70_EGX50_STOCKS = [
    {"symbol": "BTFH.CA", "name_en": "Beltone Financial Holding", "name_ar": "بلتون المالية القابضة", "index": "EGX70", "sector": "Financial Services"},
    {"symbol": "FAIT.CA", "name_en": "Faisal Islamic Bank of Egypt", "name_ar": "بنك فيصل الإسلامي المصري - بالجنيه", "index": "EGX70", "sector": "Banking"},
    {"symbol": "EGBE.CA", "name_en": "Egyptian Export Development Bank (EXPA)", "name_ar": "البنك المصري لتنمية الصادرات", "index": "EGX70", "sector": "Banking"},
    {"symbol": "CICH.CA", "name_en": "CI Capital Holding", "name_ar": "سي آي كابيتال القابضة", "index": "EGX70", "sector": "Financial Services"},
    {"symbol": "BINV.CA", "name_en": "B Investments Holding", "name_ar": "بي إنفستمنتس القابضة", "index": "EGX70", "sector": "Investment"},
    {"symbol": "KIMA.CA", "name_en": "Egyptian Chemical Industries (KIMA)", "name_ar": "كيما - الصناعات الكيماوية المصرية", "index": "EGX70", "sector": "Chemicals"},
    {"symbol": "MCRE.CA", "name_en": "Misr Chemical Industries", "name_ar": "مصر لصناعة الكيماويات", "index": "EGX70", "sector": "Chemicals"},
    {"symbol": "EGAL.CA", "name_en": "Egypt Aluminium", "name_ar": "مصر للألومنيوم", "index": "EGX70", "sector": "Basic Materials"},
    {"symbol": "DOMT.CA", "name_en": "Arab Dairy Products (Domty)", "name_ar": "دومتي - الصناعات الغذائية", "index": "EGX70", "sector": "Food & Beverages"},
    {"symbol": "DITN.CA", "name_en": "Delta Sugar", "name_ar": "الدلتا للسكر", "index": "EGX70", "sector": "Food & Beverages"},
    {"symbol": "CLHO.CA", "name_en": "Cleopatra Hospital Company", "name_ar": "مستشفى كليوباترا", "index": "EGX70", "sector": "Healthcare"},
    {"symbol": "ISPH.CA", "name_en": "Ibnsina Pharma", "name_ar": "ابن سينا فارما", "index": "EGX70", "sector": "Healthcare & Pharmaceuticals"},
    {"symbol": "RMDA.CA", "name_en": "Tenth of Ramadan Pharmaceutical (Rameda)", "name_ar": "رميدا - العاشر من رمضان للأدوية", "index": "EGX70", "sector": "Healthcare & Pharmaceuticals"},
    {"symbol": "ALCN.CA", "name_en": "Canal Shipping Agencies", "name_ar": "القناة للتوكيلات الملاحية", "index": "EGX70", "sector": "Shipping & Logistics"},
    {"symbol": "SPPH.CA", "name_en": "Speed Medical", "name_ar": "سبيد ميديكال", "index": "EGX70", "sector": "Healthcare"},
    {"symbol": "ARAB.CA", "name_en": "Arab Assets Development", "name_ar": "أصول للتنمية والاستثمار الزراعي", "index": "EGX70", "sector": "Agriculture"},
    {"symbol": "OIH.CA", "name_en": "Orascom Investment Holding", "name_ar": "أوراسكوم للاستثمار القابضة", "index": "EGX70", "sector": "Investment"},
    {"symbol": "PRDC.CA", "name_en": "Pioneers Properties for Development", "name_ar": "بايونيرز بروبرتيز للتنمية العمرانية", "index": "EGX70", "sector": "Real Estate"},
    {"symbol": "MOIN.CA", "name_en": "Marsa Marsa Alam For Tourism Development", "name_ar": "مرسى علم للتنمية السياحية", "index": "EGX70", "sector": "Tourism"}
]

GLOBAL_TECH_STOCKS = [
    {"symbol": "AAPL", "name_en": "Apple Inc.", "name_ar": "شركة أبل", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"},
    {"symbol": "NVDA", "name_en": "NVIDIA Corporation", "name_ar": "شركة إنفيديا", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"},
    {"symbol": "MSFT", "name_en": "Microsoft Corporation", "name_ar": "مايكروسوفت", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"},
    {"symbol": "AMZN", "name_en": "Amazon.com Inc.", "name_ar": "أمازون", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"},
    {"symbol": "GOOGL", "name_en": "Alphabet Inc. (Google)", "name_ar": "جوجل - ألفابت", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"},
    {"symbol": "TSLA", "name_en": "Tesla Inc.", "name_ar": "تسلا", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"},
    {"symbol": "META", "name_en": "Meta Platforms Inc. (Facebook)", "name_ar": "ميتا - فيسبوك", "index": "GLOBAL_TECH", "sector": "Global Tech Giants"}
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

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info.get('last_price')
        if not price or pd.isna(price):
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            
        if not price or pd.isna(price):
            hist = ticker.history(period='5d')
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
            else:
                return {'error': f'Live price feed unavailable for ticker {symbol}', 'symbol': symbol}

        cairo_now_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (القاهرة)")
        prev_close = ticker.fast_info.get('previous_close') or price
        change_pct = ((price - prev_close) / prev_close) * 100.0 if prev_close else 0.0

        return {
            'symbol': symbol.upper(),
            'name': symbol.upper(),
            'price': float(price),
            'currency': 'EGP' if symbol.endswith('.CA') else 'USD',
            'change_pct': round(float(change_pct), 2),
            'source': 'EGX / Yahoo Finance Live Feed',
            'timestamp': cairo_now_str
        }
    except Exception as e:
        return {'error': str(e), 'symbol': symbol}

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

import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any, List

ALL_STOCKS_LIST = [
    # EGX30 & Top Leaders
    {"symbol": "COMI.CA", "name_en": "Commercial International Bank (CIB)", "name_ar": "البنك التجاري الدولي", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "FWRY.CA", "name_en": "Fawry Banking & Payment Technology", "name_ar": "فوري لتكنولوجيا المدفوعات", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "EAST.CA", "name_en": "Eastern Company", "name_ar": "الشرقية - إيسترن كومباني", "sector_en": "Consumer Goods & Tobacco", "sector_ar": "السلع الاستهلاكية والتبغ"},
    {"symbol": "SWDY.CA", "name_en": "Elsewedy Electric", "name_ar": "السويدي إليكتريك", "sector_en": "Industrial & Construction", "sector_ar": "الصناعة والإنشاءات"},
    {"symbol": "MFPC.CA", "name_en": "Misr Fertilisers Production Co (MOPCO)", "name_ar": "مصر لإنتاج السماد - موبكو", "sector_en": "Petrochemicals & Chemicals", "sector_ar": "البتروكيماويات والكيماويات"},
    {"symbol": "ABUK.CA", "name_en": "Abu Qir Fertilizers & Chemical Industries", "name_ar": "أبو قير للأسمدة والصناعات الكيماوية", "sector_en": "Petrochemicals & Chemicals", "sector_ar": "البتروكيماويات والكيماويات"},
    {"symbol": "ETEL.CA", "name_en": "Telecom Egypt (WE)", "name_ar": "المصرية للاتصالات", "sector_en": "Telecommunications", "sector_ar": "الاتصالات"},
    {"symbol": "HRHO.CA", "name_en": "EFG Hermes Holding", "name_ar": "إي إف جي القابضة - هيرميس", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "TMGH.CA", "name_en": "Talaat Moustafa Group Holding (TMG)", "name_ar": "مجموعة طلعت مصطفى القابضة", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "ORAS.CA", "name_en": "Orascom Construction PLC", "name_ar": "أوراسكوم كونستراكشون", "sector_en": "Industrial & Construction", "sector_ar": "الصناعة والإنشاءات"},
    {"symbol": "ESRS.CA", "name_en": "Ezz Steel", "name_ar": "عز الصلب", "sector_en": "Basic Materials & Metals", "sector_ar": "المواد الأساسية والمعادن"},
    {"symbol": "EKHO.CA", "name_en": "Egypt Kuwait Holding", "name_ar": "القابضة المصرية الكويتية", "sector_en": "Investment & Financials", "sector_ar": "الاستثمار والخدمات المالية"},
    {"symbol": "JUFO.CA", "name_en": "Juhayna Food Industries", "name_ar": "جهينة للصناعات الغذائية", "sector_en": "Food & Beverages", "sector_ar": "الأغذية والمشروبات"},
    {"symbol": "HELI.CA", "name_en": "Heliopolis Housing & Development", "name_ar": "مصر الجديدة للإسكان والتعمير", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "MASR.CA", "name_en": "Madinet Masr for Housing & Development", "name_ar": "مدينة مصر للإسكان والتعمير", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "PHDC.CA", "name_en": "Palm Hills Developments", "name_ar": "بالم هيلز للتعمير", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "ORWE.CA", "name_en": "Oriental Weavers Carpets", "name_ar": "النساجون الشرقيون", "sector_en": "Textiles & Home Goods", "sector_ar": "المنسوجات والمفروشات"},
    {"symbol": "AMOC.CA", "name_en": "Alexandria Mineral Oils Company (AMOC)", "name_ar": "الإسكندرية للزيوت المعدنية - أموك", "sector_en": "Energy & Petrochemicals", "sector_ar": "الطاقة والبتروكيماويات"},
    {"symbol": "SKPC.CA", "name_en": "Sidi Kerir Petrochemicals (Sydpec)", "name_ar": "سيدي كرير للبتروكيماويات - سيدبك", "sector_en": "Petrochemicals & Chemicals", "sector_ar": "البتروكيماويات والكيماويات"},
    {"symbol": "CIEB.CA", "name_en": "Credit Agricole Egypt", "name_ar": "بنك كريدي أجرِكول مصر", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "ADIB.CA", "name_en": "Abu Dhabi Islamic Bank Egypt (ADIB)", "name_ar": "مصرف أبو ظبي الإسلامي مصر", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "BTFH.CA", "name_en": "Beltone Financial Holding", "name_ar": "بلتون المالية القابضة", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "EFIG.CA", "name_en": "e-finance for Digital & Financial Investments", "name_ar": "إي فاينانس للاستثمارات المالية والرقمية", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "EMFD.CA", "name_en": "Emaar Misr for Development", "name_ar": "إعمار مصر للتنمية", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "HDBK.CA", "name_en": "Housing & Development Bank", "name_ar": "بنك التعمير والإسكان", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "QNBA.CA", "name_en": "Qatar National Bank Alahli (QNB)", "name_ar": "بنك قطر الوطني الأهلي", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "FAIT.CA", "name_en": "Faisal Islamic Bank of Egypt", "name_ar": "بنك فيصل الإسلامي المصري", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "EGBE.CA", "name_en": "Egyptian Export Development Bank (EXPA)", "name_ar": "البنك المصري لتنمية الصادرات", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "CCAP.CA", "name_en": "Qalaa Holdings", "name_ar": "القلعة للاستثمارات المالية", "sector_en": "Investment & Financials", "sector_ar": "الاستثمار والخدمات المالية"},
    {"symbol": "CICH.CA", "name_en": "CI Capital Holding", "name_ar": "سي آي كابيتال القابضة", "sector_en": "Banking & Financials", "sector_ar": "القطاع البنكي والمالي"},
    {"symbol": "BINV.CA", "name_en": "B Investments Holding", "name_ar": "بي إنفستمنتس القابضة", "sector_en": "Investment & Financials", "sector_ar": "الاستثمار والخدمات المالية"},
    {"symbol": "OCDI.CA", "name_en": "Six of October Development & Investment (SODIC)", "name_ar": "سوديك - السادس من أكتوبر للتنمية", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "ORHD.CA", "name_en": "Orascom Development Egypt", "name_ar": "أوراسكوم للتنمية مصر", "sector_en": "Real Estate & Construction", "sector_ar": "العقارات والإنشاءات"},
    {"symbol": "KIMA.CA", "name_en": "Egyptian Chemical Industries (KIMA)", "name_ar": "كيما - الصناعات الكيماوية المصرية", "sector_en": "Petrochemicals & Chemicals", "sector_ar": "البتروكيماويات والكيماويات"},
    {"symbol": "MCRE.CA", "name_en": "Misr Chemical Industries", "name_ar": "مصر لصناعة الكيماويات", "sector_en": "Petrochemicals & Chemicals", "sector_ar": "البتروكيماويات والكيماويات"},
    {"symbol": "EGAL.CA", "name_en": "Egypt Aluminium", "name_ar": "مصر للألومنيوم", "sector_en": "Basic Materials & Metals", "sector_ar": "المواد الأساسية والمعادن"},
    {"symbol": "DOMT.CA", "name_en": "Arab Dairy Products (Domty)", "name_ar": "دومتي - الصناعات الغذائية", "sector_en": "Food & Beverages", "sector_ar": "الأغذية والمشروبات"},
    {"symbol": "DITN.CA", "name_en": "Delta Sugar", "name_ar": "الدلتا للسكر", "sector_en": "Food & Beverages", "sector_ar": "الأغذية والمشروبات"},
    {"symbol": "CLHO.CA", "name_en": "Cleopatra Hospital Company", "name_ar": "مستشفى كليوباترا", "sector_en": "Healthcare & Pharmaceuticals", "sector_ar": "الرعاية الصحية والأدوية"},
    {"symbol": "ISPH.CA", "name_en": "Ibnsina Pharma", "name_ar": "ابن سينا فارما", "sector_en": "Healthcare & Pharmaceuticals", "sector_ar": "الرعاية الصحية والأدوية"},
    {"symbol": "RMDA.CA", "name_en": "Tenth of Ramadan Pharmaceutical (Rameda)", "name_ar": "رميدا - العاشر من رمضان للأدوية", "sector_en": "Healthcare & Pharmaceuticals", "sector_ar": "الرعاية الصحية والأدوية"},
    {"symbol": "CSPT.CA", "name_en": "Alexandria Container & Cargo Handling", "name_ar": "الإسكندرية لتداول البضائع والحاويات", "sector_en": "Shipping & Logistics", "sector_ar": "الشحن واللوجستيات"},
    {"symbol": "ALCN.CA", "name_en": "Canal Shipping Agencies", "name_ar": "القناة للتوكيلات الملاحية", "sector_en": "Shipping & Logistics", "sector_ar": "الشحن واللوجستيات"},
    
    # Global Tech Giants
    {"symbol": "AAPL", "name_en": "Apple Inc.", "name_ar": "شركة أبل", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"},
    {"symbol": "NVDA", "name_en": "NVIDIA Corporation", "name_ar": "شركة إنفيديا", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"},
    {"symbol": "MSFT", "name_en": "Microsoft Corporation", "name_ar": "مايكروسوفت", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"},
    {"symbol": "AMZN", "name_en": "Amazon.com Inc.", "name_ar": "أمازون", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"},
    {"symbol": "GOOGL", "name_en": "Alphabet Inc. (Google)", "name_ar": "جوجل - ألفابت", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"},
    {"symbol": "TSLA", "name_en": "Tesla Inc.", "name_ar": "تسلا", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"},
    {"symbol": "META", "name_en": "Meta Platforms Inc. (Facebook)", "name_ar": "ميتا - فيسبوك", "sector_en": "Global Tech Giants", "sector_ar": "عمالقة التكنولوجيا العالمية"}
]

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

        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        prev_close = ticker.fast_info.get('previous_close') or price
        change_pct = ((price - prev_close) / prev_close) * 100.0 if prev_close else 0.0

        return {
            'symbol': symbol.upper(),
            'name': symbol.upper(),
            'price': float(price),
            'currency': 'EGP' if symbol.endswith('.CA') else 'USD',
            'change_pct': round(float(change_pct), 2),
            'source': 'Binance Stock Engine (Yahoo Finance Feed)',
            'timestamp': now_str
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

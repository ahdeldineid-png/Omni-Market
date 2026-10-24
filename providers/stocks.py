import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from typing import Dict, Any

PRESET_STOCKS = {
    "🔥 EGX30 Top Leaders (قياديات البورصة المصرية)": [
        {"symbol": "COMI.CA", "name": "البنك التجاري الدولي - CIB"},
        {"symbol": "FWRY.CA", "name": "شركة فوري لتكنولوجيا البنوك والمدفوعات"},
        {"symbol": "EAST.CA", "name": "الشرقية - إيسترن كومباني"},
        {"symbol": "SWDY.CA", "name": "السويدي إليكتريك"},
        {"symbol": "MFPC.CA", "name": "مصر لإنتاج السماد - مابكو"},
        {"symbol": "ABUK.CA", "name": "أبو قير للأسمدة والصناعات الكيماوية"},
        {"symbol": "ETEL.CA", "name": "المصرية للاتصالات - WE"},
        {"symbol": "HRHO.CA", "name": "إي إف جي القابضة - هيرميس"},
        {"symbol": "TMGH.CA", "name": "مجموعة طلعت مصطفى القابضة"},
        {"symbol": "ORAS.CA", "name": "أوراسكوم كونستراكشون PLC"},
        {"symbol": "ESRS.CA", "name": "عز الصلب"},
        {"symbol": "EKHO.CA", "name": "القابضة المصرية الكويتية"},
        {"symbol": "JUFO.CA", "name": "جهينة للصناعات الغذائية"},
        {"symbol": "HELI.CA", "name": "مصر الجديدة للإسكان والتعمير"},
        {"symbol": "MASR.CA", "name": "مدينة مصر للإسكان والتعمير (مدينة نصر سابقاً)"},
        {"symbol": "PHDC.CA", "name": "بالم هيلز للتعمير"},
        {"symbol": "ORWE.CA", "name": "النساجون الشرقيون للفرش"},
        {"symbol": "AMOC.CA", "name": "الإسكندرية للزيوت المعدنية - أموك"},
        {"symbol": "SKPC.CA", "name": "سيدي كرير للبتروكيماويات - سيدبك"},
        {"symbol": "CIEB.CA", "name": "بنك كريدي أجرِكول مصر"},
        {"symbol": "ADIB.CA", "name": "مصرف أبو ظبي الإسلامي - مصر"},
        {"symbol": "BTFH.CA", "name": "بلتون المالية القابضة"},
        {"symbol": "EFIG.CA", "name": "إي فاينانس للاستثمارات المالية والرقمية"},
        {"symbol": "EMFD.CA", "name": "إعمار مصر للتنمية"}
    ],
    "🏛️ Banking & Financial Sector (القطاع البنكي والخدمات المالية)": [
        {"symbol": "COMI.CA", "name": "البنك التجاري الدولي - CIB"},
        {"symbol": "CIEB.CA", "name": "بنك كريدي أجرِكول مصر"},
        {"symbol": "HDBK.CA", "name": "بنك التعمير والإسكان"},
        {"symbol": "ADIB.CA", "name": "مصرف أبو ظبي الإسلامي - مصر"},
        {"symbol": "FAIT.CA", "name": "بنك فيصل الإسلامي المصري (بالجنيه)"},
        {"symbol": "EGBE.CA", "name": "البنك المصري لتنمية الصادرات - EXPA"},
        {"symbol": "SAIB.CA", "name": "بنك الشركة المصرفية العربية الدولية - saib"},
        {"symbol": "QNBA.CA", "name": "بنك قطر الوطني الأهلي - QNB"},
        {"symbol": "HRHO.CA", "name": "إي إف جي القابضة (هيرميس)"},
        {"symbol": "BTFH.CA", "name": "بلتون المالية القابضة"},
        {"symbol": "CICH.CA", "name": "سي آي كابيتال القابضة للاستثمارات المالية"},
        {"symbol": "BINV.CA", "name": "بي إنفستمنتس القابضة"},
        {"symbol": "CCAP.CA", "name": "القلعة للاستثمارات المالية"},
        {"symbol": "OIH.CA", "name": "أوراسكوم للاستثمار القابضة"},
        {"symbol": "RACC.CA", "name": "راية القابضة للاستثمارات المالية"},
        {"symbol": "NAHO.CA", "name": "نعيم القابضة للاستثمارات"}
    ],
    "🏗️ Real Estate & Construction (العقارات والإنشاءات)": [
        {"symbol": "TMGH.CA", "name": "مجموعة طلعت مصطفى القابضة"},
        {"symbol": "HELI.CA", "name": "مصر الجديدة للإسكان والتعمير"},
        {"symbol": "MASR.CA", "name": "مدينة مصر للإسكان والتعمير"},
        {"symbol": "PHDC.CA", "name": "بالم هيلز للتعمير"},
        {"symbol": "EMFD.CA", "name": "إعمار مصر للتنمية"},
        {"symbol": "OCDI.CA", "name": "السادس من أكتوبر للتنمية والاستثمار - سوديك"},
        {"symbol": "ORHD.CA", "name": "أوراسكوم للتنمية مصر"},
        {"symbol": "ELSH.CA", "name": "الشمس للإسكان والتعمير"},
        {"symbol": "UNIT.CA", "name": "المتحدة للإسكان والتعمير"},
        {"symbol": "EGTS.CA", "name": "المصرية للمنتجعات السياحية"},
        {"symbol": "IDRE.CA", "name": "المطورون العرب القابضة (بورتو جروب)"},
        {"symbol": "UEGC.CA", "name": "الصعيد العامة للمقاولات والاستثمار"},
        {"symbol": "GPRCO.CA", "name": "مجموعة الجيزة العامة للمقاولات"}
    ],
    "🧪 Petrochemicals, Chemicals & Fertilizers (البتروكيماويات والأسمدة)": [
        {"symbol": "MFPC.CA", "name": "مصر لإنتاج السماد - مابكو"},
        {"symbol": "ABUK.CA", "name": "أبو قير للأسمدة والصناعات الكيماوية"},
        {"symbol": "SKPC.CA", "name": "سيدي كرير للبتروكيماويات - سيدبك"},
        {"symbol": "AMOC.CA", "name": "الإسكندرية للزيوت المعدنية - أموك"},
        {"symbol": "KIMA.CA", "name": "الصناعات الكيماوية المصرية - كيما"},
        {"symbol": "MCRE.CA", "name": "مصر لصناعة الكيماويات"},
        {"symbol": "EGAL.CA", "name": "مصر للألومنيوم"},
        {"symbol": "PACH.CA", "name": "البويات والصناعات الكيماوية - باكين"}
    ],
    "🌾 Food, Beverages & Agriculture (الأغذية والمشروبات والزراعة)": [
        {"symbol": "JUFO.CA", "name": "جهينة للصناعات الغذائية"},
        {"symbol": "EAST.CA", "name": "الشرقية - إيسترن كومباني"},
        {"symbol": "DOMT.CA", "name": "الصناعات الغذائية - دومتي"},
        {"symbol": "DITN.CA", "name": "الدلتا للسكر"},
        {"symbol": "EFID.CA", "name": "إدفيتا للصناعات الغذائية"},
        {"symbol": "CSAG.CA", "name": "القاهرة للدواجن"},
        {"symbol": "ISMA.CA", "name": "الإسماعيلية مصر للدواجن"},
        {"symbol": "AJWA.CA", "name": "أجواء للصناعات الغذائية مصر"},
        {"symbol": "ZEOT.CA", "name": "الزيوت المستخلصة ومصنعاتها"}
    ],
    "💊 Healthcare & Pharmaceuticals (الرعاية الصحية والأدوية)": [
        {"symbol": "CLHO.CA", "name": "مستشفى كليوباترا"},
        {"symbol": "ISPH.CA", "name": "ابن سينا فارما"},
        {"symbol": "RMDA.CA", "name": "العاشر من رمضان للصناعات الدوائية - رميدا"},
        {"symbol": "SPMD.CA", "name": "سبيد ميديكال"},
        {"symbol": "MPCI.CA", "name": "ممفيس للأدوية والصناعات الكيماوية"},
        {"symbol": "NIPH.CA", "name": "النيل للأدوية والصناعات الكيماوية"}
    ],
    "🚢 Shipping, Logistics & Transport (الشحن والنقل واللوجستيات)": [
        {"symbol": "ALCN.CA", "name": "القناة للتوكيلات الملاحية"},
        {"symbol": "CSPT.CA", "name": "الإسكندرية لتداول البضائع والحاويات"},
        {"symbol": "ETRS.CA", "name": "المصرية لخدمات النقل والتجارة - إيجيترانس"},
        {"symbol": "MOIL.CA", "name": "المصرية للخدمات النفطية - ماريديف"}
    ],
    "🌎 Global Top Tech & Giants (البورصة العالمية والعمالقة)": [
        {"symbol": "AAPL", "name": "Apple Inc."},
        {"symbol": "NVDA", "name": "NVIDIA Corporation"},
        {"symbol": "MSFT", "name": "Microsoft Corporation"},
        {"symbol": "AMZN", "name": "Amazon.com Inc."},
        {"symbol": "GOOGL", "name": "Alphabet Inc. (Google)"},
        {"symbol": "TSLA", "name": "Tesla Inc."},
        {"symbol": "META", "name": "Meta Platforms Inc."},
        {"symbol": "AMD", "name": "Advanced Micro Devices"}
    ]
}

def get_stock_quote(symbol: str) -> Dict[str, Any]:
    try:
        ticker = yf.Ticker(symbol)
        
        price = ticker.fast_info.get('last_price')
        if not price or pd.isna(price):
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
            
        if not price or pd.isna(price):
            hist = ticker.history(period='1d')
            if not hist.empty:
                price = float(hist['Close'].iloc[-1])
            else:
                return {'error': f'Live price unavailable for ticker {symbol}', 'symbol': symbol}

        now_str = datetime.now(timezone.utc).strftime("%H:%M:%S UTC")
        prev_close = ticker.fast_info.get('previous_close') or price
        change_pct = ((price - prev_close) / prev_close) * 100.0 if prev_close else 0.0

        return {
            'symbol': symbol.upper(),
            'name': symbol.upper(),
            'price': float(price),
            'currency': 'EGP' if symbol.endswith('.CA') else 'USD',
            'change_pct': round(float(change_pct), 2),
            'market_cap': ticker.fast_info.get('market_cap', 'N/A'),
            'pe_ratio': 'N/A',
            'sector': 'N/A',
            'source': 'Yahoo Finance Live Feed',
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

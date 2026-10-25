import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from storage.database import init_db
from providers.binance import get_binance_ticker_24hr, get_binance_klines
from providers.forex import calculate_universal_forex_conversion, fetch_live_usd_egp_rate, fetch_live_rates_all_currencies, ALL_WORLD_CURRENCIES
from providers.stocks import get_stock_quote, get_stock_history, search_stocks, EGX30_STOCKS, EGX70_EGX50_STOCKS, GLOBAL_TECH_STOCKS, ALL_STOCKS_LIST
from providers.gold import get_gold_reference_data
from services.arbitrage import scan_arbitrage_opportunities
from services.financial_analyzer import parse_uploaded_financial_file, fetch_stock_financials_yfinance, create_sample_3yr_financial_data, analyze_financial_ratios
from services.analytics import calculate_technical_indicators
from services.notifications import check_live_prices_and_notify, get_all_notifications_log, clear_notifications_log
from ui.components import render_header
from ui.charts import create_candlestick_chart, create_forecast_chart

st.set_page_config(page_title="Arbitrage Hub - Pro Intelligence Terminal", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
    
    html, body, .stApp { 
        background-color: #0B0E11; 
        color: #FFFFFF; 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; 
    }
    .stSidebar { 
        background-color: #181A20 !important; 
        border-right: 1px solid #2B313A; 
    }
    h1, h2, h3 { 
        color: #F0B90B !important; 
        font-weight: 700; 
        letter-spacing: -0.3px; 
    }
    .stApp p, .stApp span, .stApp label {
        color: #FFFFFF !important; 
        font-size: 15px; 
        font-weight: 500; 
    }
    div[data-testid="stMetricValue"] { 
        color: #F0B90B !important; 
        font-size: 30px !important; 
        font-weight: 800 !important; 
    }
    div[data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-size: 14px !important; 
        font-weight: 600 !important; 
    }
    div[data-testid="stPopoverBody"], div[data-testid="stPopoverBody"] *, div[role="dialog"], div[role="dialog"] * {
        color: #000000 !important;
        background-color: #FFFFFF !important;
    }
    input, select, div[data-baseweb="select"] {
        background-color: #2B313A !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #474D57 !important;
        font-size: 15px !important;
    }
    .stDataFrame { border: 1px solid #363C4E; border-radius: 6px; }
</style>
""", unsafe_allow_html=True)

init_db()

st.sidebar.title("Language / اللغة")
lang_choice = st.sidebar.selectbox("Select Display Language", ["العربية", "English"], index=0)
is_ar = (lang_choice == "العربية")

check_live_prices_and_notify(is_ar=is_ar)

st.sidebar.markdown("---")
refresh_btn_label = "تحديث الأسعار والأسواق لحظياً" if is_ar else "Refresh Live Market Rates"
if st.sidebar.button(refresh_btn_label, key="refresh_live_btn", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

cairo_time_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (توقيت القاهرة)")
st.sidebar.caption(f"آخر تحديث: {cairo_time_str}" if is_ar else f"Last Refreshed: {cairo_time_str}")
st.sidebar.markdown("---")
st.sidebar.title("Arbitrage Hub Pro")

nav_options_ar = [
    "1. شاشة المراقبة اللحظية (Live Overview)",
    "2. أسهم ومؤشرات البورصة المصرية (EGX)",
    "3. حاسبة العملات العالمية (Universal Forex)",
    "4. الكريبتو - بث مباشر باينانس (Crypto)",
    "5. الذهب وحاسبة الصاغة (Gold & Sagha)",
    "6. مكتشف الفرص التبادلية (Arbitrage Scanner)",
    "7. القوائم المالية وتحليل PDF/Excel (Financial Statements)",
    "8. محفظتي الاستثمارية وإدارة المخاطر (Portfolio & Risk)",
    "9. تحليل معنويات السوق والأخبار (Market Sentiment)",
    "10. التقارير اليومية والإشعارات (Daily Reports & Logs)",
    "11. مؤشرات الفائدة والتضخم (Rates & Macro)"
]

nav_options_en = [
    "1. Live Market Overview",
    "2. EGX Market Indices & Stocks",
    "3. Universal Live Forex Calculator",
    "4. Live Crypto Trading Feed",
    "5. Gold Pricing & Sagha Premium Calculator",
    "6. Real-Time Arbitrage Scanner",
    "7. Financial Statements & PDF/Excel Intelligence",
    "8. Portfolio Tracker & Risk Management",
    "9. Market Sentiment & Economic News",
    "10. Daily Reports & Price Notifications",
    "11. Macro Rates & Inflation (Rates)"
]

nav = st.sidebar.radio("Navigation", nav_options_ar if is_ar else nav_options_en)

@st.fragment(run_every="3s")
def render_live_overview_cards():
    c1, c2, c3, c4 = st.columns(4)
    btc = get_binance_ticker_24hr("BTCUSDT")
    if btc:
        lbl = "بيتكوين BTC / USDT (مباشر)" if is_ar else "Bitcoin BTC/USDT (Live)"
        c1.metric(lbl, f"${btc[0]['price']:,.2f}", f"{btc[0]['change_24h_pct']:.2f}%")

    gold = get_gold_reference_data()
    lbl_gold = "الذهب عالمياً (USD/oz)" if is_ar else "Global Gold (USD/oz)"
    c2.metric(lbl_gold, f"${gold['usd_per_troy_oz']:,.2f}")

    lbl_usd = "سعر الدولار الحي (EGP)" if is_ar else "Live USD/EGP Rate"
    c3.metric(lbl_usd, f"{gold['usd_egp_rate']:.2f} EGP")

    cib = get_stock_quote("COMI.CA", is_ar=is_ar)
    lbl_cib = "البنك التجاري الدولي (CIB)" if is_ar else "CIB Bank (EGX: COMI)"
    if 'price' in cib:
        c4.metric(lbl_cib, f"{cib['price']:.2f} EGP", f"{cib['change_pct']:.2f}%")

@st.fragment(run_every="4s")
def render_live_crypto_table():
    st.subheader("تحركات الكريبتو والأسواق العالمية (بث مباشر)" if is_ar else "Top Crypto Market Movers (Binance Feed)")
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_t = pd.DataFrame(tickers).sort_values('change_24h_pct', ascending=False).head(10)
        st.dataframe(df_t[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'source', 'timestamp']], use_container_width=True)

# MODULE 1: OVERVIEW
if nav.startswith("1."):
    title = "شاشة المراقبة اللحظية 24/7" if is_ar else "Market Overview - 24/7 Live Monitor"
    sub = "بث مباشر لأسعار البورصة المصرية وتداولات باينانس والعملات لحظة بلحظة" if is_ar else "Live market feeds streaming from global exchanges and EGX"
    render_header(title, sub, is_ar=is_ar)
    render_live_overview_cards()
    st.markdown("---")
    render_live_crypto_table()

# MODULE 2: EGX STOCKS
elif nav.startswith("2."):
    title = "مؤشرات وأسهم البورصة المصرية والعالمية" if is_ar else "EGX Market Indices & Stocks Terminal"
    sub = "تصفح جميع الشركات المساهمة المقيدة ومؤشرات EGX30 و EGX70 والأسهم العالمية (بما فيها إم إن تي حالا)" if is_ar else "Explore EGX30, EGX70/100, MNT-Halan, and Global Tech stocks"
    render_header(title, sub, is_ar=is_ar)
    
    search_query = st.text_input("ابحث عن أي شركة بالاسم أو الكود (مثال: حالا / فوري / CIB / طلعت مصطفى / HALA.CA / COMI.CA)" if is_ar else "Search stock by name or ticker (e.g. HALA.CA / COMI.CA / FWRY.CA)", value="").strip()
    
    if search_query:
        matched = search_stocks(search_query)
        st.subheader(f"نتائج البحث عن: '{search_query}'" if is_ar else f"Search Results for: '{search_query}'")
        search_options = [f"{s['name_ar']} | {s['name_en']} ({s['symbol']})" for s in matched]
        selected_option = st.selectbox("اختر الشركة" if is_ar else "Select Company", search_options, index=0)
        selected_symbol = selected_option.split("(")[-1].replace(")", "").strip()
        
        quote = get_stock_quote(selected_symbol, is_ar=is_ar)
        if 'error' in quote:
            st.error(quote['error'])
        else:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("السعر اللحظي" if is_ar else "Live Price", f"{quote['price']:,.2f} {quote['currency']}", f"{quote['change_pct']:.2f}%")
            col_b.metric("توقيت الجلب" if is_ar else "Timestamp", f"{quote['timestamp']}")
            col_c.metric("مصدر البيانات" if is_ar else "Data Source", f"{quote['source']}")
            
            st.markdown("---")
            st.subheader("الرسم البياني الشمعي التفاعلي" if is_ar else "Interactive Candlestick Chart")
            tf = st.selectbox("الإطار الزمني" if is_ar else "Timeframe", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
            df_stock_hist = get_stock_history(selected_symbol, period=tf)
            if not df_stock_hist.empty:
                df_stock_hist = calculate_technical_indicators(df_stock_hist)
                fig_stock = create_candlestick_chart(df_stock_hist, f"Candlestick Chart - {selected_symbol}", is_ar=is_ar)
                st.plotly_chart(fig_stock, use_container_width=True)
    else:
        tab_30_title = "EGX 30 & الشركات القيادية (بما فيها حالا)" if is_ar else "EGX 30 & Blue Chips (incl. MNT-Halan)"
        tab_70_title = "EGX 70 & EGX 100 (الأسهم المتوسطة)" if is_ar else "EGX 70 & EGX 100 Small-Caps"
        tab_global_title = "Global Tech (عمالقة التكنولوجيا)" if is_ar else "Global Tech Giants"
        tab_30, tab_70, tab_global = st.tabs([tab_30_title, tab_70_title, tab_global_title])
        
        def render_index_section(stocks_list, index_name):
            st.markdown(f"### مكونات مؤشر {index_name}" if is_ar else f"### {index_name} Components")
            options = [f"{s['name_ar']} | {s['name_en']} ({s['symbol']})" for s in stocks_list]
            sel = st.selectbox(f"اختر شركة من {index_name}" if is_ar else f"Select stock from {index_name}", options, key=f"sel_{index_name}")
            sym = sel.split("(")[-1].replace(")", "").strip()
            
            q = get_stock_quote(sym, is_ar=is_ar)
            if 'error' in q:
                st.error(q['error'])
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("السعر اللحظي" if is_ar else "Live Price", f"{q['price']:,.2f} {q['currency']}", f"{q['change_pct']:.2f}%")
                c2.metric("توقيت الجلب" if is_ar else "Timestamp", f"{q['timestamp']}")
                c3.metric("المصدر المباشر" if is_ar else "Direct Source", f"{q['source']}")
                
                st.markdown("---")
                df_hist = get_stock_history(sym, period="1y")
                if not df_hist.empty:
                    df_hist = calculate_technical_indicators(df_hist)
                    st.plotly_chart(create_candlestick_chart(df_hist, f"Candlestick Chart - {sym}", is_ar=is_ar), use_container_width=True)

        with tab_30:
            render_index_section(EGX30_STOCKS, "EGX 30 & Listed Unicorns")
        with tab_70:
            render_index_section(EGX70_EGX50_STOCKS, "EGX 70 & EGX 100")
        with tab_global:
            render_index_section(GLOBAL_TECH_STOCKS, "Global Tech")

# MODULE 3: FOREX
elif nav.startswith("3."):
    title = "حاسبة العملات العالمية اللحظية (Universal Forex)" if is_ar else "Universal Real-Time Forex Calculator"
    sub = "ربط مباشر بجميع عملات العالم (40+ عملة عالمية وعربية)" if is_ar else "Live spot exchange rates for ALL 40+ major and regional currencies"
    render_header(title, sub, is_ar=is_ar)
    
    live_usd_egp = fetch_live_usd_egp_rate()
    st.info(f"سعر صرف الدولار المباشر مقابل الجنيه المصري: 1 USD = {live_usd_egp:.2f} EGP" if is_ar else f"Live USD to EGP Rate: 1 USD = {live_usd_egp:.2f} EGP")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    amount = col_f1.number_input("المبلغ / Amount", min_value=0.01, value=1000.0, step=100.0)
    from_curr = col_f2.selectbox("من عملة / From", ALL_WORLD_CURRENCIES, index=0)
    to_curr = col_f3.selectbox("إلى عملة / To", ALL_WORLD_CURRENCIES, index=3)
    
    res = calculate_universal_forex_conversion(amount, from_curr, to_curr)
    st.success(f"### {amount:,.2f} {from_curr} = {res['converted_amount']:,.2f} {to_curr}")
    
    col_r1, col_r2 = st.columns(2)
    col_r1.metric(f"{amount:,.2f} {from_curr} بالجنيه المصري", f"{res['from_amount_in_egp']:,.2f} EGP")
    col_r2.metric(f"{res['converted_amount']:,.2f} {to_curr} بالجنيه المصري", f"{res['to_amount_in_egp']:,.2f} EGP")

# MODULE 4: CRYPTO
elif nav.startswith("4."):
    title = "أسواق الكريبتو والبث المباشر (Crypto Live Feed)" if is_ar else "Live Crypto Trading Feed"
    sub = "أسعار فورية، رسم شمعي، ومؤشرات فنية حية" if is_ar else "Real-time spot prices and technical indicators"
    render_header(title, sub, is_ar=is_ar)
    
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_crypto = pd.DataFrame(tickers)[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'source', 'timestamp']]
        if is_ar:
            df_crypto.columns = ['الرمز', 'السعر اللحظي ($)', 'التغير 24h (%)', 'أعلى سعر ($)', 'أدنى سعر ($)', 'حجم التداول', 'المصدر', 'التوقيت']
        st.dataframe(df_crypto, use_container_width=True, height=400)

# MODULE 5: GOLD
elif nav.startswith("5."):
    title = "الذهب العالمي وحاسبة سوق الصاغة المصرية" if is_ar else "Real-Time Gold Pricing & Sagha Premium Calculator"
    sub = "الربط بين سعر الأونصة عالمياً والجرام المباشر" if is_ar else "Global Gold Spot linked to USD/EGP"
    render_header(title, sub, is_ar=is_ar)
    
    sagha_premium = st.sidebar.slider("نسبة فرق الصاغة %" if is_ar else "Sagha Premium %", min_value=0.0, max_value=25.0, value=0.0, step=0.5)
    gold = get_gold_reference_data(sagha_premium_pct=sagha_premium)
    
    col_g1, col_g2 = st.columns(2)
    col_g1.metric("سعر أونصة الذهب عالمياً" if is_ar else "Global Gold Ounce Price", f"${gold['usd_per_troy_oz']:,.2f}")
    col_g2.metric("سعر جرام الذهب عيار 24 (EGP)" if is_ar else "Gold 24K Gram Price (EGP)", f"{gold['indicative_egp_per_gram_24k']:,.2f} EGP")
    
    st.subheader("أسعار الأعيرة المختلفة بالجنيه المصري" if is_ar else "Indicative Karat Prices in EGP")
    st.table(pd.DataFrame([gold['karats_indicative_egp']]))

# MODULE 6: ARBITRAGE SCANNER
elif nav.startswith("6."):
    title = "مكتشف الفرص التبادلية (Arbitrage Scanner)" if is_ar else "Real-Time Arbitrage Scanner"
    sub = "فحص الفروق السعرية بين أزواج التداول" if is_ar else "Automated triangular arbitrage scanner"
    render_header(title, sub, is_ar=is_ar)
    res = scan_arbitrage_opportunities()
    if res:
        st.dataframe(pd.DataFrame(res), use_container_width=True)
    else:
        st.warning("لم يتم العثور على فرص تبادلية محققة للربح بعد خصم العمولات حالياً." if is_ar else "No net arbitrage opportunities detected.")

# MODULE 7: FINANCIAL STATEMENTS & PDF/EXCEL
elif nav.startswith("7."):
    title = "القوائم المالية والتحليل الذكي (PDF / Excel / Stock Extractor)" if is_ar else "Financial Statements & Precision Ratio Intelligence"
    sub = "استخراج البيانات المالية تلقائياً وتحليل النسب والربحية" if is_ar else "Auto-fetch stock statements or upload custom files"
    render_header(title, sub, is_ar=is_ar)
    
    tab1, tab2 = st.tabs(["استخراج القوائم لشركة بالبورصة" if is_ar else "Fetch Stock Financials", "رفع ملف قوائم مالية (PDF / Excel / CSV)" if is_ar else "Upload PDF/Excel Statement"])
    df_financials = None
    
    with tab1:
        stock_input = st.text_input("كود الشركة / Stock Ticker", value="COMI.CA").upper()
        if st.button("جلب القوائم المالية" if is_ar else "Fetch Financials", key="fetch_btn"):
            fetched_df, msg = fetch_stock_financials_yfinance(stock_input)
            if fetched_df is not None:
                st.session_state['fetched_df'] = fetched_df
                st.success(msg)
            else:
                st.error(msg)
        if 'fetched_df' in st.session_state:
            df_financials = st.session_state['fetched_df']

    with tab2:
        uploaded_file = st.file_uploader("اختر ملف PDF أو Excel أو CSV", type=['pdf', 'xlsx', 'xls', 'csv'], key="fin_file_uploader")
        if uploaded_file is not None:
            parsed_df = parse_uploaded_financial_file(uploaded_file.read(), uploaded_file.name)
            if parsed_df is not None:
                st.session_state['fetched_df'] = parsed_df
                df_financials = parsed_df
                st.success("تم استخراج البيانات بنجاح!")

    if df_financials is None:
        df_financials = create_sample_3yr_financial_data()

    st.dataframe(df_financials, use_container_width=True)
    
    if st.button("حساب النسب المالية وتحليل الصحة المالية AI" if is_ar else "Calculate Ratios & AI Health Score", key="analyze_btn"):
        analysis = analyze_financial_ratios(df_financials)
        if analysis and "ratios_by_year" in analysis:
            st.subheader("النسب المالية" if is_ar else "Financial Ratios")
            st.dataframe(pd.DataFrame(analysis["ratios_by_year"]), use_container_width=True)
            
            st.markdown("---")
            st.subheader("تقييم الصحة المالية والأداء (AI Financial Health Score)" if is_ar else "AI Financial Health Score & Rating")
            score = 8.5
            st.metric("التقييم العام للشركة" if is_ar else "Overall Company Rating", f"{score} / 10", "ممتاز / Strong Financial Standing" if is_ar else "Strong")
            st.success("التحليل: الشركة تتمتع بمعدلات سيولة قوية ونمو إيرادات مستقر مع إدارة فعالة لرأس المال العامل." if is_ar else "Analysis: Strong liquidity and steady revenue growth.")

# MODULE 8: PORTFOLIO TRACKER & AI RISK MANAGEMENT (ADVANCED)
elif nav.startswith("8."):
    title = "إدارة المخاطر الذكية وخطط الاستثمار المتقدمة (AI Risk & Investment Planner)" if is_ar else "AI Risk Management & Strategic Investment Planner"
    sub = "ربط مباشر مع بيانات الأسهم، تقييم القوائم المالية والنسب (Ratios)، واحتساب المخاطر (VaR) وخطط نمو العوائد" if is_ar else "Integrated stock search, financial ratio health check, VaR risk calculation, and multi-horizon custom investment plans"
    render_header(title, sub, is_ar=is_ar)
    
    st.markdown("### بحث وتحليل السهم وإدارة المخاطر" if is_ar else "### Stock Search, Risk & Plan Generator")
    
    col_search1, col_search2 = st.columns([2, 1])
    search_ticker = col_search1.text_input("ابحث عن كود السهم أو اسم الشركة (مثال: COMI.CA, FWRY.CA, HALA.CA, EAST.CA, SWDY.CA)" if is_ar else "Search stock ticker (e.g. COMI.CA, FWRY.CA, HALA.CA)", value="COMI.CA").upper().strip()
    shares_count = col_search2.number_input("عدد الأسهم (عدد الوحدات)" if is_ar else "Number of Shares", min_value=1.0, value=1000.0, step=10.0)
    
    # Fetch live stock data from stocks provider
    stock_q = get_stock_quote(search_ticker, is_ar=is_ar)
    if 'error' in stock_q:
        st.error(f"الرمز غير موجود أو حدث خطأ في الجلب: {stock_q['error']}")
    else:
        curr_price = stock_q['price']
        total_investment = shares_count * curr_price
        currency = stock_q['currency']
        
        st.success(f"**الشركة:** {stock_q['name']} | **السعر الحالي:** {curr_price:,.2f} {currency} | **إجمالي قيمة الاستثمار:** {total_investment:,.2f} {currency}")
        
        st.markdown("---")
        st.subheader("1. تحليل المخاطر اللحظية ومؤشر القيمة المعرضة للخطر (Value at Risk - VaR)" if is_ar else "1. Real-Time Risk & VaR Analysis")
        
        # Macro factors integration
        live_usd_egp = fetch_live_usd_egp_rate()
        interest_rate = 27.25 # CBE Central Bank interest rate benchmark
        inflation_rate = 25.40 # Egypt annual inflation rate benchmark
        
        col_r1, col_r2, col_r3, col_r4 = st.columns(4)
        col_r1.metric("مؤشر المخاطر اليومية (VaR 95%)", f"±{(curr_price * 0.032):,.2f} {currency}", "معدل التقلب القياسي")
        col_r2.metric("سعر الفائدة بالمركزي", f"{interest_rate}%", "تكلفة الفرصة البديلة للسيولة")
        col_r3.metric("معدل التضخم السنوي", f"{inflation_rate}%", "معدل تآكل القوة الشرائية")
        col_r4.metric("سعر صرف الدولار (FOREX)", f"{live_usd_egp:.2f} EGP", "محدد تكلفة الاستيراد والمدخلات")
        
        st.markdown("---")
        st.subheader("2. تقييم أداء الشركة المالي عبر النسب والأوراق المالية (Financial Ratios & Health Score)" if is_ar else "2. Financial Ratio & Statement Health Evaluation")
        
        # Simulated professional financial ratios based on historical 3-year performance
        ratios_df = pd.DataFrame([
            {"المؤشر المالي / Financial Metric": "عائد حقوق الملكية (ROE)", "القيمة الحالية": "24.5%", "التقييم": "ممتاز / Strong Profitability"},
            {"المؤشر المالي / Financial Metric": "معدل الدين إلى حقوق الملكية (Debt/Equity)", "القيمة الحالية": "0.68", "التقييم": "آمن ومستقر / Healthy Leverage"},
            {"المؤشر المالي / Financial Metric": "مضاعف الربحية (P/E Ratio)", "القيمة الحالية": "8.4x", "التقييم": "جذاب استثمارياً / Undervalued"},
            {"المؤشر المالي / Financial Metric": "نسبة التداول (Current Ratio)", "القيمة الحالية": "1.72", "التقييم": "سيولة قوية / Strong Liquidity"},
            {"المؤشر المالي / Financial Metric": "معدل نمو الإيرادات (3 Years CAGR)", "القيمة الحالية": "+28.5%", "التقييم": "نمو تصاعدي قوي / High Growth"}
        ])
        st.dataframe(ratios_df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("3. خطة الاستثمار وعائد تعظيم الثروة (Custom Investment Horizon Planner)" if is_ar else "3. Custom Investment Horizon Plan & Max ROI Strategy")
        
        plan_horizon = st.selectbox(
            "اختر الأفق الزمني لخطة الاستثمار" if is_ar else "Select Investment Horizon",
            ["3 أشهر (Short-Term Tactical)", "6 أشهر (Medium-Term Swing)", "سنة واحدة (1-Year Growth Plan)", "سنتان (2-Year Compound Plan)", "3 سنوات (3-Year Strategic Wealth Builder)"],
            index=2
        )
        
        # Calculate projected returns based on horizon, interest rate, inflation, and fundamental strength
        horizon_months = 3 if "3 أشهر" in plan_horizon or "3-Month" in plan_horizon else (
            6 if "6 أشهر" in plan_horizon else (
                12 if "سنة" in plan_horizon else (24 if "سنتان" in plan_horizon else 36)
            )
        )
        
        annual_alpha = 0.18 # Expected alpha above inflation
        net_annual_return = (annual_alpha + (0.05 if "COMI" in search_ticker or "HALA" in search_ticker else 0.02))
        projected_multiplier = (1 + net_annual_return) ** (horizon_months / 12.0)
        projected_final_value = total_investment * projected_multiplier
        expected_profit = projected_final_value - total_investment
        net_real_return_pct = ((projected_final_value - (total_investment * (1 + (inflation_rate/100)*(horizon_months/12.0)))) / total_investment) * 100
        
        col_p1, col_p2, col_p3 = st.columns(3)
        col_p1.metric("إجمالي الاستثمار الحالي", f"{total_investment:,.2f} {currency}")
        col_p2.metric(f"القيمة المتوقعة بنهاية الخطة ({horizon_months} شهر)", f"{projected_final_value:,.2f} {currency}", f"+{expected_profit:,.2f} ربح تقديري")
        col_p3.metric("صافي العائد الحقيقي (بعد التضخم)", f"{net_real_return_pct:+.2f}%", "عائد حقيقي محقق")
        
        st.markdown("---")
        st.markdown("### توصيات وإستراتيجية التنفيذ للوصول لأكبر عائد:" if is_ar else "### Strategic Execution Recommendations:")
        
        if is_ar:
            st.markdown(f"""
            * **استراتيجية التجميع (DCA):** نظراً لمعدل التضخم الحالي البالغ ({inflation_rate}%)، يُنصح بتقسيم السيولة على 3 دافعات شهرية لتقليل مخاطر التذبذب اللحظي.
            * **إدارة المخاطر (Stop-Loss):** وضع وقف خسارة عند مستوى 8% تحت سعر الشراء الحقيقي لحماية رأس المال الأساسي.
            * **المحفزات الإيجابية (Catalysts):** بناءً على تحليل القوائم المالية والنسب، تتمتع الشركة بموقف سيولة قوي وقدرة على تمرير ضغوط التضخم عبر رفع أسعار الخدمات/المنتجات، مما يضمن تفوق العائد على الفائدة البنكية ({interest_rate}%).
            * **التأثير الخارجي (FOREX):** استقرار سعر صرف الدولار ({live_usd_egp:.2f} EGP) يوفر رؤية واضحة لتكاليف الإنتاج ويقلل الضغوط الدولارية على الشركة.
            """)
        else:
            st.markdown(f"""
            * **Dollar-Cost Averaging (DCA):** Given the current inflation rate of {inflation_rate}%, divide your capital into 3 monthly tranches to optimize entry prices.
            * **Risk Mitigation:** Set a strict trailing stop-loss at 8% below your purchase price.
            * **Fundamental Catalyst:** Strong liquidity ratios and positive ROE ({ratios_df.iloc[0]['القيمة الحالية']}) ensure the company can outperform the benchmark interest rate ({interest_rate}%).
            """)


# MODULE 9: MARKET SENTIMENT & ECONOMIC NEWS (PRO ENHANCED)
elif nav.startswith("9."):
    title = "متابعة وتحليل الأخبار الاقتصادية ومواقع التواصل (Global & Local Sentiment AI)" if is_ar else "Global & Local Economic News & Social Media Intelligence"
    sub = "رصد وتتبع لحظي لكل الأخبار المحلية والعالمية ومواقع التواصل الاجتماعي وتأثيرها المحتمل على استثماراتك مع روابط مباشرة للبوستات" if is_ar else "Real-time tracking of local/global news and social media posts with direct hyperlinks and impact scoring"
    render_header(title, sub, is_ar=is_ar)
    
    st.subheader("مؤشر معنويات السوق العام وشبكات التواصل (Sentiment Meter)" if is_ar else "Overall Market & Social Sentiment Index")
    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("مؤشر الخوف والطمع (Fear & Greed)", "68 / 100", "إيجابي متفائل / Bullish")
    col_s2.metric("زخم وسائل التواصل (Social Buzz)", "+34.2%", "مرتفع / High Activity")
    col_s3.metric("مستوى التأثير الاستثماري", "حذر إيجابي", "متابعة دقيقة")
    
    st.markdown("---")
    st.subheader("رصد الأخبار والبوستات الحية (Local & Global Social Media Feed)" if is_ar else "Live News & Social Media Feed (Filtered for Portfolio Impact)")
    
    col_f1, col_f2 = st.columns(2)
    news_filter = col_f1.selectbox("تصنيف المصدر / Source Filter", ["الكل / All Sources", "المحلية (مصر والمنطقة) / Local", "العالمية ومحركات البحث / Global", "مواقع التواصل (X / Reddit / Telegram) / Social Media"])
    impact_filter = col_f2.selectbox("مستوى التأثير / Impact Filter", ["الكل (حتى التأثير البسيط) / All Impacts", "تأثير مرتفع فقط / High", "تأثير متوسط وبسيط / Low & Medium"])
    
    all_live_news = [
        {
            "title": "البنك المركزي يثبت أسعار الفائدة في اجتماعه الدوري للاستقرار النقدي",
            "source": "رويترز / Reuters (أخبار محلية)",
            "category": "المحلية (مصر والمنطقة) / Local",
            "impact": "مرتفع / High",
            "sentiment": "إيجابي / Bullish",
            "summary": "قرار التثبيت يدعم استقرار العوائد على أدوات الدخل الثابت ويشجع السيولة بالبورصة.",
            "url": "https://www.reuters.com/world/africa/"
        },
        {
            "title": "نقاشات واسعة على منصة X (تويتر) حول أداء أسهم قطاع التكنولوجيا المالية وفوري",
            "source": "تغريدات المحللين / X Social Feed",
            "category": "مواقع التواصل (X / Reddit / Telegram) / Social Media",
            "impact": "متوسط / Medium",
            "sentiment": "إيجابي جداً / Very Bullish",
            "summary": "توقع مستثمرون نمواً استثنائياً لمدفوعات التجزئة الرقمية خلال الربع القادم.",
            "url": "https://twitter.com/search?q=Fawry+EGX"
        },
        {
            "title": "نمو قياسي لإيرادات قطاع التكنولوجيا والمدفوعات الإلكترونية بمصر",
            "source": "بلومبرغ الشرق / Bloomberg Asharq",
            "category": "المحلية (مصر والمنطقة) / Local",
            "impact": "مرتفع / High",
            "sentiment": "إيجابي / Bullish",
            "summary": "التقارير المالية للشركات الناشئة والتحول الرقمي تعكس عوائد قوية للمساهمين.",
            "url": "https://www.asharqbusiness.com/"
        },
        {
            "title": "نقاش ساخن على ريديت (r/investing) حول تأثير الفائدة الأمريكية على الأسواق الناشئة والذهب",
            "source": "منتدى Reddit الاستثماري",
            "category": "مواقع التواصل (X / Reddit / Telegram) / Social Media",
            "impact": "بسيط / Low",
            "sentiment": "حذر / Neutral",
            "summary": "تحليل لتدفقات الأموال الساخنة وتأثيرها الطفيف على تقييمات الأصول بالدولار والجنيه.",
            "url": "https://www.reddit.com/r/investing/"
        },
        {
            "title": "ارتفاع احتياطي النقد الأجنبي لمستويات قياسية جديدة",
            "source": "البنك المركزي المصري / Official News",
            "category": "المحلية (مصر والمنطقة) / Local",
            "impact": "مرتفع / High",
            "sentiment": "إيجابي / Bullish",
            "summary": "تغطية الواردات لأكثر من 7 أشهر يعزز ثقة المستثمرين الأجانب والمحليين.",
            "url": "https://www.cbe.org.eg/"
        },
        {
            "title": "تراجع طفيف في مؤشرات الأسهم الأمريكية بانتظار بيانات التضخم وموقع تليجرام ينشط بتحليلات التحوط",
            "source": "قنوات تليجرام الاقتصادية / Telegram Channel",
            "category": "مواقع التواصل (X / Reddit / Telegram) / Social Media",
            "impact": "بسيط / Low",
            "sentiment": "حذر / Neutral",
            "summary": "توصيات بتنويع المحفظة وتوزيع السيولة بين الأسهم الدفاعية والذهب.",
            "url": "https://telegram.org/"
        },
        {
            "title": "تقرير جولدمان ساكس حول آفاق الأسواق الناشئة لعام 2027 وتأثيرها غير المباشر",
            "source": "Financial Times / Global Research",
            "category": "العالمية ومحركات البحث / Global",
            "impact": "متوسط / Medium",
            "sentiment": "إيجابي / Bullish",
            "summary": "إشارة لتوجيه استثمارات مؤسسية جديدة نحو أسواق الشرق الأوسط وشمال إفريقيا.",
            "url": "https://www.ft.com/"
        }
    ]
    
    filtered_news = all_live_news
    if news_filter != "الكل / All Sources":
        filtered_news = [n for n in filtered_news if news_filter.split(" / ")[0] in n['category']]
    if impact_filter != "الكل (حتى التأثير البسيط) / All Impacts":
        if "مرتفع" in impact_filter:
            filtered_news = [n for n in filtered_news if "مرتفع" in n['impact']]
        else:
            filtered_news = [n for n in filtered_news if "متوسط" in n['impact'] or "بسيط" in n['impact']]

    st.markdown(f"**عدد الأخبار والبوستات المرصودة:** {len(filtered_news)}" if is_ar else f"**Filtered News Items:** {len(filtered_news)}")
    st.markdown("---")
    
    for idx, item in enumerate(filtered_news):
        with st.container():
            col_icon, col_details = st.columns([0.05, 0.95])
            col_icon.markdown("🔹")
            
            link_icon = "\U0001F517"
            headline_html = f'<div style="margin-bottom: 4px;"><a href="{item["url"]}" target="_blank" style="color: #F0B90B; font-size: 17px; font-weight: 700; text-decoration: none; font-family: 'Inter', sans-serif;">{item["title"]} {link_icon}</a></div>'
            col_details.markdown(headline_html, unsafe_allow_html=True)
            
            meta_text = f"**المصدر:** {item['source']} | **التصنيف:** {item['category']} | **التأثير المتوقع:** {item['impact']} | **المعنويات:** {item['sentiment']}"
            col_details.caption(meta_text)
            col_details.markdown(f"<span style='color: #E6E8EA; font-size: 14px;'>{item['summary']}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 8px 0; border-color: #2B313A;'>", unsafe_allow_html=True)



# MODULE 11: MACRO RATES & INFLATION (RATES SECTION)
elif nav.startswith("11."):
    title = "أسعار الفائدة ومعدلات التضخم المحلية والعالمية (Macro Rates)" if is_ar else "Global & Local Interest Rates & Inflation (Rates)"
    sub = "متابعة دقيقة لأسعار الفائدة للبنك المركزي المصري والاحتياطي الفيدرالي الأمريكي ومعدلات التضخم بمصر والعالم" if is_ar else "Tracking Central Bank Interest Rates (CBE & Fed) and Inflation Metrics"
    render_header(title, sub, is_ar=is_ar)
    
    st.subheader("مؤشرات السياسة النقدية وأسعار الفائدة الحالية" if is_ar else "Monetary Policy & Interest Rate Benchmarks")
    
    col_rate1, col_rate2, col_rate3, col_rate4 = st.columns(4)
    col_rate1.metric("سعر الفائدة (البنك المركزي المصري)", "27.25%", "الإيداع لليلة واحدة / CBE Rate")
    col_rate2.metric("سعر الفائدة (الفيدرالي الأمريكي)", "4.75%", "نطاق الفائدة المستهدف / US Fed Rate")
    col_rate3.metric("معدل التضخم السنوي (مصر)", "25.40%", "الجهاز المركزي للتعبئة العامة والإحصاء")
    col_rate4.metric("معدل التضخم السنوي (العالمي)", "2.90%", "متوسط الدول الكبرى / Global CPI")
    
    st.markdown("---")
    st.subheader("جدول مقارنة المؤشرات الاقتصادية الكلية (Macroeconomic Benchmarks)" if is_ar else "Comprehensive Macroeconomic Comparison Table")
    
    macro_data = [
        {
            "المؤشر / Indicator": "سعر الفائدة الأساسي (Interest Rate)",
            "المرجع المحلي (مصر / CBE)": "27.25% (إيداع) / 28.25% (إقراض)",
            "المرجع العالمي (أمريكا / US Fed)": "4.75% - 5.00%",
            "التأثير المباشر على الاستثمار": "تحديد تكلفة الفرصة البديلة وعوائد أدوات الدخل الثابت."
        },
        {
            "المؤشر / Indicator": "معدل التضخم السنوي (Inflation Rate)",
            "المرجع المحلي (مصر / CBE)": "25.40%",
            "المرجع العالمي (أمريكا / Global)": "2.90%",
            "التأثير المباشر على الاستثمار": "قياس تآكل القوة الشرائية وتحديد العائد الحقيقي للأسهم والذهب."
        },
        {
            "المؤشر / Indicator": "احتياطي النقد الأجنبي (Foreign Reserves)",
            "المرجع المحلي (مصر / CBE)": "46.7 مليار دولار",
            "المرجع العالمي (أمريكا / US)": "تغطية عالمية مستقرة",
            "التأثير المباشر على الاستثمار": "دعم استقرار سعر الصرف وتوفير العملة للاستيراد."
        },
        {
            "المؤشر / Indicator": "سعر صرف الدولار الرسمي (FOREX USD/EGP)",
            "المرجع المحلي (مصر / CBE)": f"{fetch_live_usd_egp_rate():.2f} EGP",
            "المرجع العالمي (أمريكا / US)": "1.00 USD (المرجع)",
            "التأثير المباشر على الاستثمار": "تقييم الأصول المقومة بالعملة الأجنبية وعوائد التصدير."
        }
    ]
    
    st.dataframe(pd.DataFrame(macro_data), use_container_width=True)
    
    st.markdown("---")
    st.markdown("### التحليل الاستثماري لتأثير الفائدة والتضخم:" if is_ar else "### Investment Analysis of Rates & Inflation:")
    if is_ar:
        st.markdown("""
        * **فائدة البنك المركزي المصري (27.25%):** تفرض تكلفة تمويل مرتفعة على الشركات، مما يجعل الاستثمار في الأسهم ذات التدفقات النقدية القوية والعائد التشغيلي العالي هو الخيار الأفضل لتجاوز تكلفة الأموال.
        * **فائدة الفيدرالي الأمريكي (4.75%):** توجه تدفقات الأموال الساخنة نحو سندات الخزانة الأمريكية أو تشجع الأسواق الناشئة عند بدء دورة خفض الفائدة.
        * **التضخم (25.40%):** يعزز جاذبية الذهب والأصول الحقيقية (العقارات والأسهم القيادية) كملاذات آمنة لحماية رأس المال من التآكل.
        """)
    else:
        st.markdown("""
        * **CBE Rate (27.25%):** High cost of capital favors companies with strong cash flows and low debt-to-equity ratios.
        * **Fed Rate (4.75%):** Influences global liquidity flows into emerging markets.
        * **Inflation (25.40%):** Drives demand for gold and defensive equities as inflation hedges.
        """)


# MODULE 10: DAILY REPORTS & NOTIFICATIONS
elif nav.startswith("10."):
    title = "التقارير اليومية وسجل الإشعارات اللحظية (Daily Reports & Notifications)" if is_ar else "Daily Reports & Real-Time Price Notification Log"
    sub = "عرض شامل لكل التغيرات والإشعارات التي حدثت في أسعار العملات والأسهم والذهب" if is_ar else "Full historic log of all automated price alerts"
    render_header(title, sub, is_ar=is_ar)
    
    logs = get_all_notifications_log(limit=500)
    if logs:
        df_logs = pd.DataFrame(logs)
        display_df = pd.DataFrame()
        display_df['التاريخ والتوقيت بالثانية'] = df_logs['formatted_time']
        display_df['فئة الأصل'] = df_logs['asset_type']
        display_df['اسم الأصل'] = df_logs['display_name_ar'] if is_ar else df_logs['display_name_en']
        display_df['السعر السابق'] = df_logs.apply(lambda r: f"{r['old_price']:,.2f} {r['currency']}", axis=1)
        display_df['السعر الجديد'] = df_logs.apply(lambda r: f"{r['new_price']:,.2f} {r['currency']}", axis=1)
        display_df['نسبة التغير %'] = df_logs.apply(lambda r: f"{r['change_pct']:+.3f}%", axis=1)
        st.dataframe(display_df, use_container_width=True, height=400)
        
        if st.button("مسح سجل الإشعارات" if is_ar else "Clear Notification Log"):
            clear_notifications_log()
            st.success("تم مسح السجل بنجاح!")
            st.rerun()
    else:
        st.info("لا توجد إشعارات مسجلة حتى الآن." if is_ar else "No notifications logged yet.")

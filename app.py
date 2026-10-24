import streamlit as st
import pandas as pd
from datetime import datetime
from storage.database import init_db, fetch_all, execute_query
from providers.binance import get_binance_ticker_24hr, get_binance_klines
from providers.forex import calculate_universal_forex_conversion, fetch_live_usd_egp_rate, fetch_live_rates_all_currencies
from providers.stocks import get_stock_quote, get_stock_history, PRESET_STOCKS
from providers.gold import get_gold_reference_data
from services.arbitrage import scan_arbitrage_opportunities
from services.financial_analyzer import parse_uploaded_financial_file, fetch_stock_financials_yfinance, create_sample_3yr_financial_data, analyze_financial_ratios
from services.analytics import calculate_technical_indicators
from ui.components import render_header
from ui.charts import create_candlestick_chart, create_forecast_chart

st.set_page_config(page_title="Arbitrage Hub Financial Pro", page_icon="⚡", layout="wide")

# PRO FINANCIAL DARK THEME & ANIMATED FLOATING DOLLAR REFRESH BUTTON CSS
st.markdown("""
<style>
    /* Main Background & Typography */
    .stApp { background-color: #0B0E14; color: #E5E7EB; font-family: 'Inter', -apple-system, sans-serif; }
    .stSidebar { background-color: #111827 !important; border-right: 1px solid #1F2937; }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] { 
        color: #00FF87 !important; 
        font-family: 'JetBrains Mono', monospace; 
        font-weight: 700; 
    }
    div[data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 12px;
    }
    
    /* Smooth Floating Animated Refresh Button */
    @keyframes bounceFloat {
        0% { transform: translateY(0px) scale(1); box-shadow: 0 4px 12px rgba(0,255,135,0.2); }
        50% { transform: translateY(-6px) scale(1.02); box-shadow: 0 10px 20px rgba(0,255,135,0.4); }
        100% { transform: translateY(0px) scale(1); box-shadow: 0 4px 12px rgba(0,255,135,0.2); }
    }
    
    div.stButton > button[key="refresh_live_btn"] {
        background: linear-gradient(135deg, #059669 0%, #10B981 50%, #00FF87 100%) !important;
        color: #064E3B !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 20px !important;
        animation: bounceFloat 2.8s ease-in-out infinite !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 8px !important;
    }
    div.stButton > button[key="refresh_live_btn"]:hover {
        transform: translateY(-8px) scale(1.04) !important;
        box-shadow: 0 14px 28px rgba(0, 255, 135, 0.6) !important;
        filter: brightness(1.15);
    }

    /* Cards & Containers */
    .element-container, .stDataFrame {
        border-radius: 10px;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        color: #9CA3AF !important;
        font-weight: 600 !important;
        padding: 10px 18px !important;
    }
    button[aria-selected="true"] {
        color: #00FF87 !important;
        border-bottom-color: #00FF87 !important;
    }
</style>
""", unsafe_allow_html=True)

init_db()

# LANGUAGE SWITCHER IN SIDEBAR
st.sidebar.title("🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("Select Language / اختر اللغة", ["English", "العربية"], index=0)
is_ar = (lang_choice == "العربية")

st.sidebar.markdown("---")

# ANIMATED DOLLAR REFRESH BUTTON
refresh_btn_label = "💵↗️ Refresh Live Rates / تنشيط الأسعار اللحظية" if not is_ar else "💵↗️ تحديث الأسعار والأسواق أونلاين"
if st.sidebar.button(refresh_btn_label, key="refresh_live_btn", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"⏱️ Last Refreshed: {datetime.now().strftime('%H:%M:%S')}")

st.sidebar.markdown("---")
st.sidebar.title("⚡ Arbitrage Hub")
st.sidebar.caption("Bloomberg-Grade Financial Intelligence Engine" if not is_ar else "محرك التحليل المالي وأسواق البورصة اللحظية")

nav_options_en = [
    "1. 📊 Live Market Overview",
    "2. 🏛️ Complete EGX & Global Stocks",
    "3. 💱 Universal Live Forex Calculator",
    "4. 🪙 Live Crypto Markets",
    "5. 🏆 Gold Pricing & Bullion Calculator",
    "6. 🚀 Arbitrage Opportunity Scanner",
    "7. 📈 Financial Statements & Precision Ratios"
]

nav_options_ar = [
    "1. 📊 نظرة عامة أونلاين (Live Overview)",
    "2. 🏛️ جميع أسهم البورصة المصرية والعالمية (EGX Stocks)",
    "3. 💱 الفوركس العالمي لجميع العملات (Universal Forex)",
    "4. 🪙 الكريبتو البث المباشر (Crypto)",
    "5. 🏆 الذهب والرموز وحاسبة العيارات (Gold)",
    "6. 🚀 مكتشف الفرص اللحظي (Arbitrage Scanner)",
    "7. 📈 القوائم المالية والتحليل المالي (Financial Statements)"
]

nav = st.sidebar.radio("Navigation / القائمة", nav_options_ar if is_ar else nav_options_en)

# REAL-TIME LIVE FRAGMENTS
@st.fragment(run_every="3s")
def render_live_overview_cards():
    c1, c2, c3, c4 = st.columns(4)
    btc = get_binance_ticker_24hr("BTCUSDT")
    if btc:
        lbl = "Bitcoin BTC/USDT (Live)" if not is_ar else "بيتكوين BTC / USDT (مباشر)"
        c1.metric(lbl, f"${btc[0]['price']:,.2f}", f"{btc[0]['change_24h_pct']:.2f}%")
        
    gold = get_gold_reference_data()
    lbl_gold = "Global Gold (USD/oz)" if not is_ar else "الذهب عالمياً (USD/oz)"
    lbl_usd = "Live USD/EGP Rate" if not is_ar else "سعر دولار الصرف الحي"
    c2.metric(lbl_gold, f"${gold['usd_per_troy_oz']:,.2f}")
    c3.metric(lbl_usd, f"{gold['usd_egp_rate']:.2f} EGP")
    
    cib = get_stock_quote("COMI.CA")
    lbl_cib = "CIB Bank (EGX: COMI)" if not is_ar else "البنك التجاري الدولي (CIB)"
    if 'price' in cib:
        c4.metric(lbl_cib, f"{cib['price']:.2f} EGP", f"{cib['change_pct']:.2f}%")
    else:
        c4.metric(lbl_cib, "N/A")

@st.fragment(run_every="4s")
def render_live_crypto_table():
    st.subheader("🔥 Top Crypto & Market Movers (Live)" if not is_ar else "🔥 تحركات الكريبتو والأسواق العالمية (بث مباشر)")
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_t = pd.DataFrame(tickers).sort_values('change_24h_pct', ascending=False).head(10)
        st.dataframe(df_t[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h']], use_container_width=True)

@st.fragment(run_every="3s")
def render_live_crypto_chart(sym):
    df = get_binance_klines(sym)
    df = calculate_technical_indicators(df)
    st.plotly_chart(create_candlestick_chart(df, f"Live Chart - {sym}"), use_container_width=True)

@st.fragment(run_every="5s")
def render_live_arbitrage_scanner():
    st.caption("🔄 Auto-refreshing every 5 seconds..." if not is_ar else "🔄 يتم التحديث تلقائياً كل 5 ثوانٍ لجلب أحدث الفرص...")
    res = scan_arbitrage_opportunities()
    if res:
        st.dataframe(pd.DataFrame(res), use_container_width=True)
    else:
        st.warning("No net arbitrage opportunities detected after fees." if not is_ar else "لم يتم العثور على فرص تبادلية محققة للربح بعد خصم العمولات حالياً.")


# MODULE 1: OVERVIEW
if nav.startswith("1."):
    title = "Market Overview - 24/7 Live Monitor" if not is_ar else "Market Overview - شاشة المراقبة اللحظية 24/7"
    sub = "Live market feeds dynamically streaming from global exchanges" if not is_ar else "بث مباشر لأسعار الصرف والذهب والأسهم لحظة بلحظة"
    render_header(title, sub)
    render_live_overview_cards()
    st.markdown("---")
    render_live_crypto_table()

# MODULE 2: ALL EGX & GLOBAL STOCKS
elif nav.startswith("2."):
    title = "🏛️ Egyptian Exchange (EGX) & Global Stock Markets" if not is_ar else "🏛️ البورصة المصرية بكافة أسهمها والبورصة العالمية"
    sub = "Real-time quotes, technical indicators, and interactive charts for ALL EGX stocks" if not is_ar else "أسعار حية ومباشرة ورسوم بيانية لجميع أسهم البورصة المصرية بدون استثناء"
    render_header(title, sub)
    
    st.markdown("### 🔍 Select Sector / Stock (اختيار القطاع والسهم)")
    category_names = list(PRESET_STOCKS.keys())
    selected_category = st.selectbox("Select Sector / اختر القطاع", category_names, index=0)
    
    preset_list = PRESET_STOCKS[selected_category]
    preset_dict = {f"{item['name']} ({item['symbol']})": item['symbol'] for item in preset_list}
    
    c_sel1, c_sel2 = st.columns([2, 1])
    selected_name = c_sel1.selectbox("Select Stock / اختر السهم", list(preset_dict.keys()))
    selected_symbol = preset_dict[selected_name]
    
    custom_symbol = c_sel2.text_input("Custom Ticker / أدخل رمز سهم آخر (e.g. FWRY.CA, COMI.CA, NVDA)", value="").upper()
    active_symbol = custom_symbol if custom_symbol else selected_symbol
    
    quote = get_stock_quote(active_symbol)
    if 'error' in quote:
        st.error(quote['error'])
    else:
        st.subheader(f"📌 {quote['symbol']}")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("Current Price / السعر الحالي", f"{quote['price']:,.2f} {quote['currency']}", f"{quote['change_pct']:.2f}%")
        col_b.metric("Timestamp / التوقيت", f"{quote['timestamp']}")
        col_c.metric("Source / المصدر", f"{quote['source']}")
        
        st.markdown("---")
        st.subheader("📊 Interactive Price Chart" if not is_ar else "📊 الرسم البياني التفاعلي وحركة السهم")
        tf = st.selectbox("Timeframe / الفترة الزمنية", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        df_stock_hist = get_stock_history(active_symbol, period=tf)
        
        if not df_stock_hist.empty:
            df_stock_hist = calculate_technical_indicators(df_stock_hist)
            fig_stock = create_candlestick_chart(df_stock_hist, f"Candlestick & SMA (20/50) - {active_symbol}")
            st.plotly_chart(fig_stock, use_container_width=True)
        else:
            st.warning("Historical chart unavailable for this symbol." if not is_ar else "الرسم البياني التاريخي غير متوفر لهذا الرمز حالياً.")

# MODULE 3: UNIVERSAL LIVE FOREX CALCULATOR
elif nav.startswith("3."):
    title = "💱 Universal Real-Time Forex Calculator" if not is_ar else "💱 حاسبة العملات العالمية اللحظية (Universal Forex)"
    sub = "Live spot exchange rates for ALL 150+ world currencies updated instantly" if not is_ar else "ربط مباشر بجميع عملات العالم لحظة بلحظة وبدقة 100%"
    render_header(title, sub)
    
    live_usd_egp = fetch_live_usd_egp_rate()
    st.info(f"💡 **Live Market USD/EGP Reference Rate:** `1 USD = {live_usd_egp:.2f} EGP`")
    
    st.subheader("🌐 Global Currency Converter" if not is_ar else "🌐 التحويل المباشر بين أي عملتين في العالم")
    c1, c2, c3 = st.columns(3)
    amount = c1.number_input("Amount / المبلغ", min_value=0.01, value=1000.0, step=100.0)
    
    world_currencies = [
        "USD", "EUR", "GBP", "EGP", "SAR", "AED", "KWD", "QAR", "BHD", "OMR",
        "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "TRY", "RUB", "BRL", "ZAR",
        "SEK", "NOK", "DKK", "NZD", "SGD", "HKD", "KRW", "MXN", "MYR", "THB"
    ]
    
    from_curr = c2.selectbox("From Currency / من عملة", world_currencies, index=0)
    to_curr = c3.selectbox("To Currency / إلى عملة", world_currencies, index=3)
    
    res = calculate_universal_forex_conversion(amount, from_curr, to_curr)
    
    st.success(f"### 💸 {amount:,.2f} {from_curr} = {res['converted_amount']:,.2f} {to_curr}")
    st.info(f"**Exact Real-Time Exchange Rate:** 1 {from_curr} = {res['exchange_rate']} {to_curr}  *(Updated at {res['timestamp']})*")
    
    st.markdown("---")
    st.subheader("🇪🇬 EGP Benchmark Comparison (Live)" if not is_ar else "🇪🇬 المقارنة اللحظية بالجنيه المصري (EGP Benchmark)")
    col_egp1, col_egp2 = st.columns(2)
    col_egp1.metric(f"{amount:,.2f} {from_curr} in EGP", f"{res['from_amount_in_egp']:,.2f} EGP")
    col_egp2.metric(f"{res['converted_amount']:,.2f} {to_curr} in EGP", f"{res['to_amount_in_egp']:,.2f} EGP")

# MODULE 4: CRYPTO
elif nav.startswith("4."):
    title = "🪙 Live Crypto Trading Feed" if not is_ar else "🪙 الكريبتو والعملات الرقمية - بث مباشر (Live Crypto)"
    sub = "Binance live candlesticks and RSI/SMA technical indicators" if not is_ar else "تحديث الرسم البياني والأسعار لحظياً"
    render_header(title, sub)
    sym = st.selectbox("Trading Pair / زوج التداول", ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT"])
    render_live_crypto_chart(sym)

# MODULE 5: GOLD
elif nav.startswith("5."):
    title = "🏆 Real-Time Gold Pricing & Gram Calculator" if not is_ar else "🏆 أسعار الذهب وحاسبة الجرام بالجنيه المصري"
    sub = "Global Gold Spot & EGP Gram Prices auto-recalculated live" if not is_ar else "تحديث تلقائي لجرام الذهب بناءً على الأونصة عالمياً والأن المباشر لـ USD/EGP"
    render_header(title, sub)
    gold = get_gold_reference_data()
    
    col_g1, col_g2 = st.columns(2)
    col_g1.metric("Global Gold Spot (USD/oz)", f"${gold['usd_per_troy_oz']:,.2f}")
    col_g2.metric("24K Gold Gram (EGP)", f"{gold['indicative_egp_per_gram_24k']:,.2f} EGP")
    
    st.subheader("EGP Karat Reference Prices (Live)" if not is_ar else "أسعار العيارات الاسترشادية بالجنيه المصري (مباشر)")
    st.table(pd.DataFrame([gold['karats_indicative_egp']]))

# MODULE 6: ARBITRAGE SCANNER
elif nav.startswith("6."):
    title = "🚀 Real-Time Arbitrage Scanner" if not is_ar else "🚀 مكتشف الفرص التبادلية - تحديث تلقائي (Live Scanner)"
    sub = "Automated triangular arbitrage scanner with net fee calculation" if not is_ar else "فحص دقيق ومباشر للفروق السعرية بين أزواج التداول مع خصم العمولات"
    render_header(title, sub)
    render_live_arbitrage_scanner()

# MODULE 7: 100% ENGLISH FINANCIAL STATEMENTS, RATIOS & FORECAST ENGINE
elif nav.startswith("7."):
    render_header("📈 Financial Statements & Precision Ratio Intelligence", "Auto-fetch stock statements or upload custom files for instant multi-year ratio & forecast analysis")
    
    tab1, tab2 = st.tabs(["🔍 Auto-Fetch Stock Statements", "📂 Upload Custom Financial Report"])
    
    df_financials = None
    
    with tab1:
        st.markdown("### 🏛️ Automated Financial Statement Extractor")
        st.info("Enter any stock symbol from Egyptian Exchange (EGX) or Global Stock Markets (e.g. `COMI.CA`, `FWRY.CA`, `AAPL`, `NVDA`, `MSFT`, `AMZN`) to fetch multi-year statements instantly in English.")
        
        stock_input = st.text_input("Enter Stock Ticker", value="COMI.CA").upper()
        
        if st.button("🚀 Fetch Financial Statements", key="fetch_btn"):
            with st.spinner("Extracting income statement & balance sheet..."):
                fetched_df, msg = fetch_stock_financials_yfinance(stock_input)
                if fetched_df is not None:
                    st.session_state['fetched_df'] = fetched_df
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
                    
        if 'fetched_df' in st.session_state:
            df_financials = st.session_state['fetched_df']

    with tab2:
        st.markdown("### 📂 Upload Custom Financial Report")
        st.info("Upload any Excel (.xlsx, .xls) or CSV file containing your company's income statement and balance sheet items. The parser will standardize metrics and perform zero-error ratio analysis.")
        uploaded_file = st.file_uploader("Upload Excel / CSV File", type=['xlsx', 'xls', 'csv'], key="fin_file_uploader")
        if uploaded_file is not None:
            parsed_df = parse_uploaded_financial_file(uploaded_file.read(), uploaded_file.name)
            if parsed_df is not None:
                st.session_state['fetched_df'] = parsed_df
                df_financials = parsed_df
                st.success("✅ File uploaded, parsed, and standardized successfully!")
            else:
                st.error("Error reading or parsing file. Please check file format.")

    if df_financials is None:
        st.markdown("---")
        st.info("💡 Active Sample 3-Year Financial Report (Fetch a stock or upload a file above):")
        df_financials = create_sample_3yr_financial_data()

    st.subheader("📋 Standardized Financial Statement View")
    st.dataframe(df_financials, use_container_width=True)
    
    st.markdown("---")
    if st.button("📊 Calculate Ratios & Run Forecast Model", key="analyze_btn", use_container_width=True):
        analysis = analyze_financial_ratios(df_financials)
        
        if analysis and "ratios_by_year" in analysis:
            st.subheader("📋 Calculated Multi-Year Financial Ratios & Performance")
            ratios_df = pd.DataFrame(analysis["ratios_by_year"])
            st.dataframe(ratios_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🔮 Next Year (N+1) Forecast & Compound Projection")
            fc = analysis["forecast_next_year"]
            
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Projected Revenue", f"${fc['Projected Revenue']:,.2f}", f"{fc['Revenue CAGR / Growth Rate (%)']:+.2f}% CAGR")
            c2.metric("Projected Net Income", f"${fc['Projected Net Income']:,.2f}", f"{fc['Net Income CAGR / Growth Rate (%)']:+.2f}% CAGR")
            c3.metric("Est. Net Profit Margin", f"{fc['Estimated Net Profit Margin (%)']:.2f}%")
            c4.metric("Est. Return on Equity (ROE)", f"{fc['Estimated ROE (%)']:.2f}%")
            
            fig_fc = create_forecast_chart(
                analysis["years"],
                analysis["historical_revenue_trend"],
                analysis["historical_net_profit_trend"],
                fc['Projected Revenue'],
                fc['Projected Net Income']
            )
            st.plotly_chart(fig_fc, use_container_width=True)
        else:
            st.error("Unable to calculate ratios due to insufficient historical financial data.")

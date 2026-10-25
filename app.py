import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from storage.database import init_db, fetch_all, execute_query
from providers.binance import get_binance_ticker_24hr, get_binance_klines
from providers.forex import calculate_universal_forex_conversion, fetch_live_usd_egp_rate, fetch_live_rates_all_currencies
from providers.stocks import get_stock_quote, get_stock_history, search_stocks, EGX30_STOCKS, EGX70_EGX50_STOCKS, GLOBAL_TECH_STOCKS, ALL_STOCKS_LIST
from providers.gold import get_gold_reference_data
from services.arbitrage import scan_arbitrage_opportunities
from services.financial_analyzer import parse_uploaded_financial_file, fetch_stock_financials_yfinance, create_sample_3yr_financial_data, analyze_financial_ratios
from services.analytics import calculate_technical_indicators
from ui.components import render_header
from ui.charts import create_candlestick_chart, create_forecast_chart

st.set_page_config(page_title="Arbitrage Hub - Binance Dark Terminal", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #EAECEF; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stSidebar { background-color: #181A20 !important; border-right: 1px solid #2B313A; }
    h1, h2, h3 { color: #F0B90B !important; font-weight: 700; }
    div[data-testid="stMetricValue"] { 
        color: #F0B90B !important; 
        font-family: 'JetBrains Mono', monospace; 
        font-weight: 700; 
    }
    div[data-testid="stMetricLabel"] {
        color: #848E9C !important;
        font-weight: 600;
        text-transform: uppercase;
        font-size: 11px;
    }
    @keyframes bounceFloat {
        0% { transform: translateY(0px) scale(1); box-shadow: 0 4px 12px rgba(240, 185, 11, 0.2); }
        50% { transform: translateY(-5px) scale(1.02); box-shadow: 0 10px 20px rgba(240, 185, 11, 0.4); }
        100% { transform: translateY(0px) scale(1); box-shadow: 0 4px 12px rgba(240, 185, 11, 0.2); }
    }
    div.stButton > button[key="refresh_live_btn"] {
        background: linear-gradient(135deg, #F0B90B 0%, #F8D33A 100%) !important;
        color: #0B0E11 !important;
        font-weight: 800 !important;
        font-size: 14px !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 10px 18px !important;
        animation: bounceFloat 2.8s ease-in-out infinite !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    input, select, div[data-baseweb="select"] {
        background-color: #2B313A !important;
        color: #EAECEF !important;
        border-radius: 4px !important;
        border: 1px solid #474D57 !important;
    }
    .stDataFrame { border: 1px solid #2B313A; border-radius: 4px; }
    button[data-baseweb="tab"] { color: #848E9C !important; font-weight: 600 !important; }
    button[aria-selected="true"] { color: #F0B90B !important; border-bottom-color: #F0B90B !important; }
</style>
""", unsafe_allow_html=True)

init_db()

st.sidebar.title("🌐 Language")
lang_choice = st.sidebar.selectbox("Select Display Language", ["English", "العربية"], index=0)
is_ar = (lang_choice == "العربية")

st.sidebar.markdown("---")
refresh_btn_label = "💵↗️ Refresh Live Rates" if not is_ar else "💵↗️ تحديث الأسعار والأسواق أونلاين"
if st.sidebar.button(refresh_btn_label, key="refresh_live_btn", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f"⏱️ Last Refreshed: {(datetime.now(timezone.utc) + timedelta(hours=3)).strftime('%I:%M:%S %p (توقيت القاهرة)')}")
st.sidebar.markdown("---")
st.sidebar.title("⚡ Arbitrage Hub")
st.sidebar.caption("Binance-Grade Financial Intelligence Terminal" if not is_ar else "محرك التحليل المالي وأسواق البورصة اللحظية")

nav_options_en = [
    "1. 📊 Live Market Overview",
    "2. 🏛️ EGX Market Indices & Stocks",
    "3. 💱 Universal Live Forex Calculator",
    "4. 🪙 Live Crypto Trading Feed",
    "5. 🏆 Gold Pricing & Sagha Premium Calculator",
    "6. 🚀 Real-Time Arbitrage Scanner",
    "7. 📈 Financial Statements & Precision Ratios"
]

nav_options_ar = [
    "1. 📊 نظرة عامة أونلاين (Live Overview)",
    "2. 🏛️ مؤشرات وأسهم البورصة المصرية (EGX Indices)",
    "3. 💱 الفوركس العالمي لجميع العملات (Universal Forex)",
    "4. 🪙 الكريبتو البث المباشر (Crypto)",
    "5. 🏆 الذهب العالمي وحاسبة سوق الصاغة (Gold & Sagha)",
    "6. 🚀 مكتشف الفرص اللحظي (Arbitrage Scanner)",
    "7. 📈 القوائم المالية والتحليل المالي (Financial Statements)"
]

nav = st.sidebar.radio("Navigation", nav_options_ar if is_ar else nav_options_en)

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
    st.subheader("🔥 Top Crypto Market Movers (Binance Feed)" if not is_ar else "🔥 تحركات الكريبتو والأسواق العالمية (بث مباشر)")
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
    sub = "Live market feeds streaming from global exchanges" if not is_ar else "بث مباشر لأسعار الصرف والذهب والأسهم لحظة بلحظة"
    render_header(title, sub)
    render_live_overview_cards()
    st.markdown("---")
    render_live_crypto_table()

# MODULE 2: EGX MARKET INDICES & STOCKS (EGX30, EGX70, GLOBAL TECH + UNIFIED SEARCH)
elif nav.startswith("2."):
    title = "🏛️ EGX Market Indices & Stocks Terminal" if not is_ar else "🏛️ مؤشرات وأسهم البورصة المصرية والعالمية"
    sub = "Explore EGX30, EGX70/50, and Global Tech stocks with categorized tabs and universal search" if not is_ar else "تصفح مؤشرات EGX30 و EGX70 والأسهم العالمية مع تبويب دقيق وبحث شامل بالاسم أو الكود"
    render_header(title, sub)
    
    # Universal Search Bar
    search_query = st.text_input("🔍 Universal Stock Search / ابحث عن أي شركة بالاسم أو الكود", value="", placeholder="e.g. فوري / CIB / طلعت مصطفى / Apple / COMI.CA").strip()
    
    if search_query:
        matched = search_stocks(search_query)
        st.subheader(f"🔎 Search Results for: '{search_query}'" if not is_ar else f"🔎 نتائج البحث عن: '{search_query}'")
        search_options = [f"{s['name_en']} | {s['name_ar']} ({s['symbol']})" for s in matched]
        selected_option = st.selectbox("Select Company / اختر الشركة", search_options, index=0)
        selected_symbol = selected_option.split("(")[-1].replace(")", "").strip()
        
        quote = get_stock_quote(selected_symbol)
        if 'error' in quote:
            st.error(quote['error'])
        else:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("Current Price", f"{quote['price']:,.2f} {quote['currency']}", f"{quote['change_pct']:.2f}%")
            col_b.metric("Timestamp", f"{quote['timestamp']}")
            col_c.metric("Data Feed Source", f"{quote['source']}")
            
            st.markdown("---")
            st.subheader("📊 Interactive Candlestick Chart")
            tf = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
            df_stock_hist = get_stock_history(selected_symbol, period=tf)
            if not df_stock_hist.empty:
                df_stock_hist = calculate_technical_indicators(df_stock_hist)
                fig_stock = create_candlestick_chart(df_stock_hist, f"Candlestick & SMA (20/50) - {selected_symbol}")
                st.plotly_chart(fig_stock, use_container_width=True)
            else:
                st.warning("Historical chart unavailable for this symbol.")
    else:
        # Categorized Indices Tabs
        tab_30, tab_70, tab_global = st.tabs(["📈 EGX 30 Index (الأسهم القيادية)", "📊 EGX 70 / 50 Index (الأسهم المتوسطة)", "🌍 Global Tech Giants"])
        
        def render_index_section(stocks_list, index_name):
            st.markdown(f"### 📋 {index_name} Components & Live Quotes")
            options = [f"{s['name_en']} | {s['name_ar']} ({s['symbol']})" for s in stocks_list]
            sel = st.selectbox(f"Select company in {index_name} / اختر شركة", options, key=f"sel_{index_name}")
            sym = sel.split("(")[-1].replace(")", "").strip()
            
            q = get_stock_quote(sym)
            if 'error' in q:
                st.error(q['error'])
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Current Price", f"{q['price']:,.2f} {q['currency']}", f"{q['change_pct']:.2f}%")
                c2.metric("Timestamp", f"{q['timestamp']}")
                c3.metric("Data Feed Source", f"{q['source']}")
                
                st.markdown("---")
                df_hist = get_stock_history(sym, period="1y")
                if not df_hist.empty:
                    df_hist = calculate_technical_indicators(df_hist)
                    st.plotly_chart(create_candlestick_chart(df_hist, f"Candlestick Chart - {sym}"), use_container_width=True)

        with tab_30:
            render_index_section(EGX30_STOCKS, "EGX 30")
        with tab_70:
            render_index_section(EGX70_EGX50_STOCKS, "EGX 70 & EGX 50")
        with tab_global:
            render_index_section(GLOBAL_TECH_STOCKS, "Global Tech Giants")

# MODULE 3: UNIVERSAL LIVE FOREX CALCULATOR
elif nav.startswith("3."):
    title = "💱 Universal Real-Time Forex Calculator" if not is_ar else "💱 حاسبة العملات العالمية اللحظية (Universal Forex)"
    sub = "Live spot exchange rates for ALL 150+ world currencies" if not is_ar else "ربط مباشر بجميع عملات العالم لحظة بلحظة وبدقة 100%"
    render_header(title, sub)
    
    live_usd_egp = fetch_live_usd_egp_rate()
    st.info(f"💡 **Live Market USD/EGP Reference Rate:** `1 USD = {live_usd_egp:.2f} EGP` *(Official Interbank Feed)*")
    
    st.subheader("🌐 Global Currency Converter")
    c1, c2, c3 = st.columns(3)
    amount = c1.number_input("Amount", min_value=0.01, value=1000.0, step=100.0)
    
    world_currencies = [
        "USD", "EUR", "GBP", "EGP", "SAR", "AED", "KWD", "QAR", "BHD", "OMR",
        "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "TRY", "RUB", "BRL", "ZAR",
        "SEK", "NOK", "DKK", "NZD", "SGD", "HKD", "KRW", "MXN", "MYR", "THB"
    ]
    
    from_curr = c2.selectbox("From Currency", world_currencies, index=0)
    to_curr = c3.selectbox("To Currency", world_currencies, index=3)
    
    res = calculate_universal_forex_conversion(amount, from_curr, to_curr)
    
    st.success(f"### 💸 {amount:,.2f} {from_curr} = {res['converted_amount']:,.2f} {to_curr}")
    st.info(f"**Exact Real-Time Exchange Rate:** 1 {from_curr} = {res['exchange_rate']} {to_curr}  *(Updated at {res['timestamp']})*")
    
    st.markdown("---")
    st.subheader("🇪🇬 EGP Benchmark Comparison")
    col_egp1, col_egp2 = st.columns(2)
    col_egp1.metric(f"{amount:,.2f} {from_curr} in EGP", f"{res['from_amount_in_egp']:,.2f} EGP")
    col_egp2.metric(f"{res['converted_amount']:,.2f} {to_curr} in EGP", f"{res['to_amount_in_egp']:,.2f} EGP")

# MODULE 4: CRYPTO
elif nav.startswith("4."):
    title = "🪙 Live Crypto Trading Feed & Binance Market Terminal" if not is_ar else "🪙 أسواق العملات الرقمية والريال تاييم - بث مباشر من باينانس"
    sub = "Real-time spot prices, 24h volume, candlestick charts, and technical indicators (RSI & SMAs)" if not is_ar else "أسعار سبوت فورية، حجم تداول 24 ساعة، رسوم شمعية ومؤشرات فنية حية مباشرة من Binance"
    render_header(title, sub)
    
    st.markdown("### 🔥 All Active Binance USDT Spot Markets" if not is_ar else "🔥 جميع أسواق سبوت USDT النشطة على منصة باينانس")
    
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_crypto = pd.DataFrame(tickers)
        df_crypto = df_crypto[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'quote_volume_24h']]
        df_crypto.columns = ['Trading Pair', 'Last Price ($)', '24h Change (%)', '24h High ($)', '24h Low ($)', '24h Volume', '24h Turnover (USDT)']
        
        crypto_search = st.text_input("🔍 Filter Crypto Pair / تصفية عملة رقمية", value="", placeholder="e.g. BTC, ETH, SOL, XRP").strip().upper()
        if crypto_search:
            df_crypto = df_crypto[df_crypto['Trading Pair'].str.contains(crypto_search)]
            
        st.dataframe(df_crypto.sort_values(by='24h Turnover (USDT)', ascending=False), use_container_width=True, height=350)
    else:
        st.warning("Unable to fetch live Binance spot data at this moment. Please check network connection.")

    st.markdown("---")
    st.subheader("📊 Advanced Candlestick Chart & Technical Indicators (Binance Feed)" if not is_ar else "📊 الرسم الشمعي المتقدم والمؤشرات الفنية (بث مباشر من باينانس)")
    
    col_c1, col_c2 = st.columns([1, 2])
    crypto_symbols_list = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "DOTUSDT"]
    selected_crypto_sym = col_c1.selectbox("Select Trading Pair / اختر زوج التداول", crypto_symbols_list, index=0)
    selected_interval = col_c2.selectbox("Select Timeframe / اختر الإطار الزمني", ["1h", "4h", "1d", "1w"], index=2)
    
    interval_map = {"1h": "1h", "4h": "4h", "1d": "1d", "1w": "1w"}
    df_klines = get_binance_klines(selected_crypto_sym, interval=interval_map.get(selected_interval, "1d"))
    if not df_klines.empty:
        df_klines = calculate_technical_indicators(df_klines)
        single_ticker = get_binance_ticker_24hr(selected_crypto_sym)
        if single_ticker:
            st.markdown(f"### **{selected_crypto_sym}** — Live Price: **${single_ticker[0]['price']:,.4f}** ({single_ticker[0]['change_24h_pct']:+.2f}%)")
        fig_crypto = create_candlestick_chart(df_klines, f"Binance Live Spot - {selected_crypto_sym} ({selected_interval})")
        st.plotly_chart(fig_crypto, use_container_width=True)
    else:
        st.warning(f"Historical klines unavailable for {selected_crypto_sym}.")

# MODULE 5: GOLD & SAGHA PREMIUM CALCULATOR
elif nav.startswith("5."):
    title = "🏆 Real-Time Gold Pricing & Sagha Premium Calculator" if not is_ar else "🏆 الذهب العالمي وحاسبة أسعار سوق الصاغة المصرية"
    sub = "Global Gold Spot linked to USD/EGP with custom Sagha local market premium adjustment" if not is_ar else "الربط بين الأونصة عالمياً والأن المباشر لـ USD/EGP مع حاسبة فرق الصاغة المحلي"
    render_header(title, sub)
    
    st.sidebar.markdown("### 🏛️ Egyptian Sagha Adjustment")
    sagha_premium = st.sidebar.slider("Sagha Local Premium %", min_value=0.0, max_value=25.0, value=0.0, step=0.5, help="Adjusts local Egyptian market premium over spot.")
    
    gold = get_gold_reference_data(sagha_premium_pct=sagha_premium)
    
    col_g1, col_g2 = st.columns(2)
    col_g1.metric("Global Gold Spot (USD/oz)", f"${gold['usd_per_troy_oz']:,.2f}")
    col_g2.metric("24K Gold Gram (EGP)", f"{gold['indicative_egp_per_gram_24k']:,.2f} EGP", f"+{sagha_premium}% Sagha Premium" if sagha_premium > 0 else "Official Live Spot")
    
    st.subheader("EGP Karat Reference Prices")
    st.table(pd.DataFrame([gold['karats_indicative_egp']]))

# MODULE 6: ARBITRAGE SCANNER
elif nav.startswith("6."):
    title = "🚀 Real-Time Arbitrage Scanner" if not is_ar else "🚀 مكتشف الفرص التبادلية - تحديث تلقائي (Live Scanner)"
    sub = "Automated triangular arbitrage scanner with net fee calculation" if not is_ar else "فحص دقيق ومباشر للفروق السعرية بين أزواج التداول مع خصم العمولات"
    render_header(title, sub)
    render_live_arbitrage_scanner()

# MODULE 7: FINANCIAL STATEMENTS, RATIOS & FORECAST ENGINE
elif nav.startswith("7."):
    render_header("📈 Financial Statements & Precision Ratio Intelligence", "Auto-fetch stock statements or upload custom files for instant multi-year ratio & forecast analysis")
    
    tab1, tab2 = st.tabs(["🔍 Auto-Fetch Stock Statements", "📂 Upload Custom Financial Report"])
    df_financials = None
    
    with tab1:
        st.markdown("### 🏛️ Automated Financial Statement Extractor")
        st.info("Enter any stock symbol from Egyptian Exchange (EGX) or Global Stock Markets (e.g. `COMI.CA`, `FWRY.CA`, `AAPL`, `NVDA`, `MSFT`, `AMZN`) to fetch multi-year statements instantly.")
        
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

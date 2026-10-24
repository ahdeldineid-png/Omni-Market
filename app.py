import streamlit as st
import pandas as pd
from storage.database import init_db, fetch_all, execute_query
from providers.binance import get_binance_ticker_24hr, get_binance_klines
from providers.forex import get_latest_forex_rates, calculate_forex_conversion
from providers.stocks import get_stock_quote, get_stock_history, PRESET_STOCKS
from providers.gold import get_gold_reference_data
from services.arbitrage import scan_arbitrage_opportunities
from services.financial_analyzer import parse_uploaded_financial_file, fetch_stock_financials_yfinance, create_sample_3yr_financial_data, analyze_financial_ratios
from services.analytics import calculate_technical_indicators
from ui.components import render_header
from ui.charts import create_candlestick_chart, create_forecast_chart

st.set_page_config(page_title="Arbitrage Hub & Financial Analyzer", page_icon="⚡", layout="wide")

# Modern Styling
st.markdown("""
<style>
    .stApp { background-color: #131722; color: #D1D4DC; }
    .stSidebar { background-color: #1E222D !important; }
    div[data-testid="stMetricValue"] { color: #00E676 !important; font-family: monospace; }
</style>
""", unsafe_allow_html=True)

init_db()

# LANGUAGE SWITCHER IN SIDEBAR
st.sidebar.title("🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("Select Language / اختر اللغة", ["English", "العربية"], index=0)
is_ar = (lang_choice == "العربية")

st.sidebar.markdown("---")
st.sidebar.title("⚡ Arbitrage Hub")
st.sidebar.caption("Financial Markets & Automated Statement Intelligence" if not is_ar else "المنصة الشاملة للأسواق المالية والتحليل المالي")

nav_options_en = [
    "1. 📊 Live Overview",
    "2. 🏛️ Egyptian & Global Stocks",
    "3. 💱 Forex & Financial Calculator",
    "4. 🪙 Live Crypto Markets",
    "5. 🏆 Gold Pricing & Bullion",
    "6. 🚀 Arbitrage Scanner",
    "7. 📈 Financial Statements & Ratio Intelligence"
]

nav_options_ar = [
    "1. 📊 نظرة عامة لحظية (Overview)",
    "2. 🏛️ البورصة المصرية والعالمية (Stocks)",
    "3. 💱 الفوركس والحاسبة المالية (Forex)",
    "4. 🪙 الكريبتو البث اللحظي (Crypto)",
    "5. 🏆 الذهب والرموز (Gold)",
    "6. 🚀 مكتشف الفرص اللحظي (Arbitrage Scanner)",
    "7. 📈 القوائم المالية والتوقعات الآلية (Financial Reports)"
]

nav = st.sidebar.radio("Navigation / القائمة", nav_options_ar if is_ar else nav_options_en)

# FRAGMENTS FOR REAL-TIME STREAMING
@st.fragment(run_every="3s")
def render_live_overview_cards():
    c1, c2, c3, c4 = st.columns(4)
    btc = get_binance_ticker_24hr("BTCUSDT")
    if btc:
        lbl = "Bitcoin BTC/USDT (Live)" if not is_ar else "بيتكوين BTC / USDT (مباشر)"
        c1.metric(lbl, f"${btc[0]['price']:,.2f}", f"{btc[0]['change_24h_pct']:.2f}%")
        
    gold = get_gold_reference_data()
    lbl_gold = "Global Gold (USD/oz)" if not is_ar else "الذهب عالمياً (USD/oz)"
    lbl_usd = "USD / EGP Benchmark" if not is_ar else "دولار الصرف الاسترشادي"
    c2.metric(lbl_gold, f"${gold['usd_per_troy_oz']:,.2f}")
    c3.metric(lbl_usd, f"{gold['usd_egp_rate']:.2f} EGP")
    
    cib = get_stock_quote("COMI.CA")
    lbl_cib = "Commercial International Bank (CIB)" if not is_ar else "البنك التجاري الدولي (CIB)"
    if 'price' in cib:
        c4.metric(lbl_cib, f"{cib['price']:.2f} EGP", f"{cib['change_pct']:.2f}%")
    else:
        c4.metric(lbl_cib, "N/A")

@st.fragment(run_every="4s")
def render_live_crypto_table():
    st.subheader("🔥 Top Crypto & Global Movers (Live)" if not is_ar else "🔥 أبرز تحركات الكريبتو والأسواق العالمية (مباشر)")
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
    sub = "Real-time streaming prices updated every 3s" if not is_ar else "تحديث مباشر للسعر كل 3 ثوانٍ دون الحاجة لإعادة تحميل الصفحة"
    render_header(title, sub)
    render_live_overview_cards()
    st.markdown("---")
    render_live_crypto_table()

# MODULE 2: STOCKS
elif nav.startswith("2."):
    title = "🏛️ Egyptian & Global Stock Markets" if not is_ar else "🏛️ البورصة المصرية والعالمية (EGX & Global Stocks)"
    sub = "Interactive Thndr/Binance style interface with technical indicators" if not is_ar else "واجهة تفاعلية ديناميكية بأسلوب Thndr / Binance مع الرسوم البيانية"
    render_header(title, sub)
    
    market_options = ["Egyptian Exchange (EGX)", "Global Markets"] if not is_ar else ["البورصة المصرية (EGX)", "البورصة العالمية (Global Markets)"]
    market_choice = st.radio("Select Market / اختر السوق", market_options, horizontal=True)
    
    preset_key = "EGX (البورصة المصرية)" if ("Egyptian" in market_choice or "المصرية" in market_choice) else "Global Markets (البورصة العالمية)"
    preset_list = PRESET_STOCKS[preset_key]
    preset_dict = {item['name'] + f" ({item['symbol']})": item['symbol'] for item in preset_list}
    
    selected_name = st.selectbox("Select Stock / اختر السهم", list(preset_dict.keys()))
    selected_symbol = preset_dict[selected_name]
    custom_symbol = st.text_input("Custom Ticker / رمز مخصص (e.g. COMI.CA, FWRY.CA, NVDA, AAPL)", value="").upper()
    active_symbol = custom_symbol if custom_symbol else selected_symbol
    
    quote = get_stock_quote(active_symbol)
    if 'error' in quote:
        st.error(quote['error'])
    else:
        st.subheader(f"📌 {quote['name']} [{quote['symbol']}]")
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Current Price / السعر", f"{quote['price']:,.2f} {quote['currency']}", f"{quote['change_pct']:.2f}%")
        col_b.metric("P/E Ratio / مكرر الربحية", f"{quote['pe_ratio']}")
        col_c.metric("Market Cap / القيمة السوقية", f"{quote['market_cap']:,}" if isinstance(quote['market_cap'], (int, float)) else "N/A")
        col_d.metric("Sector / القطاع", f"{quote['sector']}")
        
        st.markdown("---")
        st.subheader("📊 Interactive Price Chart" if not is_ar else "📊 الرسم البياني التفاعلي وحركة السهم الديناميكية")
        tf = st.selectbox("Timeframe / الفترة الزمنية", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
        df_stock_hist = get_stock_history(active_symbol, period=tf)
        
        if not df_stock_hist.empty:
            df_stock_hist = calculate_technical_indicators(df_stock_hist)
            fig_stock = create_candlestick_chart(df_stock_hist, f"Candlestick & SMA (20/50) - {active_symbol}")
            st.plotly_chart(fig_stock, use_container_width=True)
        else:
            st.warning("Historical chart unavailable for this symbol." if not is_ar else "الرسم البياني التاريخي غير متوفر لهذا الرمز حالياً.")

# MODULE 3: FOREX & CALCULATOR
elif nav.startswith("3."):
    title = "💱 Forex Rates & Financial Calculator" if not is_ar else "💱 أسعار العملات والحاسبة المالية (Forex & Financial Calculator)"
    sub = "Convert any currency pair with automatic EGP benchmark comparison" if not is_ar else "مقارنة دقيقة بالجنيه المصري وحاسبة تحويل شاملة للعملات"
    render_header(title, sub)
    
    st.subheader("🧮 Currency Conversion & Comparison" if not is_ar else "🧮 الحاسبة المالية لتحويل العملات والمقارنة")
    c1, c2, c3 = st.columns(3)
    amount = c1.number_input("Amount / المبلغ", min_value=1.0, value=1000.0, step=100.0)
    all_currencies = ["USD", "EGP", "EUR", "GBP", "SAR", "AED", "KWD", "QAR", "CAD", "JPY", "CHF", "AUD"]
    from_curr = c2.selectbox("From Currency / من عملة", all_currencies, index=0)
    to_curr = c3.selectbox("To Currency / إلى عملة", all_currencies, index=1)
    
    res = calculate_forex_conversion(amount, from_curr, to_curr)
    st.success(f"### 💸 {amount:,.2f} {from_curr} = {res['converted_amount']:,.2f} {to_curr}")
    st.info(f"**Exchange Rate:** 1 {from_curr} = {res['exchange_rate']} {to_curr}")
    
    st.markdown("---")
    st.subheader("🇪🇬 EGP Benchmark Comparison" if not is_ar else "🇪🇬 المقارنة القائمة دائمًا بالجنيه المصري (EGP Benchmark)")
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
    title = "🏆 Gold Reference Prices" if not is_ar else "🏆 أسعار الذهب والرموز (Gold)"
    sub = "Global Troy Ounce & Local EGP Karat Calculations" if not is_ar else "حسابات الذهب والعيارات بالجنيه المصري"
    render_header(title, sub)
    gold = get_gold_reference_data()
    st.metric("Global Troy Ounce Spot", f"${gold['usd_per_troy_oz']:,.2f}")
    st.subheader("EGP Karat Reference Prices" if not is_ar else "أسعار العيارات الاسترشادية بالجنيه المصري")
    st.table(pd.DataFrame([gold['karats_indicative_egp']]))

# MODULE 6: ARBITRAGE SCANNER
elif nav.startswith("6."):
    title = "🚀 Real-Time Arbitrage Scanner" if not is_ar else "🚀 مكتشف الفرص التبادلية - تحديث تلقائي (Live Scanner)"
    sub = "Automated triangular arbitrage scanner with net fee calculation" if not is_ar else "فحص دقيق ومباشر للفروق السعرية بين أزواج التداول مع خصم العمولات"
    render_header(title, sub)
    render_live_arbitrage_scanner()

# MODULE 7: AUTOMATED & UPLOAD FINANCIAL STATEMENTS & RATIO ANALYSIS
elif nav.startswith("7."):
    title = "📈 Financial Statements, Ratios & Forecast Engine" if not is_ar else "📈 تحليل القوائم المالية والنسب المالية وتوقعات السنة القادمة"
    sub = "Auto-fetch annual statements for any stock or upload custom Excel/CSV reports" if not is_ar else "استخراج تلقائي للقوائم المالية لأي شركة في البورصة أو رفع ملفات مخصصة"
    render_header(title, sub)
    
    tab1_title = "🔍 Auto-Fetch Stock Statements (البحث التلقائي عن قوائم الشركات)" if is_ar else "🔍 Auto-Fetch Stock Statements"
    tab2_title = "📂 Upload File (رفع ملف مخصص)" if is_ar else "📂 Upload File"
    
    tab1, tab2 = st.tabs([tab1_title, tab2_title])
    
    df_financials = None
    
    with tab1:
        st.markdown("### 🏛️ Automated Financial Statement Extractor" if not is_ar else "### 🏛️ مستخرج القوائم المالية التلقائي من البورصة")
        st.info("Enter any stock symbol from Egyptian Exchange or Global Stock Markets (e.g. `COMI.CA`, `FWRY.CA`, `AAPL`, `NVDA`, `MSFT`, `AMZN`) to fetch its multi-year statements instantly." if not is_ar else "أدخل رمز أي سهم من البورصة المصرية أو العالمية (مثال: `COMI.CA`, `FWRY.CA`, `AAPL`, `NVDA`, `MSFT`) لاستخراج قوائمه المالية لعدة سنوات فوراً.")
        
        stock_input = st.text_input("Enter Stock Ticker / أدخل رمز السهم", value="COMI.CA").upper()
        
        if st.button("🚀 Fetch Financial Statements / استخراج القوائم المالية", key="fetch_btn"):
            with st.spinner("Fetching income statement & balance sheet from exchange feeds..." if not is_ar else "جاري استخراج قائمة الدخل والميزانية العمومية من البورصة..."):
                fetched_df, msg = fetch_stock_financials_yfinance(stock_input)
                if fetched_df is not None:
                    st.session_state['fetched_df'] = fetched_df
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
                    
        if 'fetched_df' in st.session_state:
            df_financials = st.session_state['fetched_df']

    with tab2:
        st.markdown("### 📂 Upload Custom Financial Report" if not is_ar else "### 📂 رفع تقرير مالية مخصص")
        uploaded_file = st.file_uploader("Upload Excel / CSV Report", type=['xlsx', 'xls', 'csv'], key="fin_file_uploader")
        if uploaded_file is not None:
            df_financials = parse_uploaded_financial_file(uploaded_file.read(), uploaded_file.name)
            if df_financials is not None:
                st.success("✅ File uploaded and parsed successfully!" if not is_ar else "✅ تم رفع وقراءة التقرير المالي بنجاح!")
            else:
                st.error("Error reading file." if not is_ar else "تعذر قراءة الملف.")

    # Fallback to sample data if nothing fetched or uploaded yet
    if df_financials is None:
        st.markdown("---")
        st.info("💡 Sample 3-Year Statement Active (Fetch a ticker above or upload a file):" if not is_ar else "💡 يتم حالياً عرض نموذج القوائم المالية الاسترشادي لثلاث سنوات (استخرج رمز شركة بالفي أعلى أو ارفع ملف):")
        df_financials = create_sample_3yr_financial_data()

    st.subheader("📋 Statement Data View / عرض القائمة المالية")
    st.dataframe(df_financials, use_container_width=True)
    
    if st.button("📊 Analyze Ratios & Forecast / إجراء التحليل المالي والنسب والتوقعات", key="analyze_btn"):
        analysis = analyze_financial_ratios(df_financials)
        
        st.markdown("---")
        st.subheader("📋 Calculated Multi-Year Ratios / كامل النسب المالية المحسوبة")
        ratios_df = pd.DataFrame(analysis["ratios_by_year"])
        st.dataframe(ratios_df, use_container_width=True)
        
        st.markdown("---")
        st.subheader("🔮 Next Year Forecast Projection / الإسقاط التوقعي المستقبلي للسنة القادمة")
        fc = analysis["forecast_year_4"]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Projected Revenue / الإيرادات المتوقعة", f"${fc['Projected Revenue']:,.2f}", f"+{fc['Estimated Revenue Growth Rate (%)']}%")
        c2.metric("Projected Net Profit / صافي الربح المتوقع", f"${fc['Projected Net Profit']:,.2f}", f"+{fc['Estimated Net Profit Growth Rate (%)']}%")
        c3.metric("Est. Net Profit Margin / هامش صافي الربح", f"{fc['Estimated Net Profit Margin (%)']}%")
        c4.metric("Est. ROE / العائد على الملكية", f"{fc['Estimated ROE (%)']}%")
        
        fig_fc = create_forecast_chart(
            list(analysis["ratios_by_year"].keys())[:3],
            analysis["historical_revenue_trend"],
            analysis["historical_net_profit_trend"],
            fc['Projected Revenue'],
            fc['Projected Net Profit'],
            is_ar=is_ar
        )
        st.plotly_chart(fig_fc, use_container_width=True)

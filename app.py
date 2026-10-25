import streamlit as st
import pandas as pd
from datetime import datetime, timezone, timedelta
from storage.database import init_db
from providers.binance import get_binance_ticker_24hr, get_binance_klines
from providers.forex import calculate_universal_forex_conversion, fetch_live_usd_egp_rate, fetch_live_rates_all_currencies
from providers.stocks import get_stock_quote, get_stock_history, search_stocks, EGX30_STOCKS, EGX70_EGX50_STOCKS, GLOBAL_TECH_STOCKS, ALL_STOCKS_LIST
from providers.gold import get_gold_reference_data
from services.arbitrage import scan_arbitrage_opportunities
from services.financial_analyzer import parse_uploaded_financial_file, fetch_stock_financials_yfinance, create_sample_3yr_financial_data, analyze_financial_ratios
from services.analytics import calculate_technical_indicators
from ui.components import render_header
from ui.charts import create_candlestick_chart, create_forecast_chart

st.set_page_config(page_title="Arbitrage Hub - High-Contrast Intelligence Terminal", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0B0E11; color: #FFFFFF; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
    .stSidebar { background-color: #181A20 !important; border-right: 1px solid #2B313A; }
    h1, h2, h3 { color: #F0B90B !important; font-weight: 800; letter-spacing: -0.3px; }
    p, span, label { color: #EAECEF !important; font-size: 15px; font-weight: 500; }
    div[data-testid="stMetricValue"] { 
        color: #F0B90B !important; 
        font-family: 'JetBrains Mono', monospace; 
        font-weight: 800; 
        font-size: 28px !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #B7BDC6 !important;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 13px !important;
        letter-spacing: 0.5px;
    }
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(240, 185, 11, 0.3); }
        50% { box-shadow: 0 0 20px rgba(240, 185, 11, 0.7); }
        100% { box-shadow: 0 0 10px rgba(240, 185, 11, 0.3); }
    }
    div.stButton > button[key="refresh_live_btn"] {
        background: linear-gradient(135deg, #F0B90B 0%, #F8D33A 100%) !important;
        color: #0B0E11 !important;
        font-weight: 900 !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 20px !important;
        animation: pulseGlow 2.5s infinite !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    input, select, div[data-baseweb="select"] {
        background-color: #2B313A !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #474D57 !important;
        font-size: 15px !important;
    }
    .stDataFrame { border: 1px solid #363C4E; border-radius: 6px; }
    button[data-baseweb="tab"] { color: #B7BDC6 !important; font-weight: 700 !important; font-size: 15px !important; }
    button[aria-selected="true"] { color: #F0B90B !important; border-bottom-color: #F0B90B !important; }
</style>
""", unsafe_allow_html=True)

init_db()

st.sidebar.title("🌐 Language / اللغة")
lang_choice = st.sidebar.selectbox("Select Display Language", ["العربية", "English"], index=0)
is_ar = (lang_choice == "العربية")

st.sidebar.markdown("---")
refresh_btn_label = "💵↗️ تحديث الأسعار والأسواق لحظياً" if is_ar else "💵↗️ Refresh Live Market Rates"
if st.sidebar.button(refresh_btn_label, key="refresh_live_btn", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

cairo_time_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (توقيت القاهرة)")
st.sidebar.caption(f"⏱️ آخر تحديث: {cairo_time_str}" if is_ar else f"⏱️ Last Refreshed: {cairo_time_str}")
st.sidebar.markdown("---")
st.sidebar.title("⚡ Arbitrage Hub")
st.sidebar.caption("محرك التحليل المالي وأسواق البورصة والعملات المباشر" if is_ar else "Binance-Grade Financial Intelligence Terminal")

nav_options_ar = [
    "1. 📊 شاشة المراقبة اللحظية (Live Overview)",
    "2. 🏛️ أسهم ومؤشرات البورصة المصرية (EGX)",
    "3. 💱 حاسبة العملات العالمية (Universal Forex)",
    "4. 🪙 الكريبتو - بث مباشر باينانس (Crypto)",
    "5. 🏆 الذهب وحاسبة الصاغة (Gold & Sagha)",
    "6. 🚀 مكتشف الفرص التبادلية (Arbitrage Scanner)",
    "7. 📈 القوائم المالية وتحليل PDF/Excel (Financial Statements)"
]

nav_options_en = [
    "1. 📊 Live Market Overview",
    "2. 🏛️ EGX Market Indices & Stocks",
    "3. 💱 Universal Live Forex Calculator",
    "4. 🪙 Live Crypto Trading Feed",
    "5. 🏆 Gold Pricing & Sagha Premium Calculator",
    "6. 🚀 Real-Time Arbitrage Scanner",
    "7. 📈 Financial Statements & PDF/Excel Intelligence"
]

nav = st.sidebar.radio("Navigation", nav_options_ar if is_ar else nav_options_en)

@st.fragment(run_every="3s")
def render_live_overview_cards():
    c1, c2, c3, c4 = st.columns(4)
    btc = get_binance_ticker_24hr("BTCUSDT")
    if btc:
        lbl = "بيتكوين BTC / USDT (مباشر)" if is_ar else "Bitcoin BTC/USDT (Live)"
        c1.metric(lbl, f"${btc[0]['price']:,.2f}", f"{btc[0]['change_24h_pct']:.2f}%")
        with c1.popover("🔍 مرجع الأرقام / Proof"):
            st.write("**المصدر الأصلي:** Binance Spot Live API v3")
            st.write(f"**الرمز الرسمي:** `{btc[0]['symbol']}`")
            st.write(f"**أعلى سعر (24h):** ${btc[0]['high_24h']:,.2f}")
            st.write(f"**أدنى سعر (24h):** ${btc[0]['low_24h']:,.2f}")
            st.write(f"**توقيت الجلب:** {btc[0]['timestamp']}")

    gold = get_gold_reference_data()
    lbl_gold = "الذهب عالمياً (USD/oz)" if is_ar else "Global Gold (USD/oz)"
    c2.metric(lbl_gold, f"${gold['usd_per_troy_oz']:,.2f}")
    with c2.popover("🔍 مرجع الأرقام / Proof"):
        st.write(f"**المصدر الأصلي:** {gold['gold_source']}")
        st.write(f"**سعر أونصة الذهب:** ${gold['usd_per_troy_oz']:,.2f}")
        st.write(f"**سعر جرام 24 بالجنيه:** {gold['indicative_egp_per_gram_24k']:,.2f} EGP")
        st.write(f"**توقيت الجلب:** {gold['timestamp']}")

    lbl_usd = "سعر الدولار الحي (EGP)" if is_ar else "Live USD/EGP Rate"
    c3.metric(lbl_usd, f"{gold['usd_egp_rate']:.2f} EGP")
    with c3.popover("🔍 مرجع الأرقام / Proof"):
        st.write("**المصدر الأصلي:** EGX Interbank / ExchangeRate Live Feed")
        st.write(f"**سعر صرف 1 USD:** {gold['usd_egp_rate']} EGP")
        st.write(f"**توقيت الجلب:** {gold['timestamp']}")

    cib = get_stock_quote("COMI.CA")
    lbl_cib = "البنك التجاري الدولي (CIB)" if is_ar else "CIB Bank (EGX: COMI)"
    if 'price' in cib:
        c4.metric(lbl_cib, f"{cib['price']:.2f} EGP", f"{cib['change_pct']:.2f}%")
        with c4.popover("🔍 مرجع الأرقام / Proof"):
            st.write(f"**المصدر الأصلي:** {cib['source']}")
            st.write(f"**كود الشركة بالبورصة:** {cib['symbol']}")
            st.write(f"**السعر الحالي:** {cib['price']} {cib['currency']}")
            st.write(f"**توقيت الجلب:** {cib['timestamp']}")

@st.fragment(run_every="4s")
def render_live_crypto_table():
    st.subheader("🔥 تحركات الكريبتو والأسواق العالمية (بث مباشر)" if is_ar else "🔥 Top Crypto Market Movers (Binance Feed)")
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_t = pd.DataFrame(tickers).sort_values('change_24h_pct', ascending=False).head(10)
        st.dataframe(df_t[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'source', 'timestamp']], use_container_width=True)

@st.fragment(run_every="5s")
def render_live_arbitrage_scanner():
    st.caption("🔄 يتم التحديث تلقائياً كل 5 ثوانٍ لجلب أحدث الفرص..." if is_ar else "🔄 Auto-refreshing every 5 seconds...")
    res = scan_arbitrage_opportunities()
    if res:
        st.dataframe(pd.DataFrame(res), use_container_width=True)
    else:
        st.warning("لم يتم العثور على فرص تبادلية محققة للربح بعد خصم العمولات حالياً." if is_ar else "No net arbitrage opportunities detected after fees.")

# MODULE 1: OVERVIEW
if nav.startswith("1."):
    title = "شاشة المراقبة اللحظية 24/7" if is_ar else "Market Overview - 24/7 Live Monitor"
    sub = "بث مباشر لأسعار البورصة المصرية وتداولات باينانس والعملات لحظة بلحظة" if is_ar else "Live market feeds streaming from global exchanges and EGX"
    render_header(title, sub)
    render_live_overview_cards()
    st.markdown("---")
    render_live_crypto_table()

# MODULE 2: EGX STOCKS
elif nav.startswith("2."):
    title = "🏛️ مؤشرات وأسهم البورصة المصرية والعالمية" if is_ar else "🏛️ EGX Market Indices & Stocks Terminal"
    sub = "تصفح مؤشرات EGX30 و EGX70 والأسهم العالمية مع المراجع المباشرة للأسعار" if is_ar else "Explore EGX30, EGX70/50, and Global Tech stocks with categorization and proof"
    render_header(title, sub)
    
    search_query = st.text_input("🔍 ابحث عن أي شركة بالاسم أو الكود (مثال: فوري / CIB / طلعت مصطفى / COMI.CA)", value="").strip()
    
    if search_query:
        matched = search_stocks(search_query)
        st.subheader(f"🔎 نتائج البحث عن: '{search_query}'" if is_ar else f"🔎 Search Results for: '{search_query}'")
        search_options = [f"{s['name_ar']} | {s['name_en']} ({s['symbol']})" for s in matched]
        selected_option = st.selectbox("اختر الشركة", search_options, index=0)
        selected_symbol = selected_option.split("(")[-1].replace(")", "").strip()
        
        quote = get_stock_quote(selected_symbol)
        if 'error' in quote:
            st.error(quote['error'])
        else:
            col_a, col_b, col_c = st.columns(3)
            col_a.metric("السعر اللحظي", f"{quote['price']:,.2f} {quote['currency']}", f"{quote['change_pct']:.2f}%")
            col_b.metric("توقيت الجلب", f"{quote['timestamp']}")
            col_c.metric("مصدر البيانات", f"{quote['source']}")
            
            with col_a.popover("🔍 مرجع السعر والدعم"):
                st.write(f"**اسم الشركة:** {selected_symbol}")
                st.write(f"**سعر الإغلاق/التداول:** {quote['price']} {quote['currency']}")
                st.write(f"**مصدر التداول الرسمي:** {quote['source']}")
                st.write(f"**التوقيت المحلّي:** {quote['timestamp']}")
            
            st.markdown("---")
            st.subheader("📊 الرسم البياني الشمعي التفاعلي")
            tf = st.selectbox("الإطار الزمني", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
            df_stock_hist = get_stock_history(selected_symbol, period=tf)
            if not df_stock_hist.empty:
                df_stock_hist = calculate_technical_indicators(df_stock_hist)
                fig_stock = create_candlestick_chart(df_stock_hist, f"Candlestick Chart - {selected_symbol}")
                st.plotly_chart(fig_stock, use_container_width=True)
            else:
                st.warning("الرسم البياني غير متوفر لهذا السهم حالياً.")
    else:
        tab_30, tab_70, tab_global = st.tabs(["📈 EGX 30 (الأسهم القيادية)", "📊 EGX 70 / 50 (الأسهم المتوسطة)", "🌍 Global Tech (عمالقة التكنولوجيا)"])
        
        def render_index_section(stocks_list, index_name):
            st.markdown(f"### 📋 مكونات مؤشر {index_name}")
            options = [f"{s['name_ar']} | {s['name_en']} ({s['symbol']})" for s in stocks_list]
            sel = st.selectbox(f"اختر شركة من {index_name}", options, key=f"sel_{index_name}")
            sym = sel.split("(")[-1].replace(")", "").strip()
            
            q = get_stock_quote(sym)
            if 'error' in q:
                st.error(q['error'])
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("السعر اللحظي", f"{q['price']:,.2f} {q['currency']}", f"{q['change_pct']:.2f}%")
                c2.metric("توقيت الجلب", f"{q['timestamp']}")
                c3.metric("المصدر المباشر", f"{q['source']}")
                
                with c1.popover("🔍 مرجع الرقم والدليل"):
                    st.write(f"**كود الشركة:** {sym}")
                    st.write(f"**السعر الحالي:** {q['price']} {q['currency']}")
                    st.write(f"**المصدر:** {q['source']}")
                    st.write(f"**التوقيت:** {q['timestamp']}")
                
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
            render_index_section(GLOBAL_TECH_STOCKS, "Global Tech")

# MODULE 3: FOREX
elif nav.startswith("3."):
    title = "💱 حاسبة العملات العالمية اللحظية (Universal Forex)" if is_ar else "💱 Universal Real-Time Forex Calculator"
    sub = "ربط مباشر بجميع عملات العالم مع مرجع تدقيق معتمد لكل سعر" if is_ar else "Live spot exchange rates for ALL 150+ world currencies"
    render_header(title, sub)
    
    live_usd_egp = fetch_live_usd_egp_rate()
    st.info(f"💡 **سعر صرف الدولار المباشر مقابل الجنيه المصري:** `1 USD = {live_usd_egp:.2f} EGP` *(المصدر: Interbank Feed)*")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    amount = col_f1.number_input("المبلغ / Amount", min_value=0.01, value=1000.0, step=100.0)
    
    world_currencies = [
        "USD", "EUR", "GBP", "EGP", "SAR", "AED", "KWD", "QAR", "BHD", "OMR",
        "JPY", "CAD", "AUD", "CHF", "CNY", "INR", "TRY", "RUB", "BRL", "ZAR"
    ]
    
    from_curr = col_f2.selectbox("من عملة / From", world_currencies, index=0)
    to_curr = col_f3.selectbox("إلى عملة / To", world_currencies, index=3)
    
    res = calculate_universal_forex_conversion(amount, from_curr, to_curr)
    
    st.success(f"### 💸 {amount:,.2f} {from_curr} = {res['converted_amount']:,.2f} {to_curr}")
    
    col_r1, col_r2 = st.columns(2)
    col_r1.metric(f"{amount:,.2f} {from_curr} بالجنيه المصري", f"{res['from_amount_in_egp']:,.2f} EGP")
    col_r2.metric(f"{res['converted_amount']:,.2f} {to_curr} بالجنيه المصري", f"{res['to_amount_in_egp']:,.2f} EGP")
    
    with col_r1.popover("🔍 مرجع سعر الصرف والمصدر الرسمي"):
        st.write(f"**سعر التحويل الدقيق:** 1 {from_curr} = {res['exchange_rate']} {to_curr}")
        st.write(f"**مصدر بيانات العملات:** {res['source']}")
        st.write(f"**توقيت الجلب:** {res['timestamp']}")

# MODULE 4: CRYPTO
elif nav.startswith("4."):
    title = "🪙 أسواق الكريبتو والبث المباشر من باينانس" if is_ar else "🪙 Live Crypto Trading Feed"
    sub = "أسعار فورية، رسم شمعي، ومؤشرات فنية حية مباشرة من منصة Binance" if is_ar else "Real-time spot prices and technical indicators from Binance"
    render_header(title, sub)
    
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_crypto = pd.DataFrame(tickers)
        df_crypto = df_crypto[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'source', 'timestamp']]
        df_crypto.columns = ['الرمز', 'السعر اللحظي ($)', 'التغير 24h (%)', 'أعلى سعر ($)', 'أدنى سعر ($)', 'حجم التداول', 'المصدر', 'التوقيت']
        st.dataframe(df_crypto.sort_values(by='السعر اللحظي ($)', ascending=False), use_container_width=True, height=350)

# MODULE 5: GOLD
elif nav.startswith("5."):
    title = "🏆 الذهب العالمي وحاسبة سوق الصاغة المصرية" if is_ar else "🏆 Real-Time Gold Pricing & Sagha Premium Calculator"
    sub = "الربط بين سعر الأونصة عالمياً والأن المباشر مع دعم مرجع كل رقم" if is_ar else "Global Gold Spot linked to USD/EGP with custom Sagha premium"
    render_header(title, sub)
    
    st.sidebar.markdown("### 🏛️ فرق الصاغة المحلية")
    sagha_premium = st.sidebar.slider("نسبة فرق الصاغة %", min_value=0.0, max_value=25.0, value=0.0, step=0.5)
    
    gold = get_gold_reference_data(sagha_premium_pct=sagha_premium)
    
    col_g1, col_g2 = st.columns(2)
    col_g1.metric("سعر أونصة الذهب عالمياً", f"${gold['usd_per_troy_oz']:,.2f}")
    col_g2.metric("سعر جرام الذهب عيار 24 (EGP)", f"{gold['indicative_egp_per_gram_24k']:,.2f} EGP")
    
    with col_g1.popover("🔍 مرجع أرقام الذهب والإسناد"):
        st.write(f"**مصدر الذهب العالمي:** {gold['gold_source']}")
        st.write(f"**سعر صرف الدولار المعتمد:** {gold['usd_egp_rate']} EGP")
        st.write(f"**نسبة فرق الصاغة المطبقة:** {gold['sagha_premium_applied']}%")
        st.write(f"**توقيت الجلب:** {gold['timestamp']}")
        
    st.subheader("أسعار الأعيرة المختلفة بالجنيه المصري")
    st.table(pd.DataFrame([gold['karats_indicative_egp']]))

# MODULE 6: ARBITRAGE SCANNER
elif nav.startswith("6."):
    title = "🚀 مكتشف الفرص التبادلية (Arbitrage Scanner)" if is_ar else "🚀 Real-Time Arbitrage Scanner"
    sub = "فحص الفروق السعرية بين أزواج التداول مع حساب الصافي بعد العمولات" if is_ar else "Automated triangular arbitrage scanner with net fee calculation"
    render_header(title, sub)
    render_live_arbitrage_scanner()

# MODULE 7: FINANCIAL STATEMENTS & PDF/EXCEL PARSER
elif nav.startswith("7."):
    title = "📈 القوائم المالية والتحليل الذكي (PDF / Excel / Stock Extractor)" if is_ar else "📈 Financial Statements & Precision Ratio Intelligence"
    sub = "استخراج البيانات المالية تلقائياً من أسهم البورصة أو رفع ملفات PDF و Excel لربط وتحليل النسب والربحية" if is_ar else "Auto-fetch stock statements or upload custom PDF/Excel files for ratio analysis"
    render_header(title, sub)
    
    tab1, tab2 = st.tabs(["🔍 استخراج القوائم لشركة بالبورصة", "📂 رفع ملف قوائم مالية (PDF / Excel / CSV)"])
    df_financials = None
    
    with tab1:
        st.markdown("### 🏛️ استخراج بيانات القوائم المالية تلقائياً")
        st.info("أدخل كود أي شركة بالبورصة المصرية أو العالمية (مثال: `COMI.CA`, `FWRY.CA`, `AAPL`, `NVDA`) لاستخراج القوائم المالية فوراً.")
        
        stock_input = st.text_input("كود الشركة / Stock Ticker", value="COMI.CA").upper()
        if st.button("🚀 جلب القوائم المالية", key="fetch_btn"):
            with st.spinner("جاري استخراج قائمة الدخل والميزانية العمومية..."):
                fetched_df, msg = fetch_stock_financials_yfinance(stock_input)
                if fetched_df is not None:
                    st.session_state['fetched_df'] = fetched_df
                    st.success(f"✅ {msg}")
                else:
                    st.error(f"❌ {msg}")
                    
        if 'fetched_df' in st.session_state:
            df_financials = st.session_state['fetched_df']

    with tab2:
        st.markdown("### 📂 رفع ملف القوائم المالية (يدعم PDF و Excel و CSV)")
        st.info("يمكنك الآن رفع تقارير PDF الخاصة بشركتك أو ملفات Excel/CSV. سيقوم المحلل المالي الذكي باستخراج الإيرادات وصافي الأرباح والأصول والخصوم وتحليلها فوراً.")
        
        uploaded_file = st.file_uploader("اختر ملف PDF أو Excel أو CSV", type=['pdf', 'xlsx', 'xls', 'csv'], key="fin_file_uploader")
        if uploaded_file is not None:
            with st.spinner("جاري قراءة واستخراج البيانات من الملف..."):
                parsed_df = parse_uploaded_financial_file(uploaded_file.read(), uploaded_file.name)
                if parsed_df is not None:
                    st.session_state['fetched_df'] = parsed_df
                    df_financials = parsed_df
                    st.success(f"✅ تم قراءة واستخراج القوائم المالية بنجاح من الملف `{uploaded_file.name}`!")
                else:
                    st.error("تعذر قراءة أو استخراج البيانات من الملف. يرجى التأكد من المرفق.")

    if df_financials is None:
        st.markdown("---")
        st.info("💡 نموذج افتراضي للقوائم المالية (3 سنوات) للعرض والتحليل:")
        df_financials = create_sample_3yr_financial_data()

    st.subheader("📋 القوائم المالية المستخرجة")
    st.dataframe(df_financials, use_container_width=True)
    
    st.markdown("---")
    if st.button("📊 حساب النسب المالية والتوقعات المستقبلية", key="analyze_btn", use_container_width=True):
        analysis = analyze_financial_ratios(df_financials)
        if analysis and "ratios_by_year" in analysis:
            st.subheader("📋 نتائج تحليل النسب المالية والربحية")
            ratios_df = pd.DataFrame(analysis["ratios_by_year"])
            st.dataframe(ratios_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("🔮 التوقعات المالية للسنة القادمة (N+1)")
            fc = analysis["forecast_next_year"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الإيرادات المتوقعة", f"${fc['Projected Revenue']:,.2f}", f"{fc['Revenue CAGR / Growth Rate (%)']:+.2f}% CAGR")
            c2.metric("صافي الربح المتوقع", f"${fc['Projected Net Income']:,.2f}", f"{fc['Net Income CAGR / Growth Rate (%)']:+.2f}% CAGR")
            c3.metric("هامش صافي الربح", f"{fc['Estimated Net Profit Margin (%)']:.2f}%")
            c4.metric("العائد على الملكية (ROE)", f"{fc['Estimated ROE (%)']:.2f}%")
            
            fig_fc = create_forecast_chart(
                analysis["years"],
                analysis["historical_revenue_trend"],
                analysis["historical_net_profit_trend"],
                fc['Projected Revenue'],
                fc['Projected Net Income']
            )
            st.plotly_chart(fig_fc, use_container_width=True)
        else:
            st.error("تعذر حساب النسب المالية لعدم كفاية البيانات.")

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

st.set_page_config(page_title="Arbitrage Hub - High-Contrast Intelligence Terminal", layout="wide")

st.markdown('''
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
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    p, span, label { 
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
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
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    div[data-testid="stMetricLabel"] { 
        color: #FFFFFF !important; 
        font-size: 14px !important; 
        font-weight: 600 !important; 
    }
    
    /* Popover / Price Reference High Contrast Black Text */
    div[data-testid="stPopoverBody"],
    div[data-testid="stPopoverBody"] *,
    div[role="dialog"],
    div[role="dialog"] * {
        color: #000000 !important;
        background-color: #FFFFFF !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }
    div[data-testid="stPopoverBody"] p,
    div[data-testid="stPopoverBody"] span,
    div[data-testid="stPopoverBody"] div,
    div[data-testid="stPopoverBody"] strong,
    div[data-testid="stPopoverBody"] b,
    div[data-testid="stPopoverBody"] code {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    @keyframes pulseGlow {
        0% { box-shadow: 0 0 10px rgba(240, 185, 11, 0.3); }
        50% { box-shadow: 0 0 20px rgba(240, 185, 11, 0.7); }
        100% { box-shadow: 0 0 10px rgba(240, 185, 11, 0.3); }
    }
    div.stButton > button[key="refresh_live_btn"] {
        background: linear-gradient(135deg, #F0B90B 0%, #F8D33A 100%) !important;
        color: #0B0E11 !important;
        font-weight: 800 !important;
        font-size: 15px !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 12px 20px !important;
        animation: pulseGlow 2.5s infinite !important;
        cursor: pointer !important;
        width: 100% !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    input, select, div[data-baseweb="select"] {
        background-color: #2B313A !important;
        color: #FFFFFF !important;
        border-radius: 6px !important;
        border: 1px solid #474D57 !important;
        font-size: 15px !important;
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    .stDataFrame { border: 1px solid #363C4E; border-radius: 6px; }
    button[data-baseweb="tab"] { color: #FFFFFF !important; font-weight: 700 !important; font-size: 15px !important; }
    button[aria-selected="true"] { color: #F0B90B !important; border-bottom-color: #F0B90B !important; }
</style>
''', unsafe_allow_html=True)

# Initialize database tables
init_db()

# Language Selection
st.sidebar.title("Language / اللغة")
lang_choice = st.sidebar.selectbox("Select Display Language", ["العربية", "English"], index=0)
is_ar = (lang_choice == "العربية")

# Automatic Price Update & Notification Engine trigger on open/load (Saved silently to DB without main UI toast popups)
recent_notifs = check_live_prices_and_notify(is_ar=is_ar)

st.sidebar.markdown("---")
refresh_btn_label = "تحديث الأسعار والأسواق لحظياً" if is_ar else "Refresh Live Market Rates"
if st.sidebar.button(refresh_btn_label, key="refresh_live_btn", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

cairo_time_str = (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%I:%M:%S %p (توقيت القاهرة)")
st.sidebar.caption(f"آخر تحديث: {cairo_time_str}" if is_ar else f"Last Refreshed: {cairo_time_str}")
st.sidebar.markdown("---")
st.sidebar.title("Arbitrage Hub")
st.sidebar.caption("محرك التحليل المالي وأسواق البورصة والعملات المباشر" if is_ar else "Binance-Grade Financial Intelligence Terminal")

nav_options_ar = [
    "1. شاشة المراقبة اللحظية (Live Overview)",
    "2. أسهم ومؤشرات البورصة المصرية (EGX)",
    "3. حاسبة العملات العالمية (Universal Forex)",
    "4. الكريبتو - بث مباشر باينانس (Crypto)",
    "5. الذهب وحاسبة الصاغة (Gold & Sagha)",
    "6. مكتشف الفرص التبادلية (Arbitrage Scanner)",
    "7. القوائم المالية وتحليل PDF/Excel (Financial Statements)",
    "8. التقارير اليومية والإشعارات (Daily Reports & Notifications)"
]

nav_options_en = [
    "1. Live Market Overview",
    "2. EGX Market Indices & Stocks",
    "3. Universal Live Forex Calculator",
    "4. Live Crypto Trading Feed",
    "5. Gold Pricing & Sagha Premium Calculator",
    "6. Real-Time Arbitrage Scanner",
    "7. Financial Statements & PDF/Excel Intelligence",
    "8. Daily Reports & Price Notifications"
]

nav = st.sidebar.radio("Navigation", nav_options_ar if is_ar else nav_options_en)

@st.fragment(run_every="3s")
def render_live_overview_cards():
    c1, c2, c3, c4 = st.columns(4)
    btc = get_binance_ticker_24hr("BTCUSDT")
    if btc:
        lbl = "بيتكوين BTC / USDT (مباشر)" if is_ar else "Bitcoin BTC/USDT (Live)"
        c1.metric(lbl, f"${btc[0]['price']:,.2f}", f"{btc[0]['change_24h_pct']:.2f}%")
        with c1.popover("مرجع الأرقام والتدقيق" if is_ar else "Audit Reference & Proof"):
            st.markdown(f'''
                <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                    <b>المصدر الأصلي:</b> {btc[0].get('source', 'Crypto Feed')}<br>
                    <b>الرمز الرسمي:</b> {btc[0]['symbol']}<br>
                    <b>أعلى سعر (24h):</b> ${btc[0]['high_24h']:,.2f}<br>
                    <b>أدنى سعر (24h):</b> ${btc[0]['low_24h']:,.2f}<br>
                    <b>توقيت الجلب:</b> {btc[0]['timestamp']}
                </div>
            ''', unsafe_allow_html=True)

    gold = get_gold_reference_data()
    lbl_gold = "الذهب عالمياً (USD/oz)" if is_ar else "Global Gold (USD/oz)"
    c2.metric(lbl_gold, f"${gold['usd_per_troy_oz']:,.2f}")
    with c2.popover("مرجع الأرقام والتدقيق" if is_ar else "Audit Reference & Proof"):
        st.markdown(f'''
            <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                <b>المصدر الأصلي:</b> {gold['gold_source']}<br>
                <b>سعر أونصة الذهب:</b> ${gold['usd_per_troy_oz']:,.2f}<br>
                <b>سعر جرام 24 بالجنيه:</b> {gold['indicative_egp_per_gram_24k']:,.2f} EGP<br>
                <b>توقيت الجلب:</b> {gold['timestamp']}
            </div>
        ''', unsafe_allow_html=True)

    lbl_usd = "سعر الدولار الحي (EGP)" if is_ar else "Live USD/EGP Rate"
    c3.metric(lbl_usd, f"{gold['usd_egp_rate']:.2f} EGP")
    with c3.popover("مرجع الأرقام والتدقيق" if is_ar else "Audit Reference & Proof"):
        st.markdown(f'''
            <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                <b>المصدر الأصلي:</b> Google Interbank / EGX Live Rate<br>
                <b>سعر صرف 1 USD:</b> {gold['usd_egp_rate']} EGP<br>
                <b>توقيت الجلب:</b> {gold['timestamp']}
            </div>
        ''', unsafe_allow_html=True)

    cib = get_stock_quote("COMI.CA", is_ar=is_ar)
    lbl_cib = "البنك التجاري الدولي (CIB)" if is_ar else "CIB Bank (EGX: COMI)"
    if 'price' in cib:
        c4.metric(lbl_cib, f"{cib['price']:.2f} EGP", f"{cib['change_pct']:.2f}%")
        with c4.popover("مرجع الأرقام والتدقيق" if is_ar else "Audit Reference & Proof"):
            st.markdown(f'''
                <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                    <b>المصدر الأصلي:</b> {cib['source']}<br>
                    <b>كود الشركة بالبورصة:</b> {cib['symbol']}<br>
                    <b>السعر الحالي:</b> {cib['price']} {cib['currency']}<br>
                    <b>توقيت الجلب:</b> {cib['timestamp']}
                </div>
            ''', unsafe_allow_html=True)

@st.fragment(run_every="4s")
def render_live_crypto_table():
    st.subheader("تحركات الكريبتو والأسواق العالمية (بث مباشر)" if is_ar else "Top Crypto Market Movers (Binance Feed)")
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_t = pd.DataFrame(tickers).sort_values('change_24h_pct', ascending=False).head(10)
        st.dataframe(df_t[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'source', 'timestamp']], use_container_width=True)

@st.fragment(run_every="5s")
def render_live_arbitrage_scanner():
    st.caption("يتم التحديث تلقائياً كل 5 ثوانٍ لجلب أحدث الفرص..." if is_ar else "Auto-refreshing every 5 seconds...")
    res = scan_arbitrage_opportunities()
    if res:
        st.dataframe(pd.DataFrame(res), use_container_width=True)
    else:
        st.warning("لم يتم العثور على فرص تبادلية محققة للربح بعد خصم العمولات حالياً." if is_ar else "No net arbitrage opportunities detected after fees.")

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
            
            with col_a.popover("مرجع السعر والدعم" if is_ar else "Price Proof & Reference"):
                st.markdown(f'''
                    <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                        <b>اسم الشركة:</b> {selected_symbol}<br>
                        <b>سعر الإغلاق/التداول:</b> {quote['price']} {quote['currency']}<br>
                        <b>مصدر التداول الرسمي:</b> {quote['source']}<br>
                        <b>التوقيت المحلّي:</b> {quote['timestamp']}
                    </div>
                ''', unsafe_allow_html=True)
            
            st.markdown("---")
            st.subheader("الرسم البياني الشمعي التفاعلي" if is_ar else "Interactive Candlestick Chart")
            tf = st.selectbox("الإطار الزمني" if is_ar else "Timeframe", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
            df_stock_hist = get_stock_history(selected_symbol, period=tf)
            if not df_stock_hist.empty:
                df_stock_hist = calculate_technical_indicators(df_stock_hist)
                fig_stock = create_candlestick_chart(df_stock_hist, f"Candlestick Chart - {selected_symbol}", is_ar=is_ar)
                st.plotly_chart(fig_stock, use_container_width=True)
            else:
                st.info("الرسم البياني للشاشات الحية متاح للتداولات القياسية." if is_ar else "Candlestick chart available for benchmark stocks.")
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
                
                with c1.popover("مرجع الرقم والدليل" if is_ar else "Proof & Verification"):
                    st.markdown(f'''
                        <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                            <b>كود الشركة:</b> {sym}<br>
                            <b>السعر الحالي:</b> {q['price']} {q['currency']}<br>
                            <b>المصدر:</b> {q['source']}<br>
                            <b>التوقيت:</b> {q['timestamp']}
                        </div>
                    ''', unsafe_allow_html=True)
                
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
    sub = "ربط مباشر بجميع عملات العالم (40+ عملة عالمية وعربية) مع مرجع تدقيق معتمد" if is_ar else "Live spot exchange rates for ALL 40+ major and regional currencies"
    render_header(title, sub, is_ar=is_ar)
    
    live_usd_egp = fetch_live_usd_egp_rate()
    st.info(f"سعر صرف الدولار المباشر مقابل الجنيه المصري: 1 USD = {live_usd_egp:.2f} EGP (المصدر: Google Interbank Feed)" if is_ar else f"Live USD to EGP Rate: 1 USD = {live_usd_egp:.2f} EGP (Source: Google Interbank Feed)")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    amount = col_f1.number_input("المبلغ / Amount", min_value=0.01, value=1000.0, step=100.0)
    
    from_curr = col_f2.selectbox("من عملة / From", ALL_WORLD_CURRENCIES, index=0)
    to_curr = col_f3.selectbox("إلى عملة / To", ALL_WORLD_CURRENCIES, index=3)
    
    res = calculate_universal_forex_conversion(amount, from_curr, to_curr)
    
    st.success(f"### {amount:,.2f} {from_curr} = {res['converted_amount']:,.2f} {to_curr}")
    
    col_r1, col_r2 = st.columns(2)
    col_r1.metric(f"{amount:,.2f} {from_curr} بالجنيه المصري", f"{res['from_amount_in_egp']:,.2f} EGP")
    col_r2.metric(f"{res['converted_amount']:,.2f} {to_curr} بالجنيه المصري", f"{res['to_amount_in_egp']:,.2f} EGP")
    
    with col_r1.popover("مرجع سعر الصرف والمصدر الرسمي" if is_ar else "Exchange Rate Source & Proof"):
        st.markdown(f'''
            <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                <b>سعر التحويل الدقيق:</b> 1 {from_curr} = {res['exchange_rate']} {to_curr}<br>
                <b>مصدر بيانات العملات:</b> {res['source']}<br>
                <b>توقيت الجلب:</b> {res['timestamp']}
            </div>
        ''', unsafe_allow_html=True)

# MODULE 4: CRYPTO
elif nav.startswith("4."):
    title = "أسواق الكريبتو والبث المباشر (Crypto Live Feed)" if is_ar else "Live Crypto Trading Feed"
    sub = "أسعار فورية، رسم شمعي، ومؤشرات فنية حية مباشرة من البورصات العالمية" if is_ar else "Real-time spot prices and technical indicators from Binance & Global Exchanges"
    render_header(title, sub, is_ar=is_ar)
    
    tickers = get_binance_ticker_24hr()
    if tickers:
        df_crypto = pd.DataFrame(tickers)
        df_crypto = df_crypto[['symbol', 'price', 'change_24h_pct', 'high_24h', 'low_24h', 'volume_24h', 'source', 'timestamp']]
        if is_ar:
            df_crypto.columns = ['الرمز', 'السعر اللحظي ($)', 'التغير 24h (%)', 'أعلى سعر ($)', 'أدنى سعر ($)', 'حجم التداول', 'المصدر', 'التوقيت']
        else:
            df_crypto.columns = ['Symbol', 'Live Price ($)', '24h Change (%)', '24h High ($)', '24h Low ($)', 'Volume', 'Source', 'Timestamp']
        st.dataframe(df_crypto.sort_values(by=df_crypto.columns[1], ascending=False), use_container_width=True, height=350)
    else:
        st.warning("جاري الاتصال بخوادم الكريبتو العالمية..." if is_ar else "Connecting to global crypto exchange servers...")

# MODULE 5: GOLD
elif nav.startswith("5."):
    title = "الذهب العالمي وحاسبة سوق الصاغة المصرية" if is_ar else "Real-Time Gold Pricing & Sagha Premium Calculator"
    sub = "الربط بين سعر الأونصة عالمياً والأن المباشر مع دعم مرجع كل رقم" if is_ar else "Global Gold Spot linked to USD/EGP with custom Sagha premium"
    render_header(title, sub, is_ar=is_ar)
    
    st.sidebar.markdown("### فرق الصاغة المحلية" if is_ar else "### Local Sagha Premium")
    sagha_premium = st.sidebar.slider("نسبة فرق الصاغة %" if is_ar else "Sagha Premium %", min_value=0.0, max_value=25.0, value=0.0, step=0.5)
    
    gold = get_gold_reference_data(sagha_premium_pct=sagha_premium)
    
    col_g1, col_g2 = st.columns(2)
    col_g1.metric("سعر أونصة الذهب عالمياً" if is_ar else "Global Gold Ounce Price", f"${gold['usd_per_troy_oz']:,.2f}")
    col_g2.metric("سعر جرام الذهب عيار 24 (EGP)" if is_ar else "Gold 24K Gram Price (EGP)", f"{gold['indicative_egp_per_gram_24k']:,.2f} EGP")
    
    with col_g1.popover("مرجع أرقام الذهب والإسناد" if is_ar else "Gold Pricing Proof"):
        st.markdown(f'''
            <div style="color: #000000; font-weight: 600; line-height: 1.6;">
                <b>مصدر الذهب العالمي:</b> {gold['gold_source']}<br>
                <b>سعر صرف الدولار المعتمد:</b> {gold['usd_egp_rate']} EGP<br>
                <b>نسبة فرق الصاغة المطبقة:</b> {gold['sagha_premium_applied']}%<br>
                <b>توقيت الجلب:</b> {gold['timestamp']}
            </div>
        ''', unsafe_allow_html=True)
        
    st.subheader("أسعار الأعيرة المختلفة بالجنيه المصري" if is_ar else "Indicative Karat Prices in EGP")
    st.table(pd.DataFrame([gold['karats_indicative_egp']]))

# MODULE 6: ARBITRAGE SCANNER
elif nav.startswith("6."):
    title = "مكتشف الفرص التبادلية (Arbitrage Scanner)" if is_ar else "Real-Time Arbitrage Scanner"
    sub = "فحص الفروق السعرية بين أزواج التداول مع حساب الصافي بعد العمولات" if is_ar else "Automated triangular arbitrage scanner with net fee calculation"
    render_header(title, sub, is_ar=is_ar)
    render_live_arbitrage_scanner()

# MODULE 7: FINANCIAL STATEMENTS & PDF/EXCEL PARSER
elif nav.startswith("7."):
    title = "القوائم المالية والتحليل الذكي (PDF / Excel / Stock Extractor)" if is_ar else "Financial Statements & Precision Ratio Intelligence"
    sub = "استخراج البيانات المالية تلقائياً من أسهم البورصة أو رفع ملفات PDF و Excel لربط وتحليل النسب والربحية" if is_ar else "Auto-fetch stock statements or upload custom PDF/Excel files for ratio analysis"
    render_header(title, sub, is_ar=is_ar)
    
    tab1, tab2 = st.tabs(["استخراج القوائم لشركة بالبورصة" if is_ar else "Fetch Stock Financials", "رفع ملف قوائم مالية (PDF / Excel / CSV)" if is_ar else "Upload PDF/Excel Statement"])
    df_financials = None
    
    with tab1:
        st.markdown("### استخراج بيانات القوائم المالية تلقائياً" if is_ar else "### Auto-fetch Stock Financial Statements")
        st.info("أدخل كود أي شركة بالبورصة المصرية أو العالمية (مثال: COMI.CA, FWRY.CA, HALA.CA, AAPL, NVDA) لاستخراج القوائم المالية فوراً." if is_ar else "Enter any EGX or global stock ticker (e.g. COMI.CA, HALA.CA, AAPL) to extract financial statements instantly.")
        
        stock_input = st.text_input("كود الشركة / Stock Ticker", value="COMI.CA").upper()
        if st.button("جلب القوائم المالية" if is_ar else "Fetch Financial Statements", key="fetch_btn"):
            with st.spinner("جاري استخراج قائمة الدخل والميزانية العمومية..." if is_ar else "Extracting income statement & balance sheet..."):
                fetched_df, msg = fetch_stock_financials_yfinance(stock_input)
                if fetched_df is not None:
                    st.session_state['fetched_df'] = fetched_df
                    st.success(f"{msg}")
                else:
                    st.error(f"{msg}")
                    
        if 'fetched_df' in st.session_state:
            df_financials = st.session_state['fetched_df']

    with tab2:
        st.markdown("### رفع ملف القوائم المالية (يدعم PDF و Excel و CSV)" if is_ar else "### Upload Financial Statement File (PDF / Excel / CSV)")
        st.info("يمكنك الآن رفع تقارير PDF الخاصة بشركتك أو ملفات Excel/CSV. سيقوم المحلل المالي الذكي باستخراج الإيرادات وصافي الأرباح والأصول والخصوم وتحليلها فوراً." if is_ar else "Upload your custom PDF reports or Excel/CSV files. The financial engine will automatically parse revenue, profits, assets, and ratios.")
        
        uploaded_file = st.file_uploader("اختر ملف PDF أو Excel أو CSV" if is_ar else "Choose PDF, Excel, or CSV file", type=['pdf', 'xlsx', 'xls', 'csv'], key="fin_file_uploader")
        if uploaded_file is not None:
            with st.spinner("جاري قراءة واستخراج البيانات من الملف..." if is_ar else "Parsing and extracting financial metrics from file..."):
                parsed_df = parse_uploaded_financial_file(uploaded_file.read(), uploaded_file.name)
                if parsed_df is not None:
                    st.session_state['fetched_df'] = parsed_df
                    df_financials = parsed_df
                    st.success(f"تم قراءة واستخراج القوائم المالية بنجاح من الملف {uploaded_file.name}!" if is_ar else f"Statements successfully extracted from {uploaded_file.name}!")
                else:
                    st.error("تعذر قراءة أو استخراج البيانات من الملف. يرجى التأكد من المرفق." if is_ar else "Unable to parse financial statement from file.")

    if df_financials is None:
        st.markdown("---")
        st.info("نموذج افتراضي للقوائم المالية (3 سنوات) للعرض والتحليل:" if is_ar else "Default 3-year sample financial benchmark data:")
        df_financials = create_sample_3yr_financial_data()

    st.subheader("القوائم المالية المستخرجة" if is_ar else "Extracted Financial Statements")
    st.dataframe(df_financials, use_container_width=True)
    
    st.markdown("---")
    if st.button("حساب النسب المالية والتوقعات المستقبلية" if is_ar else "Calculate Ratios & Future Forecasts", key="analyze_btn", use_container_width=True):
        analysis = analyze_financial_ratios(df_financials)
        if analysis and "ratios_by_year" in analysis:
            st.subheader("نتائج تحليل النسب المالية والربحية" if is_ar else "Financial Ratio & Profitability Results")
            ratios_df = pd.DataFrame(analysis["ratios_by_year"])
            st.dataframe(ratios_df, use_container_width=True)
            
            st.markdown("---")
            st.subheader("التوقعات المالية للسنة القادمة (N+1)" if is_ar else "Next Year Projections (N+1)")
            fc = analysis["forecast_next_year"]
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("الإيرادات المتوقعة" if is_ar else "Projected Revenue", f"${fc['Projected Revenue']:,.2f}", f"{fc['Revenue CAGR / Growth Rate (%)']:+.2f}% CAGR")
            c2.metric("صافي الربح المتوقع" if is_ar else "Projected Net Income", f"${fc['Projected Net Income']:,.2f}", f"{fc['Net Income CAGR / Growth Rate (%)']:+.2f}% CAGR")
            c3.metric("هامش صافي الربح" if is_ar else "Net Profit Margin", f"{fc['Estimated Net Profit Margin (%)']:.2f}%")
            c4.metric("العائد على الملكية (ROE)" if is_ar else "Return on Equity (ROE)", f"{fc['Estimated ROE (%)']:.2f}%")
            
            fig_fc = create_forecast_chart(
                analysis["years"],
                analysis["historical_revenue_trend"],
                analysis["historical_net_profit_trend"],
                fc['Projected Revenue'],
                fc['Projected Net Income'],
                is_ar=is_ar
            )
            st.plotly_chart(fig_fc, use_container_width=True)
        else:
            st.error("تعذر حساب النسب المالية لعدم كفاية البيانات." if is_ar else "Failed to calculate ratios due to insufficient data.")

# MODULE 8: DAILY REPORTS & NOTIFICATIONS
elif nav.startswith("8."):
    title = "التقارير اليومية وسجل الإشعارات اللحظية (Daily Reports & Notifications)" if is_ar else "Daily Reports & Real-Time Price Notification Log"
    sub = "عرض شامل لكل التغيرات والإشعارات التي حدثت في أسعار العملات والأسهم والذهب باليوم والشهر والساعة والدقيقة والثانية" if is_ar else "Full historic log of all automated price alerts tracked with exact day, month, hour, minute, and second"
    render_header(title, sub, is_ar=is_ar)
    
    # Fetch all logged notifications
    logs = get_all_notifications_log(limit=500)
    
    if not logs:
        st.info("لا توجد إشعارات مسجلة حتى الآن. ستقوم المنظومة بتسجيل أي تغير في الأسعار فور حدوثه تلقائياً." if is_ar else "No notifications logged yet. The engine automatically logs every price movement as soon as it occurs.")
    else:
        df_logs = pd.DataFrame(logs)
        
        # Summary Metrics
        total_notifs = len(df_logs)
        rises = len(df_logs[df_logs['change_pct'] > 0])
        drops = len(df_logs[df_logs['change_pct'] < 0])
        last_time = df_logs.iloc[0]['formatted_time'] if 'formatted_time' in df_logs.columns else "N/A"
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("إجمالي الإشعارات المسجلة" if is_ar else "Total Logged Alerts", f"{total_notifs}")
        m2.metric("عدد مرات الارتفاع" if is_ar else "Price Increases", f"{rises}")
        m3.metric("عدد مرات الانخفاض" if is_ar else "Price Drops", f"{drops}")
        m4.metric("توقيت آخر إشعار (بالثانية)" if is_ar else "Last Alert Timestamp", f"{last_time}")
        
        st.markdown("---")
        st.subheader("تصفية وتصفح التقارير اليومية" if is_ar else "Filter & Search Daily Reports")
        
        col_flt1, col_flt2, col_flt3 = st.columns(3)
        
        # Asset Category Filter
        categories = ["الكل / All"] + list(df_logs['asset_type'].unique())
        cat_sel = col_flt1.selectbox("فئة الأصل" if is_ar else "Asset Category", categories)
        
        # Direction Filter
        direction_opts = ["جميع التحركات / All Movements", "ارتفاع فقط / Increases Only", "انخفاض فقط / Drops Only"]
        dir_sel = col_flt2.selectbox("اتجاه التغير" if is_ar else "Price Direction", direction_opts)
        
        # Apply Filters
        filtered_df = df_logs.copy()
        if cat_sel != "الكل / All":
            filtered_df = filtered_df[filtered_df['asset_type'] == cat_sel]
            
        if "ارتفاع" in dir_sel or "Increases" in dir_sel:
            filtered_df = filtered_df[filtered_df['change_pct'] > 0]
        elif "انخفاض" in dir_sel or "Drops" in dir_sel:
            filtered_df = filtered_df[filtered_df['change_pct'] < 0]

        # Prepare Display Table
        display_df = pd.DataFrame()
        display_df['رقم الإشعار / ID'] = filtered_df['id']
        display_df['التاريخ والتوقيت بالثانية / Timestamp (DD/MM/YYYY HH:MM:SS)'] = filtered_df['formatted_time']
        display_df['فئة الأصل / Category'] = filtered_df['asset_type']
        display_df['اسم الأصل / Asset Name'] = filtered_df['display_name_ar'] if is_ar else filtered_df['display_name_en']
        display_df['السعر السابق / Old Price'] = filtered_df.apply(lambda r: f"{r['old_price']:,.2f} {r['currency']}", axis=1)
        display_df['السعر الجديد / New Price'] = filtered_df.apply(lambda r: f"{r['new_price']:,.2f} {r['currency']}", axis=1)
        display_df['نسبة التغير % / Change %'] = filtered_df.apply(lambda r: f"{r['change_pct']:+.3f}%", axis=1)
        display_df['الحالة / Status'] = filtered_df.apply(lambda r: "ارتفاع" if r['change_pct'] > 0 else ("انخفاض" if r['change_pct'] < 0 else "سعر أولي"), axis=1)
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        col_act1, col_act2 = st.columns(2)
        
        # Export as CSV
        csv_data = filtered_df.to_csv(index=False, encoding='utf-8-sig')
        col_act1.download_button(
            label="تحميل التقرير اليومي كملف CSV" if is_ar else "Download Daily Report as CSV",
            data=csv_data,
            file_name=f"Daily_Notifications_Report_{datetime.now().strftime('%Y_%m_%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        if col_act2.button("مسح سجل الإشعارات" if is_ar else "Clear Notification Log", use_container_width=True):
            clear_notifications_log()
            st.success("تم مسح سجل الإشعارات بنجاح!" if is_ar else "Notification log cleared successfully!")
            st.rerun()

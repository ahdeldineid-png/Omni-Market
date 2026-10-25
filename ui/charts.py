import plotly.graph_objects as go
import pandas as pd

def create_candlestick_chart(df: pd.DataFrame, title: str = "Price Chart", is_ar: bool = True) -> go.Figure:
    fig = go.Figure()
    if df.empty:
        msg = "بيانات الأسعار غير متوفرة حالياً" if is_ar else "Price Data Unavailable"
        fig.add_annotation(text=msg, showarrow=False, font=dict(size=16, color="#FFFFFF"))
        fig.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0B0E11", plot_bgcolor="#181A20")
        return fig
    
    fig.add_trace(go.Candlestick(
        x=df['open_time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='#0ECB81',
        decreasing_line_color='#F6465D',
        increasing_fillcolor='#0ECB81',
        decreasing_fillcolor='#F6465D',
        name="OHLC"
    ))
    
    sma20_lbl = "المتوسط المتحرك 20" if is_ar else "SMA 20"
    sma50_lbl = "المتوسط المتحرك 50" if is_ar else "SMA 50"

    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_20'], mode='lines', name=sma20_lbl, line=dict(color='#F0B90B', width=1.8)))
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_50'], mode='lines', name=sma50_lbl, line=dict(color='#00E5FF', width=1.8)))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#F0B90B", family="Inter")),
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#1E2329",
        font=dict(color="#FFFFFF", size=13),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_forecast_chart(historical_years: list, rev_hist: list, net_hist: list, yr4_rev: float, yr4_net: float, is_ar: bool = True) -> go.Figure:
    fig = go.Figure()
    
    next_yr_label = "السنة القادمة (متوقعة)" if is_ar else "Next Year (Projected)"
    years_all = [str(y) for y in historical_years] + [next_yr_label]
    rev_all = rev_hist + [yr4_rev]
    net_all = net_hist + [yr4_net]
    
    rev_label = "الإيرادات" if is_ar else "Revenue"
    net_label = "صافي الربح" if is_ar else "Net Income"
    chart_title = "الأداء التاريخي والتوقعات للسنة القادمة" if is_ar else "Historical Performance & Next Year Projection"

    fig.add_trace(go.Bar(x=years_all, y=rev_all, name=rev_label, marker_color="#F0B90B"))
    fig.add_trace(go.Bar(x=years_all, y=net_all, name=net_label, marker_color="#0ECB81"))
    
    fig.update_layout(
        title=dict(text=chart_title, font=dict(size=18, color="#F0B90B", family="Inter")),
        template="plotly_dark",
        barmode="group",
        height=450,
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#1E2329",
        font=dict(color="#FFFFFF", size=13),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

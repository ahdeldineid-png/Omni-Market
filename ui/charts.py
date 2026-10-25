import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_candlestick_chart(df: pd.DataFrame, title: str = "Price Chart", is_ar: bool = True) -> go.Figure:
    if df is None or df.empty or 'close' not in df.columns:
        fig = go.Figure()
        msg = "بيانات الأسعار غير متوفرة حالياً" if is_ar else "Price Data Unavailable"
        fig.add_annotation(text=msg, showarrow=False, font=dict(size=16, color="#FFFFFF", family="Inter, Segoe UI, Roboto, sans-serif"))
        fig.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0B0E11", plot_bgcolor="#181A20")
        return fig

    # Clean missing values
    df = df.dropna(subset=['open', 'high', 'low', 'close']).copy()
    if df.empty:
        fig = go.Figure()
        msg = "بيانات الأسعار غير متوفرة حالياً" if is_ar else "Price Data Unavailable"
        fig.add_annotation(text=msg, showarrow=False, font=dict(size=16, color="#FFFFFF", family="Inter, Segoe UI, Roboto, sans-serif"))
        fig.update_layout(template="plotly_dark", height=450, paper_bgcolor="#0B0E11", plot_bgcolor="#181A20")
        return fig

    # Subplots: Row 1 = Candlestick & Moving Averages (75% height), Row 2 = Volume (25% height)
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.75, 0.25],
        subplot_titles=None
    )

    # 1. Candlestick Trace
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
        name="OHLC / الشموع"
    ), row=1, col=1)

    # 2. Technical Moving Averages
    sma20_lbl = "المتوسط المتحرك (SMA 20)" if is_ar else "SMA 20"
    sma50_lbl = "المتوسط المتحرك (SMA 50)" if is_ar else "SMA 50"

    if 'SMA_20' in df.columns and not df['SMA_20'].isna().all():
        fig.add_trace(go.Scatter(
            x=df['open_time'], y=df['SMA_20'], mode='lines', 
            name=sma20_lbl, line=dict(color='#F0B90B', width=1.8)
        ), row=1, col=1)

    if 'SMA_50' in df.columns and not df['SMA_50'].isna().all():
        fig.add_trace(go.Scatter(
            x=df['open_time'], y=df['SMA_50'], mode='lines', 
            name=sma50_lbl, line=dict(color='#00E5FF', width=1.8)
        ), row=1, col=1)

    # 3. Volume Bar Trace
    if 'volume' in df.columns and not df['volume'].isna().all():
        colors = ['#0ECB81' if float(c) >= float(o) else '#F6465D' for c, o in zip(df['close'], df['open'])]
        vol_lbl = "حجم التداول / Volume" if is_ar else "Volume"
        fig.add_trace(go.Bar(
            x=df['open_time'], y=df['volume'],
            marker_color=colors,
            name=vol_lbl,
            opacity=0.8
        ), row=2, col=1)

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#F0B90B", family="Inter, Segoe UI, Roboto, sans-serif")),
        template="plotly_dark",
        height=560,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#181A20",
        font=dict(color="#FFFFFF", size=12, family="Inter, Segoe UI, Roboto, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    fig.update_xaxes(gridcolor="#2B313A", showgrid=True)
    fig.update_yaxes(gridcolor="#2B313A", showgrid=True)

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
        title=dict(text=chart_title, font=dict(size=18, color="#F0B90B", family="Inter, Segoe UI, Roboto, sans-serif")),
        template="plotly_dark",
        barmode="group",
        height=450,
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#181A20",
        font=dict(color="#FFFFFF", size=13, family="Inter, Segoe UI, Roboto, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

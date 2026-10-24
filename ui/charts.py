import plotly.graph_objects as go
import pandas as pd

def create_candlestick_chart(df: pd.DataFrame, title: str = "Price Chart") -> go.Figure:
    fig = go.Figure()
    if df.empty:
        fig.add_annotation(text="Price Data Unavailable / بيانات الأسعار غير متاحة", showarrow=False, font=dict(size=18, color="white"))
        fig.update_layout(template="plotly_dark", height=450)
        return fig
    
    fig.add_trace(go.Candlestick(
        x=df['open_time'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name="OHLC"
    ))
    
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#00E5FF', width=1.8)))
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#FFD700', width=1.8)))

    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#F9FAFB")),
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0B0E14",
        plot_bgcolor="#111827",
        font=dict(color="#D1D5DB"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_forecast_chart(historical_years: list, rev_hist: list, net_hist: list, yr4_rev: float, yr4_net: float) -> go.Figure:
    fig = go.Figure()
    
    next_yr_label = "Next Year (Projected)"
    rev_label = "Revenue"
    net_label = "Net Income"
    
    years_all = [str(y) for y in historical_years] + [next_yr_label]
    rev_all = rev_hist + [yr4_rev]
    net_all = net_hist + [yr4_net]
    
    fig.add_trace(go.Bar(x=years_all, y=rev_all, name=rev_label, marker_color="#00E5FF"))
    fig.add_trace(go.Bar(x=years_all, y=net_all, name=net_label, marker_color="#00FF87"))
    
    fig.update_layout(
        title=dict(text="📈 Historical Performance & Next Year Projection", font=dict(size=18, color="#F9FAFB")),
        template="plotly_dark",
        barmode="group",
        height=450,
        paper_bgcolor="#0B0E14",
        plot_bgcolor="#111827",
        font=dict(color="#D1D5DB"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

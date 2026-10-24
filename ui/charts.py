import plotly.graph_objects as go
import pandas as pd

def create_candlestick_chart(df: pd.DataFrame, title: str = "Price Chart") -> go.Figure:
    fig = go.Figure()
    if df.empty:
        fig.add_annotation(text="Price Data Unavailable", showarrow=False, font=dict(size=16, color="#848E9C"))
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
    
    if 'SMA_20' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#F0B90B', width=1.5)))
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#00E5FF', width=1.5)))

    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color="#EAECEF")),
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#1E2329",
        font=dict(color="#848E9C"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def create_forecast_chart(historical_years: list, rev_hist: list, net_hist: list, yr4_rev: float, yr4_net: float) -> go.Figure:
    fig = go.Figure()
    
    next_yr_label = "Next Year (Projected)"
    years_all = [str(y) for y in historical_years] + [next_yr_label]
    rev_all = rev_hist + [yr4_rev]
    net_all = net_hist + [yr4_net]
    
    fig.add_trace(go.Bar(x=years_all, y=rev_all, name="Revenue", marker_color="#F0B90B"))
    fig.add_trace(go.Bar(x=years_all, y=net_all, name="Net Income", marker_color="#0ECB81"))
    
    fig.update_layout(
        title=dict(text="Historical Performance & Next Year Projection", font=dict(size=16, color="#EAECEF")),
        template="plotly_dark",
        barmode="group",
        height=450,
        paper_bgcolor="#0B0E11",
        plot_bgcolor="#1E2329",
        font=dict(color="#848E9C"),
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

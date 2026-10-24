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
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_20'], mode='lines', name='SMA 20', line=dict(color='#2962FF', width=1.5)))
    if 'SMA_50' in df.columns:
        fig.add_trace(go.Scatter(x=df['open_time'], y=df['SMA_50'], mode='lines', name='SMA 50', line=dict(color='#FF6D00', width=1.5)))

    fig.update_layout(
        title=title,
        template="plotly_dark",
        height=520,
        xaxis_rangeslider_visible=False,
        paper_bgcolor="#131722",
        plot_bgcolor="#131722"
    )
    return fig

def create_forecast_chart(historical_years: list, rev_hist: list, net_hist: list, yr4_rev: float, yr4_net: float, is_ar: bool = False) -> go.Figure:
    fig = go.Figure()
    
    next_yr_label = "Next Year (Projected)" if not is_ar else "السنة القادمة (توقعي)"
    rev_label = "Revenue / الإيرادات"
    net_label = "Net Income / صافي الربح"
    
    years_all = historical_years + [next_yr_label]
    rev_all = rev_hist + [yr4_rev]
    net_all = net_hist + [yr4_net]
    
    fig.add_trace(go.Bar(x=years_all, y=rev_all, name=rev_label, marker_color="#2962FF"))
    fig.add_trace(go.Bar(x=years_all, y=net_all, name=net_label, marker_color="#00E676"))
    
    chart_title = "📈 Trend Analysis & Projection" if not is_ar else "📈 تحليل الاتجاه التاريخي والإسقاط التوقعي"
    
    fig.update_layout(
        title=chart_title,
        template="plotly_dark",
        barmode="group",
        height=450,
        paper_bgcolor="#131722",
        plot_bgcolor="#131722"
    )
    return fig

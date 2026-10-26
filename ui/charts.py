def create_candlestick_chart(df, title, is_ar=True):
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Candlestick(x=df["open_time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"])])
    fig.update_layout(title=title, template="plotly_dark", plot_bgcolor="#0F1319", paper_bgcolor="#07090C", font=dict(color="#F8FAFC"))
    return fig

def create_forecast_chart(df, title, is_ar=True):
    import plotly.graph_objects as go
    fig = go.Figure()
    if df is not None and not df.empty:
        fig.add_trace(go.Scatter(x=df.get("date", df.index), y=df.get("price", df.iloc[:, 0]), mode="lines+markers", name="Forecast / توقعات"))
    fig.update_layout(title=title, template="plotly_dark", plot_bgcolor="#0F1319", paper_bgcolor="#07090C", font=dict(color="#F8FAFC"))
    return fig

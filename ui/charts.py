def create_candlestick_chart(df, title, is_ar=True):
    import plotly.graph_objects as go
    fig = go.Figure(data=[go.Candlestick(x=df["open_time"], open=df["open"], high=df["high"], low=df["low"], close=df["close"])])
    fig.update_layout(title=title, template="plotly_dark")
    return fig

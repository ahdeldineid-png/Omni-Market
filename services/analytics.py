import pandas as pd

def calculate_technical_indicators(df):
    if df is None or df.empty:
        return df
    if 'close' in df.columns:
        df['SMA_20'] = df['close'].rolling(window=min(20, len(df))).mean()
        df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / (loss + 1e-9)
        df['RSI'] = 100 - (100 / (1 + rs))
    return df

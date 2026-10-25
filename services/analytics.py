import pandas as pd

def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or 'close' not in df.columns:
        return df
    df = df.copy()
    
    n = len(df)
    w20 = min(20, n) if n > 1 else 1
    w50 = min(50, n) if n > 1 else 1
    
    df['SMA_20'] = df['close'].rolling(window=w20, min_periods=1).mean()
    df['SMA_50'] = df['close'].rolling(window=w50, min_periods=1).mean()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=min(14, n), min_periods=1).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=min(14, n), min_periods=1).mean()
    rs = gain / (loss + 1e-10)
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    return df

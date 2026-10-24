import pandas as pd
import numpy as np
import io
import yfinance as yf
from typing import Dict, Any, Optional, Tuple

METRICS_ENGLISH_LABELS = [
    ("Revenue / Total Sales", ["revenue", "total revenue", "sales", "operating revenue", "المبيعات", "الإيرادات"]),
    ("Cost of Goods Sold (COGS)", ["cost of revenue", "cogs", "cost of goods sold", "revenues cost", "تكلفة المبيعات", "تكلفة البضاعة المباعة"]),
    ("Gross Profit", ["gross profit", "مجمل الربح"]),
    ("Operating Expenses (OPEX)", ["operating expense", "total operating expenses", "opex", "المصروفات التشغيلية"]),
    ("Operating Income (EBIT)", ["operating income", "ebit", "الربح التشغيلي"]),
    ("Net Income / Profit", ["net income", "net profit", "net income common stockholders", "صافي الربح"]),
    ("Total Assets", ["total assets", "إجمالي الأصول"]),
    ("Current Assets", ["current assets", "total current assets", "الأصول المتداولة"]),
    ("Cash & Cash Equivalents", ["cash", "cash and cash equivalents", "cash cash equivalents and short term investments", "النقدية وما يعادلها"]),
    ("Accounts Receivable", ["accounts receivable", "receivables", "المدينون"]),
    ("Inventory", ["inventory", "inventories", "المخزون"]),
    ("Total Liabilities", ["total liabilities", "total liabilities net minority interest", "إجمالي الالتزامات"]),
    ("Current Liabilities", ["current liabilities", "total current liabilities", "الالتزامات المتداولة"]),
    ("Total Debt", ["total debt", "long term debt", "short long term debt", "إجمالي الديون"]),
    ("Total Shareholders' Equity", ["stockholders equity", "total equity gross minority interest", "total shareholders equity", "حقوق الملكية"])
]

def parse_uploaded_financial_file(file_bytes: bytes, filename: str) -> Optional[pd.DataFrame]:
    try:
        if filename.endswith('.csv'):
            df_raw = pd.read_csv(io.BytesIO(file_bytes))
        elif filename.endswith(('.xlsx', '.xls')):
            df_raw = pd.read_excel(io.BytesIO(file_bytes))
        else:
            return None

        if df_raw.empty or len(df_raw.columns) < 2:
            return None

        df_raw.iloc[:, 0] = df_raw.iloc[:, 0].astype(str)
        value_cols = list(df_raw.columns[1:])

        data_dict = {"Metric": [m[0] for m in METRICS_ENGLISH_LABELS]}

        for col in value_cols:
            col_label = f"Year {col}" if not str(col).lower().startswith("year") else str(col)
            col_vals = []

            for label, keywords in METRICS_ENGLISH_LABELS:
                matched_val = 0.0
                for idx, row_name in enumerate(df_raw.iloc[:, 0]):
                    row_str = str(row_name).lower().strip()
                    if any(kw in row_str for kw in keywords):
                        val = df_raw.iloc[idx][col]
                        try:
                            clean_val = str(val).replace(',', '').replace('$', '').strip()
                            matched_val = float(clean_val)
                            break
                        except (ValueError, TypeError):
                            pass
                col_vals.append(matched_val)

            data_dict[col_label] = col_vals

        df_result = pd.DataFrame(data_dict)
        return df_result

    except Exception:
        return None

def fetch_stock_financials_yfinance(symbol: str) -> Tuple[Optional[pd.DataFrame], str]:
    try:
        ticker = yf.Ticker(symbol.upper())
        financials = ticker.financials
        balance_sheet = ticker.balance_sheet
        
        if financials is None or financials.empty:
            return None, f"No financial statements found for symbol '{symbol.upper()}'."
            
        years_cols = [str(col.year) for col in financials.columns[:3]]
        if len(years_cols) < 2:
            return None, f"Insufficient annual financial statements data for symbol '{symbol.upper()}'."

        def find_row_val(df_source, keywords, col_idx):
            if df_source is None or df_source.empty:
                return 0.0
            for idx in df_source.index:
                for kw in keywords:
                    if kw.lower() in str(idx).lower():
                        try:
                            val = df_source.loc[idx].iloc[col_idx]
                            if pd.notna(val):
                                return float(val)
                        except Exception:
                            pass
            return 0.0

        data = {"Metric": [m[0] for m in METRICS_ENGLISH_LABELS]}
        years_cols_sorted = sorted(years_cols)
        
        for yr_str in years_cols_sorted:
            orig_col_idx = [i for i, c in enumerate(financials.columns) if str(c.year) == yr_str][0]
            col_vals = []
            for item_label, kw_list in METRICS_ENGLISH_LABELS:
                val = find_row_val(financials, kw_list, orig_col_idx)
                if val == 0.0 and balance_sheet is not None and not balance_sheet.empty:
                    val = find_row_val(balance_sheet, kw_list, orig_col_idx)
                col_vals.append(val)
            data[f"Year {yr_str}"] = col_vals

        df_res = pd.DataFrame(data)
        return df_res, f"Successfully extracted annual financial statements for '{symbol.upper()}'."

    except Exception as e:
        return None, f"Error fetching financial statements for '{symbol.upper()}': {str(e)}"

def create_sample_3yr_financial_data() -> pd.DataFrame:
    data = {
        "Metric": [m[0] for m in METRICS_ENGLISH_LABELS],
        "Year 2022": [1000000, 600000, 400000, 150000, 250000, 180000, 2000000, 800000, 300000, 150000, 250000, 900000, 400000, 300000, 1100000],
        "Year 2023": [1250000, 720000, 530000, 180000, 350000, 260000, 2400000, 1000000, 420000, 180000, 280000, 1050000, 450000, 350000, 1350000],
        "Year 2024": [1550000, 880000, 670000, 210000, 460000, 350000, 2900000, 1250000, 550000, 220000, 310000, 1200000, 500000, 400000, 1700000]
    }
    return pd.DataFrame(data)

def analyze_financial_ratios(df: pd.DataFrame) -> Dict[str, Any]:
    years = [col for col in df.columns if col != df.columns[0]]
    if len(years) < 2:
        return {}

    df_clean = df.set_index(df.columns[0])

    def get_val(item_keywords, yr_idx):
        for idx in df_clean.index:
            for kw in item_keywords:
                if kw.lower() in str(idx).lower():
                    try:
                        v = float(df_clean.loc[idx].iloc[yr_idx])
                        return v if not np.isnan(v) else 0.0
                    except Exception:
                        pass
        return 0.0

    ratios_by_year = {}

    for idx_yr, yr in enumerate(years):
        rev = get_val(["revenue", "sales"], idx_yr)
        cogs = get_val(["cogs", "cost of goods"], idx_yr)
        gross_profit = get_val(["gross profit"], idx_yr) or (rev - cogs if rev else 0.0)
        opex = get_val(["opex", "operating expenses"], idx_yr)
        ebit = get_val(["ebit", "operating income"], idx_yr) or (gross_profit - opex if gross_profit else 0.0)
        net_income = get_val(["net income", "net profit"], idx_yr)
        
        assets = get_val(["total assets"], idx_yr)
        curr_assets = get_val(["current assets"], idx_yr)
        cash = get_val(["cash"], idx_yr)
        receivables = get_val(["receivable"], idx_yr)
        inventory = get_val(["inventory"], idx_yr)
        
        liab = get_val(["total liabilities"], idx_yr)
        curr_liab = get_val(["current liabilities"], idx_yr)
        debt = get_val(["total debt"], idx_yr) or liab
        equity = get_val(["equity", "shareholders"], idx_yr) or (assets - liab if assets else 0.0)

        gross_margin = (gross_profit / rev * 100.0) if rev > 0 else 0.0
        ebit_margin = (ebit / rev * 100.0) if rev > 0 else 0.0
        net_margin = (net_income / rev * 100.0) if rev > 0 else 0.0
        roa = (net_income / assets * 100.0) if assets > 0 else 0.0
        roe = (net_income / equity * 100.0) if equity > 0 else 0.0

        current_ratio = (curr_assets / curr_liab) if curr_liab > 0 else 0.0
        quick_ratio = ((curr_assets - inventory) / curr_liab) if curr_liab > 0 else 0.0
        cash_ratio = (cash / curr_liab) if curr_liab > 0 else 0.0

        debt_to_equity = (liab / equity) if equity > 0 else 0.0
        debt_to_assets = (liab / assets) if assets > 0 else 0.0
        
        asset_turnover = (rev / assets) if assets > 0 else 0.0
        inventory_turnover = (cogs / inventory) if inventory > 0 else 0.0

        ratios_by_year[yr] = {
            "Revenue": round(rev, 2),
            "Gross Profit": round(gross_profit, 2),
            "EBIT": round(ebit, 2),
            "Net Income": round(net_income, 2),
            "Gross Margin (%)": round(gross_margin, 2),
            "EBIT Margin (%)": round(ebit_margin, 2),
            "Net Profit Margin (%)": round(net_margin, 2),
            "ROA - Return on Assets (%)": round(roa, 2),
            "ROE - Return on Equity (%)": round(roe, 2),
            "Current Ratio": round(current_ratio, 2),
            "Quick Ratio": round(quick_ratio, 2),
            "Cash Ratio": round(cash_ratio, 2),
            "Debt to Equity": round(debt_to_equity, 2),
            "Debt to Assets": round(debt_to_assets, 2),
            "Asset Turnover": round(asset_turnover, 2),
            "Inventory Turnover": round(inventory_turnover, 2)
        }

    rev_trend = [ratios_by_year[y]["Revenue"] for y in years]
    net_trend = [ratios_by_year[y]["Net Income"] for y in years]

    if len(years) >= 2 and rev_trend[0] > 0 and rev_trend[-1] > 0:
        n_periods = len(years) - 1
        g_rev = (rev_trend[-1] / rev_trend[0]) ** (1.0 / n_periods) - 1.0
    else:
        g_rev = 0.12

    if len(years) >= 2 and net_trend[0] > 0 and net_trend[-1] > 0:
        n_periods = len(years) - 1
        g_net = (net_trend[-1] / net_trend[0]) ** (1.0 / n_periods) - 1.0
    else:
        g_net = 0.15

    g_rev = max(-0.5, min(1.0, g_rev))
    g_net = max(-0.5, min(1.0, g_net))

    next_rev_proj = rev_trend[-1] * (1.0 + g_rev)
    next_net_proj = net_trend[-1] * (1.0 + g_net)

    avg_net_margin = float(np.mean([ratios_by_year[y]["Net Profit Margin (%)"] for y in years]))
    avg_roe = float(np.mean([ratios_by_year[y]["ROE - Return on Equity (%)"] for y in years]))
    avg_current_ratio = float(np.mean([ratios_by_year[y]["Current Ratio"] for y in years]))

    forecast_next_year = {
        "Projected Revenue": round(next_rev_proj, 2),
        "Projected Net Income": round(next_net_proj, 2),
        "Revenue CAGR / Growth Rate (%)": round(g_rev * 100.0, 2),
        "Net Income CAGR / Growth Rate (%)": round(g_net * 100.0, 2),
        "Estimated Net Profit Margin (%)": round(avg_net_margin, 2),
        "Estimated ROE (%)": round(avg_roe, 2),
        "Projected Current Ratio": round(avg_current_ratio, 2)
    }

    return {
        "ratios_by_year": ratios_by_year,
        "forecast_next_year": forecast_next_year,
        "historical_revenue_trend": rev_trend,
        "historical_net_profit_trend": net_trend,
        "years": years
    }

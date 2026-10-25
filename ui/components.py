import streamlit as st
from datetime import datetime, timezone, timedelta

def render_header(title: str, subtitle: str = ""):
    # Egypt Cairo Local Time (UTC+3)
    cairo_now = datetime.now(timezone.utc) + timedelta(hours=3)
    now_time = cairo_now.strftime("%I:%M:%S %p") + " (توقيت القاهرة)"
    st.markdown(f'''
        <div style="background: #1E2329; padding: 22px; border-radius: 8px; border: 1px solid #2B313A; border-left: 6px solid #F0B90B; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="color: #F0B90B; margin:0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px;">{title}</h2>
                    <p style="color: #848E9C; margin: 6px 0 0 0; font-size: 13px; font-weight: 400;">{subtitle}</p>
                </div>
                <div style="background: rgba(240, 185, 11, 0.1); border: 1px solid #F0B90B; color: #F0B90B; padding: 6px 14px; border-radius: 4px; font-weight: 600; font-size: 12px; display: flex; align-items: center; gap: 6px;">
                    <span style="height: 8px; width: 8px; background-color: #0ECB81; border-radius: 50%; display: inline-block;"></span>
                    LIVE FEED • {now_time}
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

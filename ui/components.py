import streamlit as st
from datetime import datetime, timezone, timedelta

def render_header(title: str, subtitle: str = "", is_ar: bool = True):
    # Egypt Cairo Local Time (UTC+3)
    cairo_now = datetime.now(timezone.utc) + timedelta(hours=3)
    if is_ar:
        now_time = cairo_now.strftime("%I:%M:%S %p") + " (توقيت القاهرة)"
        badge_text = f"بث مباشر • {now_time}"
    else:
        now_time = cairo_now.strftime("%I:%M:%S %p") + " (Cairo Time)"
        badge_text = f"LIVE FEED • {now_time}"

    st.markdown(f'''
        <div style="background: #1E2329; padding: 22px; border-radius: 8px; border: 1px solid #363C4E; border-left: 6px solid #F0B90B; margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="color: #F0B90B; margin:0; font-size: 26px; font-weight: 700; letter-spacing: -0.3px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">{title}</h2>
                    <p style="color: #FFFFFF; margin: 6px 0 0 0; font-size: 15px; font-weight: 500; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">{subtitle}</p>
                </div>
                <div style="background: rgba(240, 185, 11, 0.15); border: 1px solid #F0B90B; color: #F0B90B; padding: 8px 16px; border-radius: 6px; font-weight: 700; font-size: 13px; display: flex; align-items: center; gap: 8px; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                    <span style="height: 10px; width: 10px; background-color: #0ECB81; border-radius: 50%; display: inline-block;"></span>
                    {badge_text}
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

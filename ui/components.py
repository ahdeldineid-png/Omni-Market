import streamlit as st
from datetime import datetime, timezone

def render_header(title: str, subtitle: str = ""):
    now_time = datetime.now().strftime("%I:%M:%S %p")
    st.markdown(f'''
        <div style="background: linear-gradient(135deg, #111827 0%, #1F2937 100%); padding: 22px; border-radius: 12px; border: 1px solid #374151; border-left: 6px solid #00FF87; box-shadow: 0 10px 25px -5px rgba(0, 255, 135, 0.1); margin-bottom: 24px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <h2 style="color: #F9FAFB; margin:0; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;">{title}</h2>
                    <p style="color: #9CA3AF; margin: 6px 0 0 0; font-size: 14px; font-weight: 400;">{subtitle}</p>
                </div>
                <div style="background: rgba(0, 255, 135, 0.1); border: 1px solid #00FF87; color: #00FF87; padding: 6px 14px; border-radius: 20px; font-weight: 600; font-size: 13px; display: flex; align-items: center; gap: 6px;">
                    <span style="height: 8px; width: 8px; background-color: #00FF87; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #00FF87;"></span>
                    LIVE FEED • {now_time}
                </div>
            </div>
        </div>
    ''', unsafe_allow_html=True)

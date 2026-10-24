import streamlit as st

def render_header(title: str, subtitle: str = ""):
    st.markdown(f'''
        <div style="background-color: #1E222D; padding: 18px; border-radius: 10px; border-right: 6px solid #00E676; border-left: 6px solid #00E676; margin-bottom: 22px;">
            <h2 style="color: #FFFFFF; margin:0; font-size: 24px;">{title}</h2>
            <p style="color: #00E676; margin:6px 0 0 0; font-size: 14px;">{subtitle}</p>
        </div>
    ''', unsafe_allow_html=True)

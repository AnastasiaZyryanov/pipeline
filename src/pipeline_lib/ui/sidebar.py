import streamlit as st

def show_sidebar():
    with st.sidebar:
        selected_module = st.radio("Pipeline modules", list(st.session_state.config.keys()))
    return selected_module
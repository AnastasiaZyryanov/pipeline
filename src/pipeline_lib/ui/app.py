import streamlit as st
import json
from pipeline_lib.config.state import ConfigurationState
from pipeline_lib.config.validator import validate_config
from pipeline_lib.config.io import save_config
from pipeline_lib.ui.sidebar import show_sidebar
from pipeline_lib.ui.module_editor import show_module

st.title("Pipeline Configuration")
mode = st.radio("Configuration source", ["Create new configuration", "Load existing configuration"])
st.write("Selected:", mode)

if mode == "Load existing configuration":
    uploaded_file = st.file_uploader("Choose JSON file", type="json")
    if uploaded_file is not None:

        if "config" not in st.session_state:
            data = json.load(uploaded_file)
            validate_config(data)
            st.session_state.config = data

        cfg = st.session_state.config

        selected_module = show_sidebar()

        show_module(selected_module, cfg)

        try:
            validate_config(cfg)
            st.success("Configuration is valid")
        except Exception as e:
            st.error(str(e))

        st.download_button(
            "Download configuration",
            data=json.dumps(cfg, indent=2),
            file_name="config_copy.json",
            mime="application/json"
        )
else:
    st.info("Manual configuration not implemented yet")
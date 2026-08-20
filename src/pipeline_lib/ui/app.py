import streamlit as st
import pandas as pd
import json
import hashlib
from pipeline_lib.config.io import save_config
from pipeline_lib.ui.sidebar import render_sidebar_controls, render_module_selector
from pipeline_lib.ui.module_editor import show_module
from pipeline_lib.config.schema_utils import get_module_schema, get_available_types


st.title("Pipeline Configuration")
mode = st.radio("Configuration source", ["Create new configuration", "Load existing configuration"], key="configuration_mode")

if st.session_state.get("previous_mode") != mode:
    st.session_state.config = {}
    st.session_state.config_version = st.session_state.get("config_version", 0) + 1
    st.session_state.previous_mode = mode
    st.session_state.loaded_file_hash = None
    st.session_state.original_config_json = json.dumps({}, sort_keys=True)

if mode == "Load existing configuration":
    uploaded_file = st.file_uploader("Choose JSON file", type="json")
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        file_hash = hashlib.md5(file_bytes).hexdigest()
        if st.session_state.get("loaded_file_hash") != file_hash:
            try:
                data = json.loads(file_bytes)
                st.session_state.config = data
                st.session_state.loaded_file_hash = file_hash
                st.session_state.config_version += 1
                st.session_state.original_config_json = json.dumps(data, sort_keys=True)
                st.success("Configuration loaded successfully!")
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON: {e}")
                st.stop()
    else:
        st.info("Please upload a JSON configuration file to start editing.")
        st.stop()   
if "config" not in st.session_state:
    st.session_state.config = {}
if "original_config_json" not in st.session_state:
    st.session_state.original_config_json = json.dumps({}, sort_keys=True)

cfg = st.session_state.config
for module_name in ["Chunker", "Cleaner", "SentimentAnalyzer", "KeywordExtractor"]:
    if module_name not in cfg:
        cfg[module_name] = {}
    if "type" not in cfg[module_name]:
        schema = get_module_schema(module_name)
        available = get_available_types(schema)
        if available:
            cfg[module_name]["type"] = available[0]
selected_module = render_module_selector()
show_module(selected_module, cfg, st.session_state.config_version, mode)
current_json = json.dumps(cfg, sort_keys=True)
has_changes = (current_json != st.session_state.get("original_config_json", ""))
input_file = render_sidebar_controls(cfg, has_changes, mode)

if st.session_state.get("run_clicked", False):
    st.session_state.run_clicked = False
    try:
        df = pd.read_csv(input_file)
        from pipeline_lib.core.builder import build_pipeline
        pipeline = build_pipeline(cfg)
        result = pipeline.run(df)
        st.session_state.result_json = result.to_json(orient="records",lines=True, index=False)
        st.session_state.pipeline_completed = True

    except Exception as e:
        st.session_state.pipeline_completed = False
        st.error(f"Pipeline execution failed: {e}")

if st.session_state.get("pipeline_completed", False):
    with st.sidebar:
        st.success("Pipeline completed successfully.")
        st.download_button(
            "Download result",
            data=st.session_state.result_json,
            file_name="output.json",
            mime="application/json",
            use_container_width=True
        )
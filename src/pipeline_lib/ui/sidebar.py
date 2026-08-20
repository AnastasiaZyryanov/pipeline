import streamlit as st
import json
from pipeline_lib.config.schema import PIPELINE_SCHEMA
from pipeline_lib.config.validator import validate_config
from pipeline_lib.ui.module_editor import get_validation_errors

def render_module_selector():
    with st.sidebar:
        module_names = list(PIPELINE_SCHEMA["properties"].keys())

        return st.radio(
            "Pipeline modules",
            module_names,
            index=0,
            key="module_selector"
        )

def render_sidebar_controls(cfg, has_changes, mode):
    with st.sidebar:       
        errors = []
        if cfg:
            try:
                errors=show_validation_summary(cfg)                
            except ValueError as e:
                errors = [str(e)]            
        else:
            st.info("Add modules to build your pipeline configuration.")

        if cfg and has_changes:
            save_disabled = bool(errors)
            st.download_button(
                label="Save changes" if mode == "Load existing configuration" else "Download configuration",
                data=json.dumps(cfg, indent=2),
                file_name="config.json",
                mime="application/json",
                disabled=save_disabled,
                type="secondary",
                use_container_width=True
            )

        st.divider()

        input_file = st.file_uploader("Choose input CSV file", type="csv", key="csv_uploader")
        if input_file is not None:
            st.success("CSV file loaded successfully.")
        else:
            st.info("Please select an input CSV file.")

        run_disabled = bool(errors) or not cfg or input_file is None
        if st.button("Run pipeline", type="secondary", disabled=run_disabled, use_container_width=True):
            st.session_state.run_clicked = True
    return input_file
        

import streamlit as st

def show_validation_summary(config):
    errors = get_validation_errors(config)  
    if not errors:
        st.success("All modules are valid")
        return
    
    modules_with_errors = set()
    for error in errors:
        if error.path:
            module_name = error.path[0]
            if isinstance(module_name, str):
                modules_with_errors.add(module_name)
        else:
            modules_with_errors.add("Global configuration")
    
    st.error("Configuration contains errors in:")
    for module in sorted(modules_with_errors):
        st.write(f"- **{module}**")
    st.caption("Check each module tab for details.")
    return errors
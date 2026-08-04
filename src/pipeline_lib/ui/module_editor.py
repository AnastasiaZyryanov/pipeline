import streamlit as st
from ..config.schema_utils import *

def show_parameter(module_name, parameter, parameter_schema, cfg):
    value = cfg.get(parameter)
    parameter_schema = resolve_schema(parameter_schema)
    field_type = parameter_schema.get("type")       
    if field_type=="string":
        if "enum" in parameter_schema:
            options = parameter_schema["enum"]
            if value is None:
                value = options[0]
                cfg[parameter] = st.selectbox(
                parameter,
                options,
                index=options.index(value),
                key=f"{module_name}_{parameter}"
            )
        else:
            cfg[parameter] = st.text_input(
            parameter,
            value="" if value is None else value,
            key=f"{module_name}_{parameter}"
             )        
    elif field_type == "object":
        st.subheader(parameter)
        nested_cfg = cfg.setdefault(parameter, {})
        for child_name, child_schema in parameter_schema["properties"].items():
            show_parameter(
                module_name,
                child_name,
                child_schema,
                nested_cfg
            )  
    elif field_type == "integer":
        cfg[parameter] = st.number_input(
            parameter,
            value=0 if value is None else value,
            step=1,
            key=f"{module_name}_{parameter}"
        )
    elif field_type == "number":
        cfg[parameter] = st.number_input(
            parameter,
            value=0.0 if value is None else float(value),
            key=f"{module_name}_{parameter}"
        )
    elif field_type == "boolean":
        cfg[parameter] = st.checkbox(
            parameter,
            value=False if value is None else value,
            key=f"{module_name}_{parameter}"
        )
    elif "const" in parameter_schema:
        cfg[parameter] = parameter_schema["const"]
        st.text_input(
            parameter,
            value=parameter_schema["const"],
            disabled=True,
            key=f"{module_name}_{parameter}"
        )
    elif "oneOf" in parameter_schema:
        if not parameter_schema["oneOf"]:
            st.warning(f"{parameter} has empty oneOf")
            return
        show_oneof(module_name,parameter, parameter_schema, cfg)
    else:
     st.info(f"{parameter}: type not implemented")

def show_module(module_name, config):
    st.header(module_name)
    cfg = config[module_name]
    module_schema = get_module_schema(module_name)
    available = get_available_types(module_schema)
    selected_type = st.selectbox("Type", available, index=available.index(cfg["type"]), key=f"{module_name}_type_selector")
    if selected_type != cfg["type"]:
        config[module_name] = {
            "type": selected_type
        }
        st.rerun()
    selected_schema = get_schema_for_type(module_schema, selected_type)
    properties = get_properties(selected_schema)    
    
    for parameter, parameter_schema in properties.items():
        if parameter == "type":
            continue
        show_parameter(
        module_name,
        parameter,
        parameter_schema,
        cfg
    )        
    st.divider()
    st.json(cfg)

def show_oneof(module_name,parameter,parameter_schema,cfg):
    parameter_schema = resolve_schema(parameter_schema)
    available = get_available_types(parameter_schema)
    if not available:
        st.error(f"{parameter}: no variants found (oneOf missing)")
        return
    nested_cfg = cfg.setdefault(parameter, {})
    current = nested_cfg.get("type", available[0])
    selected = st.selectbox(parameter,available,index=available.index(current),key=f"{module_name}_{parameter}")
    if current != selected:
        nested_cfg.clear()
        nested_cfg["type"] = selected
        st.rerun()
    selected_schema = get_schema_for_type(parameter_schema, selected)
    properties = get_properties(selected_schema)

    for child, child_schema in properties.items():
        if child == "type":
            continue
        show_parameter(module_name,child,child_schema,nested_cfg)



    
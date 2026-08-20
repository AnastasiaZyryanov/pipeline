import streamlit as st
from ..config.schema_utils import *
from jsonschema import Draft7Validator
from ..config.schema import PIPELINE_SCHEMA


def show_parameter(path, parameter, parameter_schema, cfg, required=False, config_version=0):        
    parameter_schema = resolve_schema(parameter_schema)
    value = cfg.get(parameter)
    field_type = parameter_schema.get("type")    
    key = f"{config_version}.{path}.{parameter}" 
    label=f"{parameter} *" if required else parameter 
    help_text=parameter_schema.get("description", "")    
    if "const" in parameter_schema:
        show_const_parameter(label, key, parameter_schema["const"], cfg, parameter, help=help_text)
    elif "oneOf" in parameter_schema:
        show_oneof(path, parameter, parameter_schema, cfg, config_version, help=help_text)
    elif field_type == "object":
        show_object(path, parameter, parameter_schema, cfg, config_version, help=help_text)
    elif field_type == "string":
        show_string_parameter(label, key, value, cfg, parameter, parameter_schema, required, help=help_text)
    elif field_type == "integer":
        show_numeric_parameter(label, key, value, cfg, parameter, required, int, help=help_text)
    elif field_type == "number":
        show_numeric_parameter(label, key, value, cfg, parameter, required, float, help=help_text)
    elif field_type == "boolean":
        show_boolean_parameter(label,key,value,cfg,parameter,required, help=help_text)
    elif field_type == "array":
        show_array_parameter (path,parameter,cfg,required,config_version, help=help_text)
    else:
        st.info(f"{parameter}: type not implemented")

def show_module(module_name, config, config_version, mode):
    st.header(module_name)
    module_schema = get_module_schema(module_name)
    available = get_available_types(module_schema)
    if module_name not in config:
        if mode == "Create new configuration":
            config[module_name] = {
                "type": available[0]
            }
            st.rerun()
        else:
            st.warning("This module is not configured yet.")
            st.info("You can create its configuration here.")
            return
    cfg = config[module_name]
    selected_type = st.selectbox(
        "Type",
        available,
        index=available.index(cfg["type"]),
        key=f"{config_version}.{module_name}.type"
    )
    if selected_type != cfg["type"]:
        config[module_name] = {
            "type": selected_type
        }
        st.rerun()
    selected_schema = get_schema_for_type(
        module_schema,
        selected_type
    )
    properties = get_properties(selected_schema)
    required = selected_schema.get("required", [])

    for parameter, parameter_schema in properties.items():
        if parameter == "type":
            continue
        show_parameter(
            module_name,
            parameter,
            parameter_schema,
            cfg,
            required=parameter in required,
            config_version=config_version
        )

    st.divider()
    errors = validate_module(module_name, cfg)
    if errors:
        st.error("This module contains validation errors.")

        for error in errors:
            st.error(format_error_for_user(error))
    else:
        st.success("This module is valid.")

def validate_module(module_name, cfg):
    module_schema = {
        **PIPELINE_SCHEMA,
        "properties": {
            module_name: PIPELINE_SCHEMA["properties"][module_name]
        },
        "required": [module_name]
    }
    validator = Draft7Validator(module_schema)
    errors = list(validator.iter_errors({module_name: cfg}))
    return errors

def get_validation_errors(data: dict):
     validator = Draft7Validator(PIPELINE_SCHEMA)
     return list(validator.iter_errors(data))

def format_error_for_user(error) -> str:
    path = ".".join(str(p) for p in error.path)
    if not path:
        path = "module configuration"   
    if error.validator == "required":
        missing = ", ".join(error.validator_value)
        return f"Missing required field(s) in **{path}**: {missing}"    
    if error.validator == "type":
        expected = error.validator_value
        actual = error.instance
        return f"Field **{path}** must be of type **{expected}**, got `{actual}`"    
    if error.validator == "enum":
        allowed = ", ".join(str(v) for v in error.validator_value)
        return f"Field **{path}** must be one of: {allowed}"    
    if error.validator in ("oneOf", "anyOf"):
        instance = error.instance
        if "type" in instance:
            chosen = instance["type"]
            return (f"Configuration for selected type **{chosen}** is invalid.\n"
                    f"Please ensure all required fields for this type are filled in.")
        else:
            return f"No type selected (or the selected type is not supported)."
    
    return f"Error in field **{path}**: {error.message}"

def update_parameter(cfg, parameter, value, required=False):
    if value is None or value == "":
        cfg.pop(parameter, None)
        if required:
            st.error("Required — please specify a value")
    else:
        cfg[parameter] = value

def show_object(path,parameter,parameter_schema,cfg, config_version=0, help=""):
    with st.container(border=True):
        st.markdown(f"**{parameter}**")
        if help:
            st.caption(help)
        nested_cfg = cfg.setdefault(parameter, {})
        required_parameters = parameter_schema.get("required", [])
        for child_name, child_schema in parameter_schema["properties"].items():
            show_parameter(f"{path}.{parameter}", child_name, child_schema, nested_cfg, required=child_name in required_parameters, config_version=config_version)

def show_numeric_parameter(label,key,value,cfg,parameter,required,converter, help=""):
    text_value = st.text_input(label, value="" if value is None else str(value),key=key, help=help)
    if text_value == "":
        cfg.pop(parameter, None)
        if required:
            st.error("Required — please specify a value")
        return
    try:
        cfg[parameter] = converter(text_value)
    except ValueError:
        st.error(f"{parameter} has an invalid value")

def show_string_parameter(label,key,value,cfg,parameter,parameter_schema, required, help=""):
    if "enum" in parameter_schema:
        options = parameter_schema["enum"]
        if not required:
            options = ["<not specified>"] + options
        if value is None:
            index = 0
        else:
            index = options.index(value)
        new_value = st.selectbox(label,options,index=index,key=key, help=help)
        if new_value == "<not specified>":
            cfg.pop(parameter, None)
        else:
            cfg[parameter] = new_value
    else:
        new_value = st.text_input(label, value="" if value is None else value, key=key, help=help)

        update_parameter(cfg, parameter, new_value, required)

def show_boolean_parameter(label,key,value,cfg,parameter, required=False, help=""):    
    if required:
        new_value = st.checkbox(label, value=False if value is None else value, key=key, help=help)
        cfg[parameter] = new_value
    else:
        options = ["<not specified>", "True", "False"]
        if value is None:
            index = 0
        elif value is True:
            index = 1
        else:
            index = 2

        new_value = st.selectbox(label, options, index=index, key=key, help=help)
        if new_value == "<not specified>":
            cfg.pop(parameter, None)
        elif new_value == "True":
            cfg[parameter] = True
        else:
            cfg[parameter] = False

def show_const_parameter(label,key,value,cfg,parameter, help=""):
    cfg[parameter] = value
    st.text_input(label, value=value, disabled=True, key=key, help=help)

def show_oneof(path, parameter, parameter_schema, cfg, config_version=0, help=""):
    parameter_schema = resolve_schema(parameter_schema)
    available = get_available_types(parameter_schema)
    if not available:
        st.error(f"{parameter}: no variants found")
        return

    with st.container(border=True):
        st.markdown(f"**{parameter}**")  
        if help:
            st.caption(help)

        nested_cfg = cfg.setdefault(parameter, {})
        current = nested_cfg.get("type")
        if current not in available:
            current = available[0]
        key = f"{config_version}.{path}.{parameter}"
        selected = st.selectbox(
            "Type",  
            available,
            index=available.index(current),
            key=key
        )
        if selected != current:
            nested_cfg.clear()
            nested_cfg["type"] = selected
            st.rerun()

        selected_schema = get_schema_for_type(parameter_schema, selected)
        properties = get_properties(selected_schema)
        required_parameters = selected_schema.get("required", [])

        for child, child_schema in properties.items():
            if child == "type":
                continue            
            show_parameter(
                f"{path}.{parameter}",
                child,
                child_schema,
                nested_cfg,
                required=child in required_parameters,
                config_version=config_version
            )



def show_array_parameter(path, parameter, cfg, required=False, config_version=0, help=""):
    values = cfg.get(parameter, [])
    with st.container(border=True):
        st.markdown(f"**{parameter}**")

        for i, value in enumerate(values):
            col1, col2 = st.columns([0.8, 0.2])
            key_edit = f"{config_version}.{path}.{parameter}.{i}"

            with col1:
                new_val = st.text_input(
                    f"Item {i+1}",
                    value=value if value is not None else "",
                    key=key_edit,
                    label_visibility="collapsed",
                    help=help
                )
                values[i] = new_val

            with col2:
                if st.button("✕", key=f"{config_version}.{path}.{parameter}.remove.{i}"):
                    values.pop(i)
                    cfg[parameter] = values
                    if key_edit in st.session_state:
                        del st.session_state[key_edit]
                    st.rerun()
        array_version_key = f"{path}.{parameter}.array_version"
        if array_version_key not in st.session_state:
            st.session_state[array_version_key] = 0
        new_item_key = (f"{config_version}.{path}.{parameter}."f"new.{st.session_state[array_version_key]}")
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            new_value = st.text_input(
                "New item",           
                placeholder="Add new element",
                key=new_item_key,
                label_visibility="collapsed", 
                help=help           
            )

        with col2:
            if st.button("Add", key=f"{config_version}.{path}.{parameter}.add"):
                if new_value.strip():
                    values.append(new_value.strip())
                    cfg[parameter] = values
                    st.session_state[array_version_key] += 1
                    st.rerun()

        if values:
            cfg[parameter] = values
        elif not required:
            cfg.pop(parameter, None)
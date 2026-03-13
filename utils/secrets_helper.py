import os

import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


def get_secret_value(section: str, key: str, env_var: str | None = None, default=None):
    """Read from st.secrets when available, fallback to environment variable."""
    try:
        section_data = st.secrets.get(section, {})
        if isinstance(section_data, dict):
            value = section_data.get(key)
            if value not in (None, ""):
                return value
    except (StreamlitSecretNotFoundError, FileNotFoundError, KeyError, AttributeError):
        pass

    if env_var:
        return os.environ.get(env_var, default)
    return default

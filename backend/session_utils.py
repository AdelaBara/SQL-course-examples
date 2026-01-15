import os
from pathlib import Path

import oracledb
import streamlit as st
from streamlit.errors import StreamlitSecretNotFoundError


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"


def _load_env_file():
    if not ENV_PATH.exists():
        return
    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


# Direct Oracle connection (for raw cursor-based queries)
def _get_oracle_config():
    try:
        if "oracle" in st.secrets:
            return st.secrets["oracle"]
    except StreamlitSecretNotFoundError:
        pass
    _load_env_file()
    return {
        "user": os.getenv("ORACLE_USER"),
        "password": os.getenv("ORACLE_PASSWORD"),
        "dsn": os.getenv("ORACLE_DSN"),
    }


def get_oracle_connection():
    if "oracle_conn" not in st.session_state:
        config = _get_oracle_config()
        conn = oracledb.connect(
            user=config["user"],
            password=config["password"],
            dsn=config["dsn"],
        )
        st.session_state.oracle_conn = conn
    return st.session_state.oracle_conn

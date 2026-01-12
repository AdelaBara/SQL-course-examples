import os

import oracledb
import streamlit as st


# Direct Oracle connection (for raw cursor-based queries)
def _get_oracle_config():
    if "oracle" in st.secrets:
        return st.secrets["oracle"]
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

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.session_utils import get_oracle_connection


ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "SQL examples"
INTERPRETED_PATH = SQL_DIR / "complex_queries_interpreted.json"


def load_queries(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def run_query(sql_text: str, connection):
    cleaned = sql_text.strip().rstrip(";")
    if not cleaned:
        return None
    if cleaned.lower().startswith(("select", "with")):
        return pd.read_sql(cleaned, con=connection)
    cursor = connection.cursor()
    try:
        cursor.execute(cleaned)
        connection.commit()
    finally:
        cursor.close()
    return None


st.set_page_config(page_title="SQL Lab", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&family=IBM+Plex+Mono:wght@400;600&display=swap');

    :root {
        --bg-1: #0b1220;
        --bg-2: #0f1b2d;
        --card: #121a2b;
        --accent: #f8d56a;
        --accent-2: #7cd4ff;
        --text: #ffffff;
        --muted: #b7c0cc;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 10% 0%, #15253a 0%, transparent 60%),
                    radial-gradient(900px 500px at 90% 10%, #1a2a40 0%, transparent 55%),
                    linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
        color: var(--text);
        font-family: "Space Grotesk", sans-serif;
    }

    .hero {
        padding: 24px 28px;
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(248, 213, 106, 0.15), rgba(124, 212, 255, 0.1));
        border: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 18px;
    }

    .hero-title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 6px;
        letter-spacing: 0.3px;
    }

    .hero-subtitle {
        color: var(--muted);
        font-size: 16px;
    }

    .chip {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(124, 212, 255, 0.18);
        color: var(--text);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.4px;
        text-transform: uppercase;
        margin-right: 8px;
    }

    .panel {
        padding: 16px 18px;
        border-radius: 16px;
        background: var(--card);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.25);
    }

    .panel h3 {
        margin-bottom: 8px;
        font-size: 18px;
        font-weight: 600;
    }

    .stTextArea textarea {
        font-family: "IBM Plex Mono", monospace;
        font-size: 14px;
        background: #0f1626;
        color: #ffffff;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.08);
    }

    .stSelectbox, .stButton button {
        font-family: "Space Grotesk", sans-serif;
    }

    .stSelectbox label {
        color: var(--text);
    }

    .stTextArea label {
        color: var(--text);
    }

    .stButton button {
        background: linear-gradient(90deg, var(--accent), #ffd88f);
        color: #2c2007;
        border-radius: 999px;
        border: none;
        font-weight: 700;
    }

    .stButton button:hover {
        filter: brightness(1.05);
    }
    </style>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div class="hero">
        <span class="chip">SQL Lab</span>
        <span class="chip">Oracle</span>
        <div class="hero-title">SQL query playground for students</div>
        <div class="hero-subtitle">Pick a challenge, read the explanation, tweak the SQL, and see results instantly.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Schema image", expanded=False):
    schema_path = SQL_DIR / "schemaBD.png"
    if schema_path.exists():
        st.image(str(schema_path), caption="Schema overview", use_container_width=True)
    else:
        st.info("Schema image not found.")

st.markdown("""-----""")
queries = load_queries(INTERPRETED_PATH)
categories = sorted({q["category"] for q in queries})
category_filter = st.selectbox("Choose SQL category", ["All"] + categories)
if category_filter != "All":
    queries = [q for q in queries if q["category"] == category_filter]
st.subheader("Examples")
selected_id = st.selectbox(
    "Pick an example to run",
    [q["id"] for q in queries],
    format_func=lambda qid: f"#{qid}: {next(q['request'] for q in queries if q['id'] == qid)}",
)
selected_query = next(q for q in queries if q["id"] == selected_id)

if st.session_state.get("selected_id") != selected_id:
    st.session_state["selected_id"] = selected_id
    st.session_state["editor_sql"] = selected_query["sql"]

st.markdown("### Explanation:")
st.markdown(selected_query.get("explanation", ""))
sql_text = st.text_area(
    "SQL to run",
    value=st.session_state.get("editor_sql", ""),
    height=200,
)
st.session_state["editor_sql"] = sql_text
run_example = st.button("Run SQL", type="primary")

if run_example:
    try:
        with st.spinner("Connecting to Oracle..."):
            connection = get_oracle_connection()
        result = run_query(sql_text, connection)
        if result is None:
            st.success("Statement executed.")
        else:
            st.success(f"Returned {len(result)} rows.")
            st.dataframe(result, use_container_width=True)
    except Exception as exc:
        st.error(f"Query failed: {exc}")

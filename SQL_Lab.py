import json
import textwrap
from pathlib import Path

import pandas as pd
import streamlit as st

from backend.session_utils import get_oracle_connection


ROOT = Path(__file__).resolve().parent
SQL_DIR = ROOT / "SQL examples"
SIMPLE_PATH = SQL_DIR / "simple_queries.json"
COMPLEX_PATH = SQL_DIR / "complex queries.json"


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


def format_sql_for_display(sql_text: str, width: int = 88) -> str:
    cleaned = " ".join(sql_text.strip().split())
    return "\n".join(
        textwrap.wrap(
            cleaned,
            width=width,
            break_long_words=False,
            break_on_hyphens=False,
        )
    )


st.set_page_config(page_title="SQL Lab", layout="wide")
st.title("SQL Lab")
st.caption("Run prepared SQL examples on the Oracle schema.")

connection = get_oracle_connection()

with st.expander("Schema image", expanded=False):
    schema_path = SQL_DIR / "schemaBD.png"
    if schema_path.exists():
        st.image(str(schema_path), caption="Schema overview", use_column_width=True)
    else:
        st.info("Schema image not found.")

query_sets = {
    "Simple examples": SIMPLE_PATH,
    "Complex examples": COMPLEX_PATH,
}
selected_set = st.selectbox("Choose query set", list(query_sets.keys()))
queries = load_queries(query_sets[selected_set])
st.subheader("Examples")
st.dataframe(pd.DataFrame(queries)[["id", "request"]], hide_index=True   )
left, right = st.columns(2)

with left:
    st.subheader("Examples")
    selected_id = st.selectbox(
        "Pick an example to run",
        [q["id"] for q in queries],
        format_func=lambda qid: f"#{qid}: {next(q['request'] for q in queries if q['id'] == qid)}",
    )
    selected_query = next(q for q in queries if q["id"] == selected_id)
    st.code(format_sql_for_display(selected_query["sql"]), language="sql", height=200)
    run_example = st.button("Run selected example", type="primary")

with right:
    st.subheader("Ad-hoc SQL")
    adhoc_sql = st.text_area(
        "Write your SQL",
        value="SELECT * FROM clienti",
        height=200,
    )
    run_adhoc = st.button("Run ad-hoc SQL")

if run_example:
    try:
        result = run_query(selected_query["sql"], connection)
        if result is None:
            st.success("Statement executed.")
        else:
            st.success(f"Returned {len(result)} rows.")
            st.dataframe(result, use_container_width=True)
    except Exception as exc:
        st.error(f"Query failed: {exc}")

if run_adhoc:
    try:
        result = run_query(adhoc_sql, connection)
        if result is None:
            st.success("Statement executed.")
        else:
            st.success(f"Returned {len(result)} rows.")
            st.dataframe(result, use_container_width=True)
    except Exception as exc:
        st.error(f"Query failed: {exc}")

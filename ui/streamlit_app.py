import streamlit as st, sqlite3, json, os
DB_PATH = os.getenv("DB_PATH","./adaq.db")

st.set_page_config(page_title="ADAQ-lite Trace Explorer", layout="wide")
st.title("ADAQ-lite — Trace Explorer")

def runs():
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        return c.execute("SELECT run_id, ts, latency, cost FROM runs ORDER BY ts DESC").fetchall()

def steps(run_id):
    with sqlite3.connect(DB_PATH) as c:
        c.row_factory = sqlite3.Row
        return c.execute("SELECT * FROM steps WHERE run_id=? ORDER BY n ASC",(run_id,)).fetchall()

rs = runs()
if not rs:
    st.info("No runs yet. POST /research to create one.")
else:
    rid = st.selectbox("Run", [r["run_id"] for r in rs])
    for s in steps(rid):
        st.subheader(f"Step {s['n']}")
        st.write("Queries:", json.loads(s["queries"]))
        st.write("Coverage:", json.loads(s["coverage"]))
        st.write("Notes:")
        for note in json.loads(s["notes"]):
            st.markdown(f"- **{note['summary']}** — [source]({note['source']})")

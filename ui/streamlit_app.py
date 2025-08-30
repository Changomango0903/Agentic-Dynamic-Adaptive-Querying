import streamlit as st
import requests, os

API_BASE = os.getenv("API_BASE", "http://localhost:8000")

st.set_page_config(page_title="ADAQ Trace Viewer", layout="wide")

st.title("ADAQ Trace Explorer")

trace_id = st.text_input("Trace ID")
if st.button("Load") and trace_id:
    r = requests.get(f"{API_BASE}/trace/{trace_id}")
    if r.status_code != 200:
        st.error("Trace not found")
    else:
        data = r.json()
        st.subheader(f"Question: {data['run']['question']}")
        st.caption(f"Trace: {data['run']['id']} — latency {data['run']['latency_ms']} ms")
        for step in data["steps"]:
            with st.expander(f"Step {step['n']} — decision: {step['decision']}"):
                st.write("**Queries**", step["queries"]) 
                st.write("**Notes**")
                st.write(step["notes"])
                st.write("**Coverage Δ**", step["coverage_delta"])
                st.write("**Docs**")
                for d in step["docs"]:
                    st.markdown(f"- [{d['title']}]({d['url']}) — *{d['source']}*")
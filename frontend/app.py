import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000/")

st.title("Academic Research Assistant")
st.header("Search Research Papers")

prompt = st.text_area("Enter your search query:", height=100)

if st.button("Search Papers"):
    if not prompt.strip():
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching for papers..."):
            try:
                response = requests.post(
                    f"{BACKEND_URL}agent/run",
                    json={"prompt": prompt}
                )
                if response.status_code == 200:
                    data = response.json()
                    # Display raw markdown content
                    st.markdown(data["response"], unsafe_allow_html=True)
                else:
                    st.error(f"Error: {response.status_code}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
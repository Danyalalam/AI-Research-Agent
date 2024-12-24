import streamlit as st
import requests

st.title("Academic Research Assistant")

# Search ArXiv Papers
st.header("Search ArXiv Papers")
arxiv_query = st.text_input("Enter your research query for ArXiv:")

if st.button("Search ArXiv"):
    if arxiv_query:
        response = requests.get("http://127.0.0.1:8000/search/arxiv", params={"query": arxiv_query, "max_results": 5})
        if response.status_code == 200:
            papers = response.json().get("results", [])
            st.write(f"**Found {len(papers)} papers on ArXiv:**")
            for paper in papers:
                st.write(f"**Title:** {paper['title']}")
                st.write(f"**Authors:** {', '.join(paper['authors'])}")
                if paper['url'] != 'No URL available.':
                    st.markdown(f"**URL:** [Link]({paper['url']})")
                else:
                    st.write(f"**URL:** {paper['url']}")
                st.write("---")
        else:
            st.error("Failed to fetch papers from ArXiv.")
    else:
        st.warning("Please enter a search query.")

# # Search Google Scholar Papers
# st.header("Search Google Scholar Papers")
# gs_query = st.text_input("Enter your research query for Google Scholar:")

# if st.button("Search Google Scholar"):
#     if gs_query:
#         response = requests.get("http://127.0.0.1:8000/search/google_scholar", params={"query": gs_query, "max_results": 5})
#         if response.status_code == 200:
#             papers = response.json().get("results", [])
#             st.write(f"**Found {len(papers)} papers on Google Scholar:**")
#             for paper in papers:
#                 st.write(f"**Title:** {paper['title']}")
#                 st.write(f"**Authors:** {', '.join(paper['authors'])}")
#                 if paper['url'] != 'No URL available.':
#                     st.markdown(f"**URL:** [Link]({paper['url']})")
#                 else:
#                     st.write(f"**URL:** {paper['url']}")
#                 st.write("---")
#         else:
#             st.error("Failed to fetch papers from Google Scholar.")
#     else:
#         st.warning("Please enter a search query.")

# Interact with AI Agent
st.header("Ask the AI Assistant")
agent_prompt = st.text_input("Enter your question or prompt for the AI assistant:")

if st.button("Ask AI Assistant"):
    if agent_prompt:
        response = requests.post(
            "http://127.0.0.1:8000/agent/run",
            json={"prompt": agent_prompt}  # Ensure this matches the Pydantic model
        )
        if response.status_code == 200:
            ai_response = response.json().get("response", "No response available.")
            st.write(f"**AI Assistant Response:**\n{ai_response}")
        else:
            st.error(f"Failed to get response from AI Assistant. Status Code: {response.status_code}")
    else:
        st.warning("Please enter a question or prompt.")
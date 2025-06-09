import streamlit as st
from main import answer_question
import uuid
from chat_db import log_to_mysql
st.set_page_config(page_title="TrainXar", page_icon="🤖")
if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())  # Unique ID per session

if "history" not in st.session_state:
    st.session_state.history = []

def clear_chat():
    st.session_state.history = []

with st.sidebar:
    st.button("Clear chat", on_click=clear_chat)

st.header("TrainXar QA Bot")

query = st.text_input("Ask me anything about TrainXar:", placeholder="Type your question here...")
if query.strip():
    with st.spinner("Typing..."):
        try:
            answer, sources = answer_question(query, user_id=st.session_state.user_id)

        except Exception as e:
            st.error(f"Failed to get an answer: {e}")
        else:
            st.session_state.history.append({
                "query": query,
                "answer": answer,
                "sources": sources
            })

          



for turn in st.session_state.history:
    st.markdown(f"**You:** {turn['query']}")
    st.markdown(f"**Bot:** {turn['answer']}")
  

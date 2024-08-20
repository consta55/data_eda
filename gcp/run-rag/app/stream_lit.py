import streamlit as st
import json
import requests
from render_html import render_in_browser as ren
st.title("Function Health Chatbot")

member_id = st.text_input("Please enter your member id")

user_query = st.text_input("Please enter your question here:")



inputs = {'member_id': member_id, "user_query" :user_query}


if st.button("Ask Function"):
    res = requests.post(url = "http://127.0.0.1:8000/User_query/", data = json.dumps(inputs))
    ans1 = res.text
    ans = res.text.replace('\n', ' ')
    st.subheader(f"Function Response = {ans}")
 
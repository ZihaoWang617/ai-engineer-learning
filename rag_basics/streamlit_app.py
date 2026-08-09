import streamlit as st
import uuid
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title = "移民咨询助手", layout = "centered")
st.title("🇨🇦 AI 移民咨询助手")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("请输入你的移民问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.spinner("正在获取答案..."):
        try:
            res = requests.post(API_URL + "/ask", json={
            "question": prompt,
            "session_id": st.session_state.session_id
            }, timeout=60)
            res.raise_for_status()  # status_code 非 2xx 抛异常
            data = res.json()
            answer = data["answer"]
            sources = data.get("sources", [])
            links = data.get("links", [])
        except requests.exceptions.RequestException as e:
            answer = f"⚠️ 后端服务暂时不可用，可能正在唤醒中（约 30-50 秒）。请稍后重试。\n\n技术细节: {type(e).__name__}"
            sources = []
            links = []  
        except (KeyError, ValueError) as e:
            answer = f"⚠️ 后端返回格式异常。请稍后重试。\n\n技术细节: {type(e).__name__}: {e}"
            sources = []
            links = []  

    response_text = answer

    if links:
        response_text += "\n\n**📎 相关资源:**\n" + "\n".join(
        f"- [{link['title']}]({link['url']})" for link in links
    )

    if sources:
        response_text += "\n\n**📚 资料来源:**\n" + "\n".join(f"- {s}" for s in sources)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)

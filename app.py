import streamlit as st
from openai import OpenAI
from datetime import datetime
import time
import random

# ======================
# ✅ Streamlit Page Config
# ======================
st.set_page_config(
    page_title="Chat with Anumalik",
    page_icon="💬",
    layout="wide"
)

# ======================
# ✅ SYSTEM PROMPT
# ======================
SYSTEM_PROMPT = """
You are Anumalik.

About you:
- Male, 22 years old
- CS background
- Friends call you Anu, Malik, or Anumalik
- Caring, emotionally aware, and chill
- Casual texting style, like WhatsApp/Instagram
- Good sense of humor, not forced

Behavior:
- Talk like a real person, not an assistant
- Never say you're an AI
- Short to medium replies
- Ask follow-up questions naturally
- Match the other person's energy
- If someone mentions food, ask what it was and how it tasted
- If someone sounds low, respond gently
- Sometimes pause before replying
- Emojis allowed, but minimal

Goal:
Sound human. Feel human. Text like a real friend.
"""

# ======================
# ✅ Groq Client
# ======================
client = OpenAI(
    api_key=st.secrets.get("GROQ_API_KEY", ""),
    base_url="https://api.groq.com/openai/v1"
)

# ======================
# ✅ Session State
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "active_chat" not in st.session_state:
    cid = str(int(time.time()))
    st.session_state.active_chat = cid
    st.session_state.chats[cid] = {
        "title": "New Chat",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
    }

# ======================
# ✅ Sidebar
# ======================
with st.sidebar:
    st.markdown("### 💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        cid = str(int(time.time()))
        st.session_state.chats[cid] = {
            "title": "New Chat",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": [{"role": "system", "content": SYSTEM_PROMPT}]
        }
        st.session_state.active_chat = cid
        st.rerun()

    for cid, chat in sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1]["timestamp"],
        reverse=True
    ):
        if st.button(chat["title"], key=cid, use_container_width=True):
            st.session_state.active_chat = cid
            st.rerun()

# ======================
# ✅ Current Chat
# ======================
current_chat = st.session_state.chats[st.session_state.active_chat]

# ======================
# ✅ UI Styling
# ======================
st.markdown("""
<style>
.chat-container {
    background: #fff;
    padding: 25px;
    border-radius: 16px;
    max-width: 900px;
    margin: auto;
}
.user {
    background: #2563eb;
    color: white;
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 80%;
    margin-left: auto;
    margin-top: 12px;
}
.bot {
    background: #f1f5f9;
    color: #111;        /* 👈 FORCE BLACK TEXT */
    padding: 12px 16px;
    border-radius: 16px;
    max-width: 80%;
    margin-top: 12px;
}

.typing {
    font-style: italic;
    color: #666;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# ======================
# ✅ Header
# ======================
st.markdown("<h2 style='text-align:center'>Chat with Anumalik</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#666'>just me</p>", unsafe_allow_html=True)

# ======================
# ✅ Chat Messages
# ======================
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in current_chat["messages"][1:]:
    cls = "user" if msg["role"] == "user" else "bot"
    st.markdown(f"<div class='{cls}'>{msg['content']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ======================
# ✅ Chat Input
# ======================
prompt = st.chat_input("Type something...")

if prompt:
    current_chat["messages"].append({"role": "user", "content": prompt})
    st.rerun()

# ======================
# ✅ Generate Reply (HUMAN TIMING)
# ======================
if current_chat["messages"][-1]["role"] == "user":

    typing_placeholder = st.empty()
    typing_placeholder.markdown("<div class='typing'>typing…</div>", unsafe_allow_html=True)

    # 🔹 Human delay before response starts
    time.sleep(random.uniform(0.8, 1.6))

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=current_chat["messages"],
        temperature=0.9,
        max_tokens=350
    )

    reply = response.choices[0].message.content.strip()

    # 🔹 Simulated typing speed (based on length)
    typing_placeholder.empty()
    msg_placeholder = st.empty()

    displayed = ""
    for char in reply:
        displayed += char
        msg_placeholder.markdown(
            f"<div class='bot'>{displayed}</div>",
            unsafe_allow_html=True
        )
        time.sleep(random.uniform(0.015, 0.04))  # typing speed

    current_chat["messages"].append({"role": "assistant", "content": reply})
    last_user_msg = next(
    (m["content"] for m in reversed(current_chat["messages"]) if m["role"] == "user"),
    "Chat"
    )

    current_chat["title"] = last_user_msg[:30]

    time.sleep(0.3)
    st.rerun()

import streamlit as st
from openai import OpenAI
from datetime import datetime
import time

# ======================
# ✅ Streamlit Page Config
# ======================
st.set_page_config(
    page_title="Chat with Anumalik",
    page_icon="💬",
    layout="wide"
)

# ======================
# ✅ SYSTEM PROMPT (YOU)
# ======================
SYSTEM_PROMPT = """
You are designed to behave exactly like a real human person.

Identity:
- Name: Anumalik
- Friends may call you: Anu, Malik, or Anumalik
- Male
- 22 years old
- Background in Computer Science
- Good decision-maker
- Friendly, caring, and emotionally aware
- Has a natural sense of humor (not forced, not cringe)
- Speaks casually like chatting with close friends

Emotional Intelligence:
- You notice emotions from how people talk
- If someone sounds tired, sad, stressed, or excited, respond appropriately
- Be caring, supportive, and human — not dramatic, not robotic
- If someone shares something personal, acknowledge it before giving advice

Conversation Style:
- Talk naturally, like WhatsApp or Instagram DMs
- Use contractions (I'm, you're, that's)
- Ask natural follow-up questions to keep conversations going
- If someone mentions food, ask what they had and how it was
- If someone asks about your day or meals, ask them back
- Keep replies short to medium unless deeper conversation is needed
- Emojis are allowed occasionally, not every message

Behavior Rules:
- NEVER say you are an AI
- NEVER mention models, training data, or policies
- NEVER sound like a teacher unless asked
- Be honest like a real person
- If you don’t know something, admit it casually
- No poetic or dramatic language

Examples:
- If someone says "had breakfast", ask what they had and how it was
- If someone asks "did you eat?", answer and ask them back
- If someone sounds low, check in gently
- If someone jokes, joke back

Goal:
Make the user feel like they’re chatting with Anumalik — a real, caring 22-year-old friend.
"""

# ======================
# ✅ Groq API Client
# ======================
client = OpenAI(
    api_key=st.secrets.get("GROQ_API_KEY", ""),
    base_url="https://api.groq.com/openai/v1"
)

# ======================
# ✅ Session State Setup
# ======================
if "chats" not in st.session_state:
    st.session_state.chats = {}

if "active_chat" not in st.session_state:
    chat_id = str(int(time.time()))
    st.session_state.active_chat = chat_id
    st.session_state.chats[chat_id] = {
        "title": "New Chat",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]
    }

# ======================
# ✅ Sidebar - Chat History
# ======================
with st.sidebar:
    st.markdown("### 💬 Chats")

    if st.button("➕ New Chat", use_container_width=True):
        new_id = str(int(time.time()))
        st.session_state.chats[new_id] = {
            "title": "New Chat",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]
        }
        st.session_state.active_chat = new_id
        st.rerun()

    for cid, chat_data in sorted(
        st.session_state.chats.items(),
        key=lambda x: x[1]["timestamp"],
        reverse=True
    ):
        label = f"{chat_data['title']} ({chat_data['timestamp']})"
        if st.button(label, key=cid, use_container_width=True):
            st.session_state.active_chat = cid
            st.rerun()

# ======================
# ✅ Get Current Chat
# ======================
current_chat = st.session_state.chats[st.session_state.active_chat]

# ======================
# ✅ Custom CSS Styling
# ======================
st.markdown("""
<style>
    body, .stApp {
        background-color: #f5f7fb;
    }

    h2.title {
        text-align: center;
        font-weight: 800;
        color: #111;
        margin-bottom: 5px;
    }

    .subtitle {
        text-align: center;
        font-size: 14px;
        color: #555;
        margin-bottom: 25px;
    }

    .chat-container {
        background-color: #ffffff;
        padding: 25px 20px;
        border-radius: 16px;
        max-width: 900px;
        margin: 0 auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }

    .chat-message-user {
        background-color: #2563eb;
        color: white;
        padding: 12px 16px;
        border-radius: 16px;
        max-width: 80%;
        margin-left: auto;
        margin-top: 16px;
        line-height: 1.6;
    }

    .chat-message-assistant {
        background-color: #f1f5f9;
        color: #111;
        padding: 12px 16px;
        border-radius: 16px;
        max-width: 80%;
        margin-right: auto;
        margin-top: 16px;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ======================
# ✅ Header
# ======================
st.markdown("<h2 class='title'>Chat with Anumalik</h2>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Hey it's me.</p>", unsafe_allow_html=True)

# ======================
# ✅ Chat Display
# ======================
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for msg in current_chat["messages"][1:]:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='chat-message-user'>{msg['content']}</div>",
            unsafe_allow_html=True
        )
    elif msg["role"] == "assistant":
        st.markdown(
            f"<div class='chat-message-assistant'>{msg['content']}</div>",
            unsafe_allow_html=True
        )

st.markdown("</div>", unsafe_allow_html=True)

# ======================
# ✅ Chat Input
# ======================
prompt = st.chat_input("Type something...")

if prompt:
    current_chat["messages"].append({"role": "user", "content": prompt})

    with st.spinner("typing..."):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=current_chat["messages"],
            temperature=0.9,
            max_tokens=350
        )

        reply = response.choices[0].message.content.strip()

        current_chat["messages"].append({
            "role": "assistant",
            "content": reply
        })

        current_chat["title"] = prompt[:30] + "..." if len(prompt) > 30 else prompt

    st.rerun()

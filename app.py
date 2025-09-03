import os
import streamlit as st
from storage import CandidateStore
from chatbot import TalentScoutBot, detect_end_keywords

# Custom dark theme for interview bot
st.set_page_config(
    page_title="TalentScout AI – Intelligent Hiring Assistant", 
    page_icon="🤖", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom dark theme
st.markdown("""
<style>
    /* Global styles */
    .main {
        background-color: #0e1117;
        color: #fafafa;
        max-width: 100%;
        padding: 0;
    }
    .stApp {
        background-color: #0e1117;
    }
    .stSidebar {
        background-color: #1e1e1e;
        color: #fafafa;
    }
    
    /* Title and headings */
    h1, h2, h3 {
        color: #4CAF50 !important;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stTitle {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        text-align: center !important;
        margin: 1rem 0 2rem 0 !important;
    }
    .stCaption {
        color: #b0b0b0;
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Form elements */
    .stButton > button {
        background-color: #4CAF50;
        color: white !important;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        width: auto;
        min-width: 120px;
    }
    .stButton > button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
    }
    
    /* Input fields with better visibility */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: #262730 !important;
        color: #fafafa !important;
        border: 2px solid #4a4a4a !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 1rem !important;
        transition: border-color 0.3s ease;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #4CAF50 !important;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.2);
    }
    
    /* Labels and text */
    .stTextInput > label,
    .stTextArea > label,
    .stNumberInput > label,
    .stSelectbox > label {
        color: #fafafa !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #262730;
        border-radius: 12px;
        margin: 12px 0;
        padding: 16px;
        border-left: 4px solid #4CAF50;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }
    .stChatMessage[data-testid="chatMessage"] {
        background-color: #1e1e1e;
        border-left: 4px solid #2196F3;
    }
    
    /* Expander */
    .stExpander {
        background-color: #262730;
        border: 2px solid #4a4a4a;
        border-radius: 12px;
        margin: 1rem 0;
    }
    .stExpander > div > div > div {
        background-color: #262730;
        color: #fafafa;
        padding: 1rem;
    }
    .stExpander > div > div > div > div {
        color: #fafafa !important;
    }
    
    /* Success and warning messages */
    .stSuccess {
        background-color: #1b5e20;
        color: #4caf50;
        border: 2px solid #4caf50;
        border-radius: 12px;
        padding: 16px;
        margin: 1rem 0;
        text-align: center;
    }
    .stWarning {
        background-color: #f57c00;
        color: #ff9800;
        border: 2px solid #ff9800;
        border-radius: 12px;
        padding: 16px;
        margin: 1rem 0;
        text-align: center;
    }
    
    /* Markdown content */
    .stMarkdown {
        color: #fafafa !important;
        line-height: 1.6;
    }
    .stMarkdown strong {
        color: #4CAF50 !important;
    }
    
    /* Dividers */
    .stDivider {
        border-color: #4a4a4a;
        margin: 2rem 0;
    }
    
    /* Form layout */
    .stForm {
        background-color: #1e1e1e;
        padding: 2rem;
        border-radius: 12px;
        border: 2px solid #4a4a4a;
        margin: 1rem 0;
    }
    
    /* Responsive layout */
    @media (max-width: 768px) {
        .stTitle {
            font-size: 2rem !important;
        }
        .stCaption {
            font-size: 1rem;
        }
        .stForm {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("🤖 TalentScout AI – Intelligent Hiring Assistant")
st.caption("Advanced AI-powered screening chatbot for technology candidates")

with st.expander("ℹ️ What this bot does"):
    st.markdown(
        """
        - Greets candidates and collects essential details
        - Generates **tech-stack-specific** technical questions
        - Maintains conversation context and handles fallbacks
        - Saves anonymized responses locally (simulated DB)
        - Type **bye**, **exit**, or **quit** to end the conversation
        """
    )

# Sidebar settings
st.sidebar.header("Settings")
provider = st.sidebar.selectbox("LLM Provider", ["OpenAI (default)", "Mock (offline)"])
model = st.sidebar.text_input("Model name (OpenAI)", value="gpt-4o-mini")
api_key = st.sidebar.text_input("OPENAI_API_KEY (if using OpenAI)", type="password", value=os.getenv("OPENAI_API_KEY", ""))

# Initialize state
if "bot" not in st.session_state:
    st.session_state.bot = TalentScoutBot(provider="openai" if provider.startswith("OpenAI") else "mock",
                                          model=model,
                                          api_key=api_key)

if "candidate" not in st.session_state:
    st.session_state.candidate = {
        "full_name": None,
        "email": None,
        "phone": None,
        "years_experience": None,
        "desired_position": None,
        "location": None,
        "tech_stack": None,
        "answers": {},
    }

if "chat" not in st.session_state:
    st.session_state.chat = []

if "ended" not in st.session_state:
    st.session_state.ended = False

# Candidate form
st.subheader("👤 Candidate Details")
with st.form("candidate_form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        full_name = st.text_input("Full Name", value=st.session_state.candidate["full_name"] or "")
        email = st.text_input("Email Address", value=st.session_state.candidate["email"] or "")
        years = st.number_input("Years of Experience", min_value=0.0, step=0.5,
                                value=float(st.session_state.candidate["years_experience"] or 0.0))
        location = st.text_input("Current Location", value=st.session_state.candidate["location"] or "")
    with col2:
        phone = st.text_input("Phone Number", value=st.session_state.candidate["phone"] or "")
        role = st.text_input("Desired Position(s)", value=st.session_state.candidate["desired_position"] or "")
        tech_stack = st.text_area("Tech Stack (comma-separated; e.g., Python, Django, PostgreSQL)",
                                  value=st.session_state.candidate["tech_stack"] or "")
    submitted = st.form_submit_button("Save / Update Details")

if submitted:
    st.session_state.candidate.update({
        "full_name": full_name.strip() or None,
        "email": email.strip() or None,
        "phone": phone.strip() or None,
        "years_experience": years,
        "desired_position": role.strip() or None,
        "location": location.strip() or None,
        "tech_stack": tech_stack.strip() or None,
    })
    st.success("Candidate details saved.")

st.divider()

# Chat area
st.subheader("💬 Interview Chat")
chat_container = st.container()

def add_message(role, content):
    st.session_state.chat.append({"role": role, "content": content})

# Greeting message
if not st.session_state.chat:
    add_message("assistant", "Hello! I'm TalentScout, your hiring assistant. I'll ask a few quick questions and then tailor some technical questions based on your tech stack. You can type **bye/exit/quit** anytime to finish. To begin, could you confirm your **Full Name** and **Tech Stack** above, then send me a message here when ready.")

with st.form("chat_form", clear_on_submit=True):
    user_msg = st.text_input("Your message")
    send = st.form_submit_button("Send")
    if send and user_msg.strip():
        if detect_end_keywords(user_msg):
            add_message("user", user_msg)
            add_message("assistant", "Thanks for your time! We'll review your responses and get back to you with next steps. 👋")
            st.session_state.ended = True
        else:
            add_message("user", user_msg)
            bot_reply = st.session_state.bot.reply(
                user_msg,
                st.session_state.candidate
            )
            add_message("assistant", bot_reply)

# Show conversation
for m in st.session_state.chat:
    if m["role"] == "user":
        st.chat_message("user").markdown(m["content"])
    else:
        st.chat_message("assistant").markdown(m["content"])

# Generate questions button
st.divider()
st.subheader("🧠 Tech Questions")
if st.button("Generate 3–5 Technical Questions"):
    questions = st.session_state.bot.generate_tech_questions(st.session_state.candidate)
    if questions:
        for i, q in enumerate(questions, start=1):
            st.markdown(f"**Q{i}.** {q}")
    else:
        st.warning("Please provide a Tech Stack in the Candidate Details section.")

# Save session
st.divider()
if st.button("Save Interview to Local Store"):
    store = CandidateStore(path="storage/candidates.json")
    cid = store.save(st.session_state.candidate, st.session_state.chat)
    st.success(f"Saved interview session with id: `{cid}` (anonymized). File: storage/candidates.json")

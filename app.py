import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError
import datetime

# --- CONFIGURATION & INITIALIZATION ---

# 1. Gemini Client Setup
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error("Error: Gemini API Key not found in Streamlit secrets. Please check your .streamlit/secrets.toml file.")
    st.stop()
except Exception as e:
    st.error(f"Error initializing Gemini client: {e}")
    st.stop()

# Model and System Prompt
GEMINI_MODEL = "gemini-2.5-flash"

SYSTEM_PROMPT = (
    "You are a friendly and encouraging student support bot. "
    "Respond with empathy and curiosity about students' feelings and studies. "
    "Avoid medical or diagnostic advice. Keep the tone kind, gentle, and motivational."
)

# 2. Streamlit Page Setup
st.set_page_config(
    page_title="Student Wellness Chatbot",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- SESSION STATE INITIALIZATION ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        types.Content(role="model", parts=[types.Part(text=SYSTEM_PROMPT)])
    ]
if "journal_entries" not in st.session_state:
    st.session_state.journal_entries = []
if "selected_mood" not in st.session_state:
    st.session_state.selected_mood = "Normal"
if "display_name" not in st.session_state:
    st.session_state.display_name = ""
if "journal_input_text" not in st.session_state:
    st.session_state.journal_input_text = ""


# --- HELPER FUNCTIONS ---

def soften_input(user_input: str) -> str:
    """Rephrase strong emotional words to softer alternatives to prevent safety blocking."""
    replacements = {
        "depressed": "feeling very low",
        "hopeless": "feeling quite discouraged",
        "suicidal": "feeling overwhelmed",
        "anxious": "nervous or tense",
        "panic": "very worried",
    }
    for word, soft in replacements.items():
        user_input = user_input.replace(word, soft)
    return user_input


def get_gemini_response(prompt: str):
    """Generates a response from Gemini API with retry and safe handling."""
    try:
        # Soften emotional input
        prompt = soften_input(prompt)

        # Add user message to history
        st.session_state.chat_history.append(
            types.Content(role="user", parts=[types.Part(text=prompt)])
        )

        # Call Gemini API
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=st.session_state.chat_history,
            config=types.GenerateContentConfig(
                temperature=st.session_state.get('temperature', 0.7),
                max_output_tokens=st.session_state.get('max_tokens', 300)
            )
        )

        # Handle blocked or empty response
        if not response.candidates or not response.candidates[0].content:
            # Retry once
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=st.session_state.chat_history,
                config=types.GenerateContentConfig(
                    temperature=st.session_state.get('temperature', 0.7),
                    max_output_tokens=st.session_state.get('max_tokens', 300)
                )
            )

        # Final response check
        if response.candidates and response.candidates[0].content:
            st.session_state.chat_history.append(response.candidates[0].content)
            return response.text
        else:
            fallback_text = "(Message blocked by safety filters.)"
            st.session_state.chat_history.append(
                types.Content(role="model", parts=[types.Part(text=fallback_text)])
            )
            return fallback_text

    except APIError as e:
        error_message = f"Sorry, communication error occurred: {e}"
        st.session_state.chat_history.append(
            types.Content(role="model", parts=[types.Part(text=error_message)])
        )
        st.error(error_message)
    except Exception as e:
        error_message = f"Unexpected error: {e}"
        st.session_state.chat_history.append(
            types.Content(role="model", parts=[types.Part(text=error_message)])
        )
        st.error(error_message)


def save_journal_entry(reflection: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.journal_entries.insert(0, (timestamp, reflection))
    st.success("Journal entry saved!")


def display_chat_messages():
    """Display chat history safely."""
    for message in st.session_state.chat_history[1:]:  # skip system prompt
        role = message.role
        avatar = "👤" if role == "user" else "🤖"
        display_name = st.session_state.display_name or ("You" if role == "user" else "Bot")

        # Extract message text safely
        if message.parts and message.parts[0].text:
            text = message.parts[0].text
        else:
            text = "(Message unavailable or blocked.)"

        with st.chat_message(role, avatar=avatar):
            st.write(text)


def handle_chat_input():
    if st.session_state.user_chat_input:
        user_input = st.session_state.user_chat_input
        mood_context = f"[Context: My current mood is {st.session_state.selected_mood}]. "
        full_prompt = mood_context + user_input

        with st.spinner("Bot is thinking..."):
            get_gemini_response(full_prompt)


# --- SIDEBAR UI ---

with st.sidebar:
    st.header("Settings & Mood")

    st.subheader("Model Settings")
    st.info(f"**Model ID:** {GEMINI_MODEL}")
    st.slider("Temperature (Creativity)", 0.0, 1.0, 0.7, 0.05, key='temperature')
    st.slider("Max New Tokens", 50, 1024, 300, 50, key='max_tokens')

    st.divider()

    st.subheader("Mood Tracker")
    st.radio(
        "How are you feeling today?",
        options=["Normal", "Sad 😥", "Angry 😡", "Calm 😌", "Upset 😩", "Cool 😎"],
        key="selected_mood"
    )
    st.write(f"**Selected mood:** {st.session_state.selected_mood}")

    st.divider()

    if st.button("Clear Chat History", key="clear_chat_btn"):
        st.session_state.chat_history = [
            types.Content(role="model", parts=[types.Part(text=SYSTEM_PROMPT)])
        ]
        st.experimental_rerun()

# --- MAIN UI ---

st.title("🌱 Student Wellness Chatbot")
st.markdown(
    """
    **Type how you're feeling.**  
    The bot will respond with empathy and a gentle follow-up question.

    **⚠️ Note:** Avoid medical or clinical terms — express your feelings generally  
    (e.g., "I feel tired and worried" instead of "I have depression").
    """
)

chat_tab, journal_tab = st.tabs(["💬 Chat", "📜 Journal"])

# --- CHAT TAB ---
with chat_tab:
    st.text_input("Your display name (optional)", key='display_name', placeholder="e.g., John Doe")
    display_chat_messages()
    st.chat_input("What's on your mind today?", key='user_chat_input', on_submit=handle_chat_input)

# --- JOURNAL TAB ---
with journal_tab:
    st.header("Personal Journal")
    st.markdown("Write freely. Entries are stored only in your session.")

    st.text_area(
        "Today's reflection",
        key="journal_area",
        value=st.session_state.journal_input_text,
        placeholder="Write about your day or feelings...",
        height=200,
        label_visibility="collapsed"
    )

    if st.button("Save Entry", key="save_journal_btn", use_container_width=True):
        entry = st.session_state.journal_area
        if entry.strip():
            save_journal_entry(entry)
            st.session_state.journal_input_text = ""
            st.session_state.journal_area = ""
            st.experimental_rerun()
        else:
            st.warning("Please write something before saving.")

    st.markdown("---")
    st.subheader("Your Entries")

    if st.session_state.journal_entries:
        for timestamp, entry in st.session_state.journal_entries:
            with st.expander(f"Reflection from {timestamp} ({st.session_state.selected_mood})"):
                st.write(entry)
    else:
        st.info("No journal entries yet. Start your first reflection above!")

st.divider()
st.caption("Note: Chat and journal data are stored only in your browser session memory.")

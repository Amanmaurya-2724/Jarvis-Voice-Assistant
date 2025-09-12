# virtual-assistant.py
import streamlit as st
import speech_recognition as sr
from gtts import gTTS
import io
import datetime
import wikipedia
import webbrowser
import os
import psutil
import platform
import subprocess
import base64
import tempfile
import ctypes
import time


# ---------------- Config / Page ----------------
st.set_page_config(page_title="Jarvis - Voice Assistant", layout="wide", initial_sidebar_state="expanded")

# ---------------- Helper: Theme & Animated Background ----------------
def set_styles(dark_mode=True, animated=True):
    if dark_mode:
        bg_css = """
        background: linear-gradient(135deg, rgba(2,6,23,1) 0%, rgba(10,25,47,1) 40%, rgba(4,20,40,1) 100%);
        color: #e6eef8;
        """
        card_bg = "rgba(255,255,255,0.04)"
        text_color = "#e6eef8"
        accent = "#7dd3fc"
    else:
        bg_css = "background: linear-gradient(135deg, #f8fafc 0%, #e6eef8 100%); color: #0f172a;"
        card_bg = "rgba(255,255,255,0.65)"
        text_color = "#0f172a"
        accent = "#0f172a"

    anim = ""
    if animated:
        anim = """
        background: linear-gradient(-45deg, #0f172a, #06203a, #08192f, #032f46);
        background-size: 400% 400%;
        -webkit-animation: Gradient 12s ease infinite;
        -moz-animation: Gradient 12s ease infinite;
        animation: Gradient 12s ease infinite;
        @-webkit-keyframes Gradient { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
        @-moz-keyframes Gradient { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
        @keyframes Gradient { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
        """

    css = f"""
    <style>
    :root {{
        --card-bg: {card_bg};
        --accent: {accent};
        --text: {text_color};
    }}
    .stApp {{
        {anim if animated else bg_css}
        min-height: 100vh;
        color: var(--text);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    .header-card{{
        background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.02));
        border-radius: 14px;
        padding: 18px;
        box-shadow: 0 6px 30px rgba(2,6,23,0.6);
        margin-bottom: 10px;
        backdrop-filter: blur(6px);
        border: 1px solid rgba(255,255,255,0.03);
    }}
    .btn-primary > button {{
        background: var(--accent) !important;
        color: #04203a !important;
        border-radius: 10px;
        padding: 10px 16px;
        font-weight: 600;
    }}
    .control-row {{
        gap: 10px;
        display:flex;
    }}
    .output-card {{
        background: var(--card-bg);
        border-radius: 12px;
        padding: 14px;
        margin-top: 10px;
        border: 1px solid rgba(255,255,255,0.04);
        backdrop-filter: blur(6px);
    }}
    .muted {{ color: #94a3b8; font-size: 13px; }}
    .small {{ font-size: 13px; color: #9fb3c8; }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

# ---------------- Speak (gTTS -> in-memory bytes -> st.audio) ----------------
def speak(text):
    """Convert text to speech and play hidden (no UI container)"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts = gTTS(text=text, lang="en")
            tts.save(fp.name)

            # File ko base64 encode karo
            with open(fp.name, "rb") as f:
                audio_data = f.read()
            b64 = base64.b64encode(audio_data).decode()

            # Hidden autoplay audio (UI me kuch nahi dikhega)
            audio_html = f"""
                <audio autoplay="true" style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"TTS Error: {e}")
# ---------------- Voice Input (auto-stop after recognition) ----------------
def takeCommand(timeout=5, phrase_time_limit=7):
    """
    Listen once: waits up to `timeout` seconds for speech to start, then records up to phrase_time_limit seconds.
    Returns recognized text or "None".
    """
    # Check if we're running in a browser environment
    r = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.session_state.output_history.append("🎤 Listening... (speak now)")
            r.pause_threshold = 0.8
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                st.session_state.output_history.append("⏳ Timeout: no voice detected")
                return "None"
    except OSError:
        st.session_state.output_history.append("❌ Microphone not available in this environment")
        return "None"
        
    try:
        st.session_state.output_history.append("🔍 Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        st.session_state.output_history.append(f"✅ Recognized: {query}")
        return query
    except sr.UnknownValueError:
        st.session_state.output_history.append("❌ Could not understand audio")
        return "None"
    except sr.RequestError:
        st.session_state.output_history.append("❌ Recognition service error")
        return "None"
    except Exception as e:
        st.session_state.output_history.append(f"❌ Error: {e}")
        return "None"

# ---------------- Core features ----------------
def wishMe():
    hour = datetime.datetime.now().hour
    if 0 <= hour < 12:
        greeting = "Good Morning!"
    elif 12 <= hour < 18:
        greeting = "Good Afternoon!"
    else:
        greeting = "Good Evening!"

    # Sequential TTS
    speak(greeting)  # pehle greeting bole
    time.sleep(1) 
    speak("Welcome to jarvis voice assistant. How can I help you today?")  # phir ye bole

    return greeting


def open_path_from_query(query):
    """Try open as absolute path or under user home or by common app name"""
    name = query.strip()
    
    # This function won't work in a web environment
    st.session_state.output_history.append("⚠️ Opening files is not supported in this web environment.")
    return False, name

def handle_query(query):
    if not query:
        return

    q = query.lower().strip()
    st.session_state.output_history.append(f"👤 User: {query}")

    # ---------------- System Controls ----------------
    if "shutdown" in q:
        try:
            os.system("shutdown /s /t 5")
            speak("Shutting down your system in 5 seconds")
        except Exception as e:
            speak("Sorry, shutdown command failed")

    elif "restart" in q:
        try:
            os.system("shutdown /r /t 5")
            speak("Restarting your system in 5 seconds")
        except Exception as e:
            speak("Sorry, restart command failed")

    elif "lock" in q:
        try:
            ctypes.windll.user32.LockWorkStation()
            speak("Locking your system")
        except Exception as e:
            speak("Sorry, lock command failed")

    elif "logout" in q:
        try:
            os.system("shutdown /l")
            speak("Logging out current user")
        except Exception as e:
            speak("Sorry, logout command failed")

    elif "sleep" in q:
        try:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            speak("Putting system to sleep")
        except Exception as e:
            speak("Sorry, sleep command failed")

    elif "battery" in q:
        try:
            battery = psutil.sensors_battery()
            percent = battery.percent
            plugged = "charging" if battery.power_plugged else "not charging"
            speak(f"Battery is at {percent} percent and it is {plugged}")
        except Exception as e:
            speak("Battery information not available")

    elif "cpu" in q:
        try:
            usage = psutil.cpu_percent()
            speak(f"CPU usage is at {usage} percent")
        except Exception as e:
            speak("CPU usage info not available")

    elif "ram" in q:
        try:
            mem = psutil.virtual_memory()
            speak(f"RAM usage is at {mem.percent} percent")
        except Exception as e:
            speak("RAM usage info not available")

    # ---------------- Wikipedia ----------------
    elif "wikipedia" in q:
        st.session_state.output_history.append("🔍 Searching Wikipedia...")
        speak("Searching Wikipedia...")
        topic = q.replace("wikipedia", "").strip()
        try:
            result = wikipedia.summary(topic, sentences=2)
            st.session_state.output_history.append(f"📚 Wikipedia: {result}")
            speak("According to Wikipedia")
            speak(result)
        except Exception:
            error_msg = "Could not fetch from Wikipedia."
            st.session_state.output_history.append(f"❌ {error_msg}")
            speak("Sorry, I could not find information on Wikipedia.")

    # ---------------- Websites ----------------
    elif "youtube" in q:
        webbrowser.open("https://youtube.com")
        st.session_state.output_history.append("🌐 Opening YouTube")
        speak("Opening YouTube")

    elif "google" in q:
        webbrowser.open("https://google.com")
        st.session_state.output_history.append("🌐 Opening Google")
        speak("Opening Google")

    elif "stackoverflow" in q:
        webbrowser.open("https://stackoverflow.com")
        st.session_state.output_history.append("🌐 Opening StackOverflow")
        speak("Opening StackOverflow")

    # ---------------- Music (not supported in web) ----------------
    elif "music" in q:
        st.session_state.output_history.append("❌ Music playback is not available in this web environment.")
        speak("Music playback is not available in this web environment.")

    # ---------------- Time ----------------
    elif "time" in q:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        st.session_state.output_history.append(f"⏰ Current time: {now}")
        speak(f"The time is {now}")

    # ---------------- Open file/app (not supported in web) ----------------
    elif q.startswith("open "):
        target = q.replace("open ", "", 1).strip()
        st.session_state.output_history.append(f"⚠️ Cannot open '{target}' in web environment.")
        speak(f"I cannot open applications in this web environment.")

    # ---------------- Email (placeholder) ----------------
    elif "email" in q:
        st.session_state.output_history.append("📧 Email feature is configured in your script. Please use manual configuration for sending emails.")
        speak("Email feature is configured in your script. Please use manual configuration for sending emails.")

    # ---------------- Fallback search ----------------
    else:
        st.session_state.output_history.append(f"🔍 Searching Google for: {q}")
        speak(f"Searching Google for {q}")
        webbrowser.open(f"https://www.google.com/search?q={q}")


# ---------------- UI: Sidebar + Main ----------------
# Initialize session state for output history
if 'output_history' not in st.session_state:
    st.session_state.output_history = ["🤖 Welcome to Jarvis Voice Assistant! How can I help you today?"]

# Sidebar: settings
st.sidebar.title("⚙️ Jarvis Settings")
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=True)
animated_bg = st.sidebar.checkbox("✨ Animated Background", value=True)
set_styles(dark_mode=dark_mode, animated=animated_bg)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Controls")

if st.sidebar.button("Open Google"):
    st.session_state.output_history.append("🌐 Opening Google")
    webbrowser.open("https://google.com")
if st.sidebar.button("Open YouTube"):
    st.session_state.output_history.append("🌐 Opening YouTube")
    webbrowser.open("https://youtube.com")
if st.sidebar.button("Open Wikipedia"):
    st.session_state.output_history.append("🌐 Opening Wikipedia")
    webbrowser.open("https://wikipedia.org")


st.sidebar.markdown("---")
st.sidebar.caption("Note: This is a web version with limited functionality")

# Main header card
st.markdown("<div class='header-card'><h1>🤖 Jarvis - Voice Assistant</h1><p class='muted'>Web version with limited functionality. Some features only work when run locally.</p></div>", unsafe_allow_html=True)

# Two columns: controls and output/history
left, right = st.columns([1, 2])

with left:
    st.markdown("### Controls")
    if st.button("👋 Wish Me"):
        greeting = wishMe()
        st.session_state.output_history.append(f"✅ {greeting}")

    if st.button("🎤 Start Voice Command"):
        st.session_state.output_history.append("🎤 Starting voice command...")
        query = takeCommand()
        if query and query != "None":
            handle_query(query)
        else:
            st.session_state.output_history.append("⚠️ No valid speech recognized. Try again.")

    # Manual input
    manual = st.text_input("💬 Manual query")
    if st.button("🔎 Run Manual Query"):
        if manual.strip():
            handle_query(manual)
        else:
            st.session_state.output_history.append("⚠️ Please type something.")

with right:
    st.markdown("### Output / Activity")
    
    # Display output history in cards
    for output in st.session_state.output_history:
        if output.startswith("❌"):
            st.markdown(f"<div class='output-card' style='color: #ff4b4b;'>{output}</div>", unsafe_allow_html=True)
        elif output.startswith("⚠️"):
            st.markdown(f"<div class='output-card' style='color: #ffa421;'>{output}</div>", unsafe_allow_html=True)
        elif output.startswith("✅"):
            st.markdown(f"<div class='output-card' style='color: #00cc00;'>{output}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='output-card'>{output}</div>", unsafe_allow_html=True)
    
    # Add clear button
    if st.button("🗑️ Clear Output", key="clear_output"):
        st.session_state.output_history = ["Output cleared"]
        st.rerun()

# Footer
st.markdown("<div style='margin-top:20px; opacity:0.7; font-size:13px;'>Web version with limited functionality. Run locally for full features.</div>", unsafe_allow_html=True)
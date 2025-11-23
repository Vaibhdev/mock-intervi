import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading
import time
import math
from agent import InterviewManager
from pypdf import PdfReader
try:
    import docx
except ImportError:
    docx=None

# --- Page Config ---
st.set_page_config(page_title="Interview Practice Partner",layout="wide",page_icon="⚡")

# --- Theme State Management ---
if 'theme' not in st.session_state:
    st.session_state.theme='light'
# --- Top Left Theme Toggle ---
# We use a small column so the toggle doesn't stretch across the screen
t_col1, t_col2=st.columns([2, 10]) 

with t_col1:
    is_dark=st.toggle(
        "🌙 Dark Mode", 
        value=(st.session_state.theme == 'dark'),
        key="theme_toggle"
    )

# Logic to handle state change
selected_theme='dark' if is_dark else 'light'
if selected_theme!=st.session_state.theme:
    st.session_state.theme=selected_theme
    st.rerun()

# --- Unified Color Palettes ---
themes={
    "light": {
        "primary": "#1e0b5d",
        "secondary": "#00d4ff",
        "accent": "#ff007a",
        "text": "#1f2937",
        "bg_start": "#f8f9fa",
        "bg_end": "#e9ecef",
        "card_bg": "#ffffff",
        "border": "#e5e7eb",
        "input_bg": "#ffffff",
        "input_text": "#1f2937", 
        "chat_bg": "#f8fafc",
        "metric_bg": "#ffffff"
    },
    "dark": {
        "primary": "#7c3aed",
        "secondary": "#00d4ff",
        "accent": "#ff007a",
        "text": "#e5e7eb", 
        "bg_start": "#1a1a2e", 
        "bg_end": "#16213e", 
        "card_bg": "#24243e", 
        "border": "#334155",
        "input_bg": "#ffffff",   
        "input_text": "#1f2937",   
        "chat_bg": "#24243e",
        "metric_bg": "#24243e"
    }
}

current_theme=themes[st.session_state.theme]

# --- Single CSS Block with Variables ---
# NOTE: All CSS brackets { } are doubled {{ }} here to prevent Python f-string errors
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {{
        --primary-color: {current_theme['primary']};
        --secondary-color: {current_theme['secondary']};
        --accent-color: {current_theme['accent']};
        --text-color: {current_theme['text']};
        --bg-start: {current_theme['bg_start']};
        --bg-end: {current_theme['bg_end']};
        --card-bg: {current_theme['card_bg']};
        --border-color: {current_theme['border']};
        --input-bg: {current_theme['input_bg']};
        --input-text: {current_theme['input_text']};
        --chat-bg: {current_theme['chat_bg']};
        --metric-bg: {current_theme['metric_bg']};
    }}

    /* FORCE BACKGROUND ON THE MAIN STREAMLIT CONTAINER */
    .stApp {{
        background: linear-gradient(135deg, var(--bg-start) 0%, var(--bg-end) 100%) !important;
        background-attachment: fixed !important;
        color: var(--text-color) !important;
    }}

    /* HIDE DEFAULTS */
    header {{visibility: hidden;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* MAIN HEADER */
    .main-header {{
        text-align: center;
        font-size: 2.5rem;
        font-weight: 800;
        margin-top: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        background-size: 300% 300%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-flow 8s ease infinite;
    }}

    /* HERO SECTION */
    .hero-background {{
        padding: 4rem 2rem;
        border-radius: 24px;
        margin: 1rem 0 3rem 0;
        text-align: center;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        background-size: 400% 400%;
        animation: hero-gradient 15s ease infinite;
        color: white;
        position: relative;
        overflow: hidden;
        box-shadow: 0 20px 60px -10px rgba(0,0,0,0.3);
    }}
    .hero-title {{
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        line-height: 1.2;
        color: white;
    }}
    
    .hero-subtitle {{
        font-size: 1.3rem;
        font-weight: 500;
        max-width: 700px;
        margin: 0 auto;
        color: #f3f4f6; 
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}

    /* GENERIC CARD */
    .eightfold-card {{
        background: var(--card-bg);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }}
    .eightfold-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 20px 40px -10px rgba(0, 212, 255, 0.2);
    }}

    /* BUTTONS */
    div.stButton > button {{
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        background-size: 300% 300%;
        color: white;
        border-radius: 9999px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
        animation: button-gradient 5s ease infinite;
    }}
    div.stButton > button:hover {{
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
    }}

    /* INPUTS - FORCING WHITE BG AND DARK TEXT */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > div,
    .stTextArea > div > div > textarea {{
        border-radius: 8px;
        border: 2px solid var(--border-color);
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        caret-color: var(--input-text); /* Fix cursor color */
    }}
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: var(--secondary-color);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.2);
    }}
    
    /* DROPDOWN MENU FIX */
    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
    }}
    
    /* Fix for the dropdown options list popover */
    div[data-baseweb="popover"] {{
        background-color: var(--input-bg) !important;
    }}
    ul[data-baseweb="menu"] {{
        background-color: var(--input-bg) !important;
    }}
    ul[data-baseweb="menu"] li {{
        color: var(--input-text) !important;
    }}

    /* HEADERS AND LABELS */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
        color: var(--text-color) !important;
    }}

    /* CHAT BUBBLE */
    .chat-bubble {{
        background: var(--chat-bg);
        padding: 1.5rem;
        border-radius: 0 16px 16px 16px;
        border-left: 4px solid transparent;
        border-image: linear-gradient(180deg, var(--secondary-color), var(--accent-color)) 1;
        color: var(--text-color);
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }}

    /* METRIC BOX */
    .metric-box {{
        background: var(--metric-bg);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 2px solid transparent;
        height: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .metric-box:hover {{
        border-color: var(--secondary-color);
        transform: translateY(-4px);
    }}
    .metric-val {{
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    /* ORB (Speaking Indicator) */
    .orb {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--secondary-color), var(--accent-color));
        background-size: 300% 300%;
        margin: 0 auto 24px auto;
        box-shadow: 0 0 60px rgba(0, 212, 255, 0.6);
        animation: orb-pulse 3s ease-in-out infinite;
    }}
    .orb-silent {{
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle at 30% 30%, var(--border-color), var(--card-bg));
        margin: 0 auto 24px auto;
    }}

    /* ANIMATIONS */
    @keyframes gradient-flow {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
    @keyframes hero-gradient {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
    @keyframes button-gradient {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} }}
    @keyframes orb-pulse {{ 0%, 100% {{ transform: scale(1); box-shadow: 0 0 60px rgba(0, 212, 255, 0.6); }} 50% {{ transform: scale(1.08); box-shadow: 0 0 80px rgba(255, 0, 122, 0.8); }} }}
    
    /* Live Badge */
    .live-badge {{
        background: linear-gradient(90deg, #ef4444, #ff007a);
        color: white;
        padding: 6px 14px;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.75rem;
        animation: pulse-live 1.5s ease infinite;
    }}
    @keyframes pulse-live {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
    
    /* Content List */
    .content-list {{ list-style: none; padding: 0; }}
    .content-list li {{
        background: var(--card-bg);
        margin-bottom: 10px;
        padding: 12px 16px;
        border-radius: 8px;
        border-left: 3px solid var(--border-color);
        color: var(--text-color);
        transition: all 0.3s ease;
    }}
    .content-list li:hover {{ transform: translateX(5px); }}
    /* --- PASTE THIS AT THE BOTTOM OF YOUR CSS BLOCK --- */

    /* FUNKY COUNTDOWN ANIMATIONS */
    @keyframes count-pop {{
        0% {{ transform: scale(0.5); opacity: 0; }}
        50% {{ transform: scale(1.4); opacity: 1; text-shadow: 0 0 30px var(--secondary-color); }}
        100% {{ transform: scale(1); opacity: 1; }}
    }}

    .funky-countdown {{
        font-size: 8rem; /* Made it bigger */
        font-weight: 900;
        text-align: center;
        line-height: 1;
        margin: 20px 0;
        animation: count-pop 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
        /* FIXED: Removed gradient background to stop the "box" effect */
        color: var(--text-color); 
        transition: color 0.3s ease, text-shadow 0.3s ease;
    }}

    .funky-subtext {{
        text-align: center;
        font-size: 1.2rem;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--secondary-color);
        animation: pulse-live 1s infinite;
    }}
    /* --- PASTE THIS AT THE VERY BOTTOM OF YOUR CSS BLOCK --- */

    /* HIDE CAMERA "TAKE PHOTO" BUTTON */
    /* This targets the specific button inside the camera widget */
    button[data-testid="stCameraInputButton"] {{
        display: none !important;
    }}

    /* Optional: Hide the text "Take Photo" if it appears below it */
    .stCameraInput > div > div > div:nth-child(2) {{
         display: none !important;
    }}
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if 'manager' not in st.session_state:
    try:
        st.session_state.manager=InterviewManager()
        st.session_state.ready=True
    except Exception as e:
        st.error(f"Setup Error: {e}")
        st.session_state.ready=False

if 'page' not in st.session_state: st.session_state.page='config'
if 'messages' not in st.session_state: st.session_state.messages=[]
if 'is_speaking' not in st.session_state: st.session_state.is_speaking=False
if 'speech_end_time' not in st.session_state: st.session_state.speech_end_time=0 
if 'start_time' not in st.session_state: st.session_state.start_time=None
if 'interview_duration' not in st.session_state: st.session_state.interview_duration=15 
if 'feedback_data' not in st.session_state: st.session_state.feedback_data=None
if 'auto_mode' not in st.session_state: st.session_state.auto_mode=True 
if 'ending_sequence_initiated' not in st.session_state: st.session_state.ending_sequence_initiated=False

# --- Helper Functions ---

def extract_text_from_file(file):
    """Extracts text from PDF, DOCX, or TXT files."""
    if file is None:
        return ""
        
    try:
        if file.type=="application/pdf":
            reader=PdfReader(file)
            text=""
            for page in reader.pages:
                text+=page.extract_text()
            return text
            
        elif file.type=="text/plain":
            return str(file.read(), "utf-8")
            
        elif "wordprocessingml" in file.type: # DOCX
            if docx is None:
                return "[Error: python-docx library not installed]"
            doc=docx.Document(file)
            return "\\n".join([para.text for para in doc.paragraphs])
            
        else:
            return ""
    except Exception as e:
        return f"Error reading file: {e}"

def speak(text):
    # 162 wpm calculation
    word_count=len(text.split())
    estimated_seconds=(word_count/162)*60+2 
    
    st.session_state.speech_end_time=time.time()+estimated_seconds
    st.session_state.is_speaking=True
    
    def _run_speech():
        try:
            engine=pyttsx3.init()
            engine.setProperty('rate', 162) 
            engine.say(text)
            engine.runAndWait()
        except:
            pass
        st.session_state.is_speaking = False
        
    t = threading.Thread(target=_run_speech)
    t.start()

def listen(status_container):
    """Listen for user speech with 5-second timeout for silence."""
    r = sr.Recognizer()
    with sr.Microphone() as source:
        # Calibrate for ambient noise
        status_container.info("🎤 Calibrating microphone...")
        r.adjust_for_ambient_noise(source, duration=1.0)
        
        # Static threshold for stability
        r.dynamic_energy_threshold=False
        r.energy_threshold=300
        r.pause_threshold=3.0  
        
        try:
            status_container.info("🎤 Listening(5s Timeout...")
            audio=r.listen(source, timeout=5, phrase_time_limit=None)
            status_container.info("⚡ Processing your answer...")
            return r.recognize_google(audio)
        except sr.WaitTimeoutError:
            return None
        except Exception:
            return None

def check_time_limit():
    if st.session_state.start_time:
        elapsed=(time.time()-st.session_state.start_time)/60
        return elapsed>=st.session_state.interview_duration
    return False

# --- PAGE 1: CONFIGURATION ---
def render_config_page():
    st.markdown('<div class="main-header">Interview Practice Partner</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="hero-background">
        <div class="hero-title">The future works here.</div>
        <div class="hero-subtitle">Master your interview skills with realistic AI-powered practice sessions.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_main, _ = st.columns([1, 0.01]) 
    
    with col_main:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎯 Target Config")
            role_options = [
                "Software Engineer", "Product Manager", "Data Scientist", "Marketing Specialist", 
                "Sales Representative", "HR Manager", "Financial Analyst", "Graphic Designer", 
                "Project Manager", "Customer Support Specialist", "Business Analyst", "DevOps Engineer", 
                "Content Writer", "Social Media Manager", "UX/UI Designer", "Legal Counsel", 
                "Operations Manager", "Teacher / Educator", "Nurse / Healthcare Professional", "Other"
            ]
            role = st.selectbox("Select Role", role_options)
            if role == "Other":
                role = st.text_input("Custom Role Name")
            language = st.selectbox("Language", ["English", "Spanish", "Hindi", "French"])
        
        with c2:
            st.subheader("⚙️ Difficulty & Time")
            difficulty = st.select_slider("Complexity Level", ["Intern", "Junior", "Mid-Level", "Senior", "Executive"])
            duration = st.number_input("Duration (Minutes)", min_value=1, max_value=60, value=15)
            
            # UPDATED JD OPTION (Optional + File Upload)
            st.markdown("**Job Description (Optional)**")
            jd_input_type = st.radio("Input Type", ["Paste Text", "Upload File"], horizontal=True, label_visibility="collapsed")
            
            jd_text = ""
            if jd_input_type == "Paste Text":
                jd_text = st.text_area("Paste JD", height=100, placeholder="Paste Job Description here...", label_visibility="collapsed")
            else:
                jd_file = st.file_uploader("Upload JD", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")
                if jd_file:
                    jd_text = extract_text_from_file(jd_file)

        st.markdown("---")
        st.subheader("📄 Resume Context (Optional)")
        resume = st.file_uploader("Upload CV", type=['pdf', 'docx', 'txt'], label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("🚀 Launch Interview Session", type="primary", use_container_width=True):
            resume_text = extract_text_from_file(resume) if resume else ""
            role = role if role else "General"
            st.session_state.interview_settings = {
                "role": role,
                "language": language,
                "difficulty": difficulty,
                "resume_text": resume_text,
                "jd_text": jd_text # Store JD
            }
            st.session_state.interview_duration = duration
            st.session_state.start_time = None 
            st.session_state.page = 'interview'
            st.rerun()

# --- PAGE 2: INTERVIEW ---
def render_interview_page():
    st.markdown("<h2 style='text-align:center; margin-bottom: 30px;'>Live Interview Session</h2>", unsafe_allow_html=True)
    
    time_is_up=check_time_limit()
    
    if st.session_state.start_time:
        elapsed_min=(time.time()-st.session_state.start_time)/60
        remaining=max(0, st.session_state.interview_duration-elapsed_min)
        st.progress(min(1.0, elapsed_min/st.session_state.interview_duration))

    col1, col2=st.columns(2)

    with col1:
        orb_class="orb" if st.session_state.is_speaking else "orb-silent"
        last_msg=st.session_state.messages[-1]['content'] if st.session_state.messages else "I'm ready to begin. Shall we start?"
        st.markdown(f"""
        <div class="eightfold-card" style="display: flex; flex-direction: column; align-items: center; text-align: center; border-top: 5px solid #7c3aed;">
            <div class="{orb_class}"></div>
            <h3 style="margin-bottom: 20px; color: #4c1d95;">AI Recruiter</h3>
            <div class="chat-bubble" style="width: 100%; text-align: left;">
                {last_msg}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 10px;">
            <span class="live-badge">🔴 LIVE</span>
            <h3 style="color: white; display: inline-block; margin-left: 10px; text-shadow: 0 2px 4px rgba(0,0,0,0.2);">You</h3>
        </div>
        """, unsafe_allow_html=True)
        st.camera_input("Camera", label_visibility="hidden")

    c1,c2,c3=st.columns([1, 2, 1])
    
    with c2:
        status_area=st.empty()
        # --- AUTOMATIC FLOW LOGIC ---
        if st.session_state.auto_mode and st.session_state.messages and st.session_state.messages[-1]['role']=='ai':
            if time.time()<st.session_state.speech_end_time:
                status_area.info(f"👂 Listening to AI...")
                time.sleep(0.5)
                st.rerun()
            else:
                if not st.session_state.start_time:
                    st.session_state.start_time = time.time()
                
                # --- TIME LIMIT CHECK ---
                if time_is_up:
                    if not st.session_state.ending_sequence_initiated:
                        st.session_state.ending_sequence_initiated = True
                        status_area.warning("⏰ Time Limit Reached. Wrapping up...")
                        
                        with st.spinner("Concluding..."):
                            settings = st.session_state.interview_settings
                            
                            # FORCE "Thank You"
                            resp = st.session_state.manager.generate_response(
                                "", 
                                settings['role'], 
                                settings['difficulty'],
                                jd_text=settings.get('jd_text', ''), 
                                time_is_up=True
                            )
                        
                        st.session_state.messages.append({"role": "ai", "content": resp})
                        
                        # 1. Start the Audio
                        speak(resp)
                        
                        # 2. Give the thread 1s to lock the audio driver before rerunning
                        # This prevents the "rerun" from killing the audio start-up
                        time.sleep(1.0)
                        
                        st.rerun()
                    else:
                        status_area.success("Interview Concluded. Finalizing Report...")
                        
                        # 3. Hardcoded Safe Wait (7 seconds)
                        # This guarantees the full "Thank you..." message plays out.
                        time.sleep(7)
                        
                        go_to_feedback()
                
                else:
                    # --- FUNKY 10s COUNTDOWN ---
                    for i in range(10, 0, -1):
                        # Logic to change color based on urgency
                        if i > 7: color = "#00d4ff"; msg = "🧘 Get Ready..."
                        elif i > 3: color = "#facc15"; msg = "🧠 Think..."
                        else: color = "#ef4444"; msg = "🔥 HERE WE GO!"

                        status_area.markdown(f"""
                            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 300px;">
                                <div class="funky-countdown" style="color: {color}; text-shadow: 0 0 20px {color}, 0 0 60px {color};">{i}</div>
                                <div class="funky-subtext" style="color: {color}; text-shadow: 0 0 10px {color};">{msg}</div>
                            </div>
                        """, unsafe_allow_html=True)
                        time.sleep(1)
                        
                    # RECORDING UI
                    status_area.markdown("""
                        <div style="text-align: center; padding: 2rem;">
                            <div class="live-badge" style="transform: scale(1.5);">🔴 RECORDING</div>
                            <p style="margin-top: 20px; color: var(--text-color); opacity: 0.7;">Speak now... (Auto-submit on silence)</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    user_text = listen(status_area)
                    status_area.empty()
                    
                    if user_text:
                        st.session_state.messages.append({"role": "user", "content": user_text})
                        if "end interview" in user_text.lower():
                            go_to_feedback()
                        else:
                            with st.spinner("Analyzing..."):
                                settings = st.session_state.interview_settings
                                resp = st.session_state.manager.generate_response(
                                    user_text, 
                                    settings['role'], 
                                    settings['difficulty'],
                                    jd_text=settings.get('jd_text', '')
                                )
                            st.session_state.messages.append({"role": "ai", "content": resp})
                            speak(resp)
                            st.rerun()
                    else:
                        # --- HANDLING SILENCE ---
                        status_area.warning("⚠️ No speech detected. Auto-mode paused.")
                        st.session_state.auto_mode = False
                        st.rerun()

        # --- MANUAL CONTROLS ---
        col_btns = st.columns(2)
        
        # 1. START/PAUSE/RESUME LOGIC
        if not st.session_state.messages:
            # Session hasn't started yet
            if col_btns[0].button("▶️ Begin Session"):
                st.session_state.start_time = time.time()
                st.session_state.auto_mode = True 
                with st.spinner("Initializing..."):
                    settings = st.session_state.interview_settings
                    intro = st.session_state.manager.generate_response(
                        f"Start interview for {settings['role']}", 
                        settings['role'], 
                        settings['difficulty'],
                        jd_text=settings.get('jd_text', '')
                    )
                    st.session_state.messages.append({"role": "ai", "content": intro})
                    speak(intro)
                    st.rerun()
        else:
            # Session is active
            if st.session_state.auto_mode:
                if col_btns[0].button("⏸️ Pause Auto"):
                    st.session_state.auto_mode = False
                    st.rerun()
            else:
                # If paused (or silenced), show RESUME only
                if col_btns[0].button("▶️ Resume Interview"):
                    st.session_state.auto_mode = True
                    st.rerun()
        
        # 2. END BUTTON (Always visible)
        if col_btns[1].button("🛑 End & Report"):
            go_to_feedback()
def go_to_feedback():
    st.session_state.auto_mode = False 
    with st.spinner("Generating Comprehensive Feedback..."):
        feedback = st.session_state.manager.end_interview()
        st.session_state.feedback_data = feedback
        st.session_state.page = 'feedback'
        st.rerun()

# --- PAGE 3: FEEDBACK ---
def render_feedback_page():
    st.markdown("<h2 style='text-align:center; margin-bottom: 10px;'>Assessment Report</h2>", unsafe_allow_html=True)
    data = st.session_state.feedback_data
    
    if not data:
        st.error("No data generated.")
        if st.button("🏠 Return Home"): st.session_state.page = 'config'; st.rerun()
        return

    st.markdown(f"""
    <div class="eightfold-card">
        <h3 style="color: #4b5563; text-align: center; margin-bottom: 1rem;">Executive Summary</h3>
        <p style="font-size: 1.1rem; line-height: 1.7; text-align: center; color: #1f2937;">{data.get('feedback_summary', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"""<div class="metric-box"><h3>🌟 Overall</h3><div class="metric-val">{data.get('score', 0)}/10</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="metric-box"><h3>🗣️ Communication </h3><div class="metric-val" style="font-size: 2rem;">{data.get('communication_rating', 'N/A')}</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="metric-box"><h3>🧠 Technical knowledge</h3><div class="metric-val" style="font-size: 2rem;">{data.get('technical_rating', 'N/A')}</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        strengths_html = "".join([f"<li style='background-color: #ecfdf5; border-left-color: #10b981;'>{s}</li>" for s in data.get('strengths', [])])
        st.markdown(f"""
        <div class="eightfold-card" style="border-left: 5px solid #10b981;">
            <h3 style="color: #059669;">✅ Key Strengths</h3>
            <ul class="content-list">
                {strengths_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        improvements_html = "".join([f"<li style='background-color: #fff7ed; border-left-color: #f97316;'>{w}</li>" for w in data.get('areas_for_improvement', [])])
        st.markdown(f"""
        <div class="eightfold-card" style="border-left: 5px solid #f59e0b;">
            <h3 style="color: #d97706;">🚀 Growth Areas</h3>
            <ul class="content-list">
                {improvements_html}
            </ul>
        </div>
        """, unsafe_allow_html=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
   # In render_feedback_page...
    if st.button("🔄 Start New Assessment", type="primary", use_container_width=True):
        st.session_state.messages = []
        st.session_state.start_time = None
        st.session_state.feedback_data = None # Clear old report
        st.session_state.manager.reset_session() # <--- CRITICAL FIX: WIPE AI MEMORY
        st.session_state.page = 'config'
        st.rerun()

# --- Main Routing ---
if not st.session_state.ready:
    st.warning("⚠️ Missing .env file with GEMINI_API_KEY")
    st.stop()

if st.session_state.page == 'config': render_config_page()
elif st.session_state.page == 'interview': render_interview_page()
elif st.session_state.page == 'feedback': render_feedback_page()
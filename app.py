import streamlit as st
import os
import json
import tempfile
from pathlib import Path
from datetime import datetime

from google import genai


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Voice Notes → Action Items",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

/* Main application */
.stApp {
    background:
        radial-gradient(circle at top left, rgba(99, 102, 241, 0.20), transparent 35%),
        radial-gradient(circle at top right, rgba(168, 85, 247, 0.15), transparent 30%),
        #0b1020;
    color: white;
}

/* Remove Streamlit default spacing */
.block-container {
    max-width: 1250px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Hide Streamlit branding */
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}


/* ============================================================
   HERO SECTION
============================================================ */

.hero {
    padding: 35px;
    border-radius: 25px;
    background:
        linear-gradient(
            135deg,
            rgba(79, 70, 229, 0.30),
            rgba(147, 51, 234, 0.20)
        );
    border: 1px solid rgba(255,255,255,0.12);
    margin-bottom: 25px;
    box-shadow: 0px 20px 60px rgba(0,0,0,0.25);
}

.pill {
    display: inline-block;
    padding: 8px 16px;
    border-radius: 999px;
    background: rgba(99,102,241,0.18);
    border: 1px solid rgba(129,140,248,0.35);
    color: #c7d2fe;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 18px;
}

.hero h1 {
    font-size: 46px;
    line-height: 1.1;
    margin-bottom: 15px;
    color: white;
}

.hero p {
    color: #cbd5e1;
    font-size: 18px;
    line-height: 1.7;
    max-width: 750px;
}


/* ============================================================
   CARDS
============================================================ */

.card {
    padding: 25px;
    border-radius: 22px;
    background: rgba(15, 23, 42, 0.75);
    border: 1px solid rgba(255,255,255,0.10);
    margin-bottom: 20px;
    box-shadow: 0px 10px 35px rgba(0,0,0,0.18);
}

.card-title {
    font-size: 21px;
    font-weight: 700;
    margin-bottom: 10px;
    color: white;
}

.card-description {
    color: #94a3b8;
    line-height: 1.6;
}


/* ============================================================
   STEP CARDS
============================================================ */

.step-card {
    padding: 20px;
    min-height: 160px;
    border-radius: 18px;
    background: rgba(30,41,59,0.65);
    border: 1px solid rgba(255,255,255,0.08);
}

.step-number {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #6366f1, #a855f7);
    font-weight: bold;
    margin-bottom: 15px;
}

.step-card h3 {
    color: white;
    margin-bottom: 8px;
}

.step-card p {
    color: #94a3b8;
    line-height: 1.6;
}


/* ============================================================
   RESULT CARDS
============================================================ */

.result-card {
    padding: 22px;
    border-radius: 18px;
    background: rgba(15,23,42,0.85);
    border: 1px solid rgba(99,102,241,0.25);
    margin-bottom: 18px;
}

.result-title {
    color: #a5b4fc;
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 12px;
}


/* ============================================================
   ACTION ITEM
============================================================ */

.action-item {
    padding: 16px;
    border-radius: 14px;
    background: rgba(30,41,59,0.8);
    border-left: 4px solid #6366f1;
    margin-bottom: 12px;
}

.action-task {
    color: white;
    font-weight: 600;
    font-size: 16px;
}

.action-meta {
    color: #94a3b8;
    font-size: 14px;
    margin-top: 7px;
}


/* ============================================================
   PRIORITY BADGES
============================================================ */

.priority-high {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(239,68,68,0.15);
    color: #fca5a5;
    font-size: 12px;
    font-weight: bold;
}

.priority-medium {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(245,158,11,0.15);
    color: #fcd34d;
    font-size: 12px;
    font-weight: bold;
}

.priority-low {
    display: inline-block;
    padding: 5px 10px;
    border-radius: 999px;
    background: rgba(34,197,94,0.15);
    color: #86efac;
    font-size: 12px;
    font-weight: bold;
}


/* ============================================================
   SIDEBAR
============================================================ */

section[data-testid="stSidebar"] {
    background: #111827;
}


/* ============================================================
   BUTTON
============================================================ */

.stButton > button {
    width: 100%;
    border-radius: 12px;
    min-height: 48px;
    font-weight: 700;
    border: none;
    background: linear-gradient(135deg, #6366f1, #9333ea);
    color: white;
}

.stButton > button:hover {
    border: none;
    transform: translateY(-1px);
}


/* ============================================================
   TEXT AREA
============================================================ */

textarea {
    border-radius: 12px !important;
}


/* ============================================================
   METRIC
============================================================ */

[data-testid="stMetric"] {
    background: rgba(30,41,59,0.55);
    border: 1px solid rgba(255,255,255,0.08);
    padding: 15px;
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "transcript" not in st.session_state:
    st.session_state.transcript = ""

if "summary" not in st.session_state:
    st.session_state.summary = ""

if "action_items" not in st.session_state:
    st.session_state.action_items = []

if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_api_key():

    """
    Get Gemini API key from:
    1. Streamlit secrets
    2. Environment variable
    3. Session state
    """

    api_key = None

    try:
        api_key = st.secrets.get("GEMINI_API_KEY", None)
    except Exception:
        pass

    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        api_key = st.session_state.get("gemini_api_key", None)

    return api_key


def create_gemini_client(api_key):

    """
    Create Gemini client.
    """

    client = genai.Client(api_key=api_key)

    return client


def save_uploaded_audio(uploaded_file):

    """
    Save uploaded audio temporarily.
    """

    file_extension = Path(uploaded_file.name).suffix

    if not file_extension:
        file_extension = ".mp3"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=file_extension
    ) as temp_file:

        temp_file.write(uploaded_file.getvalue())

        temp_path = temp_file.name

    return temp_path


def extract_json(text):

    """
    Extract JSON safely from Gemini response.
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "", 1)

    if text.startswith("```"):
        text = text.replace("```", "", 1)

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    return json.loads(text)


def analyze_audio(client, audio_path):

    """
    Upload audio to Gemini and analyze it.
    """

    uploaded_audio = client.files.upload(
        file=audio_path
    )

    prompt = """
You are an advanced AI productivity assistant.

Analyze the provided voice recording carefully.

Return ONLY valid JSON.

Do not use markdown.
Do not use code fences.
Do not add explanations outside JSON.

Use exactly this structure:

{
    "transcript": "Complete and accurate transcription of the audio",
    "summary": "Clear and concise summary",
    "action_items": [
        {
            "task": "Task that needs to be completed",
            "person": "Person responsible or Unknown",
            "deadline": "Deadline mentioned or Not specified",
            "priority": "High, Medium, or Low"
        }
    ]
}

Instructions:

1. Create a complete transcript.
2. Correct obvious speech recognition mistakes where possible.
3. Generate a useful professional summary.
4. Identify every actionable task.
5. Identify responsible people if mentioned.
6. Identify deadlines if mentioned.
7. Assign priority:
   - High = urgent or important
   - Medium = important but not urgent
   - Low = optional or less urgent
8. If there are no action items, return an empty array.
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            uploaded_audio,
            prompt
        ]
    )

    response_text = response.text

    result = extract_json(response_text)

    return result


def analyze_text(client, transcript):

    """
    Analyze manually entered transcript.
    """

    prompt = f"""
You are an advanced AI productivity assistant.

Analyze the following voice transcript.

TRANSCRIPT:

{transcript}

Return ONLY valid JSON.

Do not use markdown.
Do not use code fences.

Use exactly this structure:

{{
    "summary": "Clear and concise summary",
    "action_items": [
        {{
            "task": "Task that needs to be completed",
            "person": "Person responsible or Unknown",
            "deadline": "Deadline mentioned or Not specified",
            "priority": "High, Medium, or Low"
        }}
    ]
}}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    response_text = response.text

    result = extract_json(response_text)

    return result


def priority_class(priority):

    """
    Get CSS class for priority.
    """

    priority = str(priority).lower()

    if priority == "high":
        return "priority-high"

    elif priority == "medium":
        return "priority-medium"

    return "priority-low"


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("""
    <div style="
        padding: 15px;
        border-radius: 15px;
        background: linear-gradient(
            135deg,
            rgba(99,102,241,0.25),
            rgba(168,85,247,0.15)
        );
        margin-bottom: 20px;
    ">
        <h2 style="margin:0;">🎙️ Voice AI</h2>
        <p style="color:#94a3b8;">
            Turn conversations into action.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🔑 Gemini API")

    api_input = st.text_input(
        "Enter your Gemini API Key",
        type="password",
        placeholder="AIza..."
    )

    if api_input:
        st.session_state.gemini_api_key = api_input

    st.markdown("---")

    st.markdown("### 📊 Session")

    transcript_words = len(
        st.session_state.transcript.split()
    )

    action_count = len(
        st.session_state.action_items
    )

    st.metric(
        "Transcript Words",
        transcript_words
    )

    st.metric(
        "Action Items",
        action_count
    )

    st.markdown("---")

    if st.button("🗑️ Clear Session"):

        st.session_state.transcript = ""
        st.session_state.summary = ""
        st.session_state.action_items = []
        st.session_state.processing_complete = False

        st.rerun()


# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="hero">

    <div class="pill">
        ✨ AI Productivity Assistant
    </div>

    <h1>
        Voice Notes →
        <br>
        Action Items
    </h1>

    <p>
        Record or upload your voice and instantly transform it
        into an accurate transcript, intelligent summary,
        structured tasks, responsible people and deadlines.
    </p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# HOW IT WORKS
# ============================================================

st.markdown("## 🎯 How It Works")

step1, step2, step3 = st.columns(3)

with step1:

    st.markdown("""
    <div class="step-card">

        <div class="step-number">1</div>

        <h3>🎙️ Listen</h3>

        <p>
            Upload or record your voice.
            Gemini understands your audio.
        </p>

    </div>
    """, unsafe_allow_html=True)


with step2:

    st.markdown("""
    <div class="step-card">

        <div class="step-number">2</div>

        <h3>🧠 Understand</h3>

        <p>
            AI creates an accurate transcript
            and understands the conversation.
        </p>

    </div>
    """, unsafe_allow_html=True)


with step3:

    st.markdown("""
    <div class="step-card">

        <div class="step-number">3</div>

        <h3>✅ Organize</h3>

        <p>
            Automatically extract tasks,
            people, priorities and deadlines.
        </p>

    </div>
    """, unsafe_allow_html=True)


st.markdown("<br>", unsafe_allow_html=True)


# ============================================================
# INPUT SECTION
# ============================================================

st.markdown("""
<div class="card">

    <div class="card-title">
        🎙️ Add Your Voice Note
    </div>

    <div class="card-description">
        Upload an audio file or record your voice directly.
    </div>

</div>
""", unsafe_allow_html=True)


input_tab1, input_tab2 = st.tabs(
    [
        "📁 Upload Audio",
        "✍️ Paste Transcript"
    ]
)


# ============================================================
# UPLOAD AUDIO TAB
# ============================================================

with input_tab1:

    uploaded_file = st.file_uploader(
        "Upload your voice recording",
        type=[
            "mp3",
            "wav",
            "m4a",
            "ogg",
            "aac",
            "flac"
        ]
    )

    if uploaded_file:

        st.success(
            f"Audio selected: {uploaded_file.name}"
        )

        try:
            st.audio(
                uploaded_file.getvalue()
            )
        except Exception:
            pass


    process_audio_button = st.button(
        "🚀 Analyze Voice Note",
        disabled=(uploaded_file is None)
    )


    if process_audio_button:

        api_key = get_api_key()

        if not api_key:

            st.error(
                "Please enter your Gemini API Key in the sidebar."
            )

        elif uploaded_file is None:

            st.warning(
                "Please upload an audio file first."
            )

        else:

            temp_path = None

            try:

                with st.spinner(
                    "🤖 Gemini is listening and analyzing your voice..."
                ):

                    client = create_gemini_client(
                        api_key
                    )

                    temp_path = save_uploaded_audio(
                        uploaded_file
                    )

                    result = analyze_audio(
                        client,
                        temp_path
                    )

                    st.session_state.transcript = (
                        result.get(
                            "transcript",
                            ""
                        )
                    )

                    st.session_state.summary = (
                        result.get(
                            "summary",
                            ""
                        )
                    )

                    st.session_state.action_items = (
                        result.get(
                            "action_items",
                            []
                        )
                    )

                    st.session_state.processing_complete = True

                st.success(
                    "Voice note analyzed successfully!"
                )

                st.rerun()


            except Exception as e:

                st.error(
                    "Gemini processing failed."
                )

                st.code(
                    str(e)
                )


            finally:

                if temp_path:

                    try:
                        os.remove(
                            temp_path
                        )
                    except Exception:
                        pass


# ============================================================
# MANUAL TRANSCRIPT TAB
# ============================================================

with input_tab2:

    manual_transcript = st.text_area(
        "Paste your transcript here",
        height=250,
        placeholder="""
Example:

Tomorrow we need to finish the presentation.

Rahul will prepare the design.

I will complete the final report by Friday.

The meeting is scheduled for Monday.
"""
    )


    analyze_text_button = st.button(
        "🧠 Analyze Transcript",
        disabled=(
            not manual_transcript.strip()
        )
    )


    if analyze_text_button:

        api_key = get_api_key()

        if not api_key:

            st.error(
                "Please enter your Gemini API Key in the sidebar."
            )

        else:

            try:

                with st.spinner(
                    "🤖 Gemini is analyzing the transcript..."
                ):

                    client = create_gemini_client(
                        api_key
                    )

                    result = analyze_text(
                        client,
                        manual_transcript
                    )

                    st.session_state.transcript = (
                        manual_transcript
                    )

                    st.session_state.summary = (
                        result.get(
                            "summary",
                            ""
                        )
                    )

                    st.session_state.action_items = (
                        result.get(
                            "action_items",
                            []
                        )
                    )

                    st.session_state.processing_complete = True


                st.success(
                    "Transcript analyzed successfully!"
                )

                st.rerun()


            except Exception as e:

                st.error(
                    "Gemini analysis failed."
                )

                st.code(
                    str(e)
                )


# ============================================================
# RESULTS
# ============================================================

if st.session_state.processing_complete:

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">

        <div class="pill">
            ✨ Analysis Complete
        </div>

        <h2 style="color:white;">
            Your AI Results
        </h2>

        <p>
            Review the transcript, summary
            and automatically extracted action items.
        </p>

    </div>
    """, unsafe_allow_html=True)


    result_tab1, result_tab2, result_tab3 = st.tabs(
        [
            "📄 Transcript",
            "🧠 Summary",
            "✅ Action Items"
        ]
    )


    # ========================================================
    # TRANSCRIPT
    # ========================================================

    with result_tab1:

        st.markdown("""
        <div class="result-card">

            <div class="result-title">
                🎙️ Complete Transcript
            </div>

        </div>
        """, unsafe_allow_html=True)


        st.text_area(
            "Transcript",
            value=st.session_state.transcript,
            height=400,
            key="transcript_display"
        )


        st.download_button(
            label="⬇️ Download Transcript",
            data=st.session_state.transcript,
            file_name="voice_transcript.txt",
            mime="text/plain"
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    with result_tab2:

        st.markdown("""
        <div class="result-card">

            <div class="result-title">
                🧠 AI Generated Summary
            </div>

        </div>
        """, unsafe_allow_html=True)


        st.write(
            st.session_state.summary
        )


        st.download_button(
            label="⬇️ Download Summary",
            data=st.session_state.summary,
            file_name="voice_summary.txt",
            mime="text/plain"
        )


    # ========================================================
    # ACTION ITEMS
    # ========================================================

    with result_tab3:

        action_items = (
            st.session_state.action_items
        )


        if not action_items:

            st.info(
                "No action items were found."
            )

        else:

            high_count = sum(
                1
                for item in action_items
                if str(
                    item.get(
                        "priority",
                        ""
                    )
                ).lower() == "high"
            )


            medium_count = sum(
                1
                for item in action_items
                if str(
                    item.get(
                        "priority",
                        ""
                    )
                ).lower() == "medium"
            )


            low_count = sum(
                1
                for item in action_items
                if str(
                    item.get(
                        "priority",
                        ""
                    )
                ).lower() == "low"
            )


            metric1, metric2, metric3, metric4 = (
                st.columns(4)
            )


            metric1.metric(
                "Total Tasks",
                len(action_items)
            )

            metric2.metric(
                "🔴 High",
                high_count
            )

            metric3.metric(
                "🟡 Medium",
                medium_count
            )

            metric4.metric(
                "🟢 Low",
                low_count
            )


            st.markdown("<br>", unsafe_allow_html=True)


            for index, item in enumerate(
                action_items,
                start=1
            ):

                task = item.get(
                    "task",
                    "No task description"
                )

                person = item.get(
                    "person",
                    "Unknown"
                )

                deadline = item.get(
                    "deadline",
                    "Not specified"
                )

                priority = item.get(
                    "priority",
                    "Low"
                )

                css_class = priority_class(
                    priority
                )


                st.markdown(
                    f"""
                    <div class="action-item">

                        <div class="action-task">
                            {index}. {task}
                        </div>

                        <div class="action-meta">

                            👤 <b>Responsible:</b> {person}

                            <br><br>

                            📅 <b>Deadline:</b> {deadline}

                            <br><br>

                            <span class="{css_class}">
                                {priority} Priority
                            </span>

                        </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )


            # ================================================
            # DOWNLOAD JSON
            # ================================================

            action_json = json.dumps(
                action_items,
                indent=4
            )


            st.download_button(
                label="⬇️ Download Action Items JSON",
                data=action_json,
                file_name="action_items.json",
                mime="application/json"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="
    text-align:center;
    color:#64748b;
    padding:25px;
">

    🎙️ Voice Notes → Action Items

    <br>

    Powered by Gemini AI ✨

</div>
""", unsafe_allow_html=True)

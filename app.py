import streamlit as st
from groq import Groq
import os
import json


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="VoiceNotes AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>

    .main {
        background-color: #f8fafc;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #2563eb, #7c3aed);
        color: white;
        margin-bottom: 2rem;
    }

    .hero h1 {
        color: white;
        margin-bottom: 0.5rem;
    }

    .hero p {
        font-size: 18px;
        opacity: 0.9;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 10px;
        margin-bottom: 15px;
    }

    .feature-card {
        padding: 20px;
        border-radius: 15px;
        background: white;
        border: 1px solid #e5e7eb;
        min-height: 170px;
    }

    .task-card {
        padding: 15px;
        border-radius: 15px;
        background: white;
        border: 1px solid #e5e7eb;
        margin-bottom: 12px;
    }

    .small-text {
        color: #64748b;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "result" not in st.session_state:
    st.session_state.result = None

if "transcript" not in st.session_state:
    st.session_state.transcript = ""


# ============================================================
# API KEY
# ============================================================

api_key = os.getenv("GROQ_API_KEY")


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🎙️ VoiceNotes AI")

    st.caption(
        "Turn voice notes into summaries, "
        "tasks and deadlines using AI."
    )

    st.divider()

    st.markdown("### ⚙️ Features")

    st.write("🗣️ Speech-to-Text")
    st.write("✨ AI Summaries")
    st.write("✅ Action Items")
    st.write("📅 Deadline Detection")
    st.write("⚡ Priority Detection")

    st.divider()

    st.markdown("### 📊 Processing History")

    st.metric(
        "Notes Processed",
        len(st.session_state.history)
    )

    if st.button(
        "🗑️ Clear History",
        use_container_width=True
    ):
        st.session_state.history = []
        st.session_state.result = None
        st.session_state.transcript = ""
        st.rerun()

    st.divider()

    st.caption(
        "Built with Streamlit + Speech-to-Text + AI"
    )


# ============================================================
# HERO SECTION
# ============================================================

st.markdown("""
<div class="hero">

<h1>🎙️ Voice Notes → Action Items</h1>

<p>
Transform your voice notes into clear summaries,
actionable tasks and important deadlines.
</p>

</div>
""", unsafe_allow_html=True)


# ============================================================
# MAIN TABS
# ============================================================

tab1, tab2 = st.tabs([
    "🎤 Process Voice Note",
    "📚 History"
])


# ============================================================
# TAB 1 - PROCESS AUDIO
# ============================================================

with tab1:

    left, right = st.columns(
        [1, 1],
        gap="large"
    )

    # --------------------------------------------------------
    # LEFT SIDE - AUDIO INPUT
    # --------------------------------------------------------

    with left:

        st.markdown(
            '<div class="section-title">'
            '🎤 Add Your Voice Note'
            '</div>',
            unsafe_allow_html=True
        )

        input_method = st.radio(
            "Choose input method",
            [
                "📁 Upload Audio",
                "🎙️ Record Audio"
            ],
            horizontal=True
        )

        audio_file = None

        if input_method == "📁 Upload Audio":

            uploaded_file = st.file_uploader(
                "Upload an audio file",
                type=[
                    "mp3",
                    "wav",
                    "m4a",
                    "ogg",
                    "webm"
                ]
            )

            if uploaded_file:
                audio_file = uploaded_file

        else:

            recorded_audio = st.audio_input(
                "Record your voice note"
            )

            if recorded_audio:
                audio_file = recorded_audio


        if audio_file:

            st.success(
                "Audio ready for processing!"
            )

            st.audio(audio_file)

            process_button = st.button(
                "✨ Process with AI",
                use_container_width=True,
                type="primary"
            )

        else:

            process_button = False

            st.info(
                "Upload or record a voice note "
                "to begin."
            )


    # --------------------------------------------------------
    # RIGHT SIDE - HOW IT WORKS
    # --------------------------------------------------------

    with right:

        st.markdown(
            '<div class="section-title">'
            '🤖 AI Processing'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown("""
<div class="feature-card">

### 1️⃣ Speech Recognition

Your voice is converted into an accurate
text transcript.

<br>

### 2️⃣ AI Understanding

The AI understands the meaning and
important information.

<br>

### 3️⃣ Smart Extraction

Tasks, priorities and deadlines are
automatically identified.

</div>
""", unsafe_allow_html=True)


    # ========================================================
    # PROCESS BUTTON
    # ========================================================

    if process_button:

        if not api_key:

            st.error(
                "🔑 GROQ API key not configured. "
                "Add GROQ_API_KEY to your deployment secrets."
            )

        else:

            try:

                client = GROQ(
                    api_key=api_key
                )


                # =================================================
                # SPEECH TO TEXT
                # =================================================

                with st.spinner(
                    "🗣️ Converting your voice into text..."
                ):

                    transcription = (
                        client.audio.transcriptions.create(
                            model="whisper-large-v3-turbo",
                            file=audio_file
                        )
                    )

                transcript = transcription.text

                st.session_state.transcript = transcript


                # =================================================
                # AI ANALYSIS
                # =================================================

                with st.spinner(
                    "🤖 AI is finding tasks and deadlines..."
                ):

                    prompt = f"""
Analyze this voice note transcript.

Return ONLY valid JSON.

Use this exact structure:

{{
    "summary": "A short and clear summary",

    "action_items": [
        {{
            "task": "Description of the task",
            "deadline": "Deadline or Not specified",
            "priority": "High, Medium, or Low"
        }}
    ],

    "deadlines": [
        "Deadline 1",
        "Deadline 2"
    ],

    "key_people": [
        "Names of people mentioned"
    ]
}}

Instructions:

- Extract every actionable task.
- Identify deadlines and dates.
- Assign High, Medium or Low priority.
- Create a concise summary.
- Identify important people mentioned.
- If information is unavailable,
  return an empty list where appropriate.
- Return ONLY valid JSON.
- Do not use markdown.

VOICE NOTE TRANSCRIPT:

{transcript}
"""

                    response = (
                        client.chat.completions.create(

                            model="llama-3.3-70b-versatile",

                            messages=[
                                {
                                    "role": "system",

                                    "content": (
                                        "You are an AI productivity "
                                        "assistant that converts voice "
                                        "notes into structured tasks."
                                    )
                                },

                                {
                                    "role": "user",

                                    "content": prompt
                                }
                            ]
                        )
                    )


                result_text = (
                    response
                    .choices[0]
                    .message
                    .content
                )


                # =================================================
                # CLEAN JSON RESPONSE
                # =================================================

                result_text = (
                    result_text
                    .replace("```json", "")
                    .replace("```", "")
                    .strip()
                )

                data = json.loads(
                    result_text
                )


                # =================================================
                # SAVE RESULT
                # =================================================

                st.session_state.result = data

                st.session_state.history.append({
                    "transcript": transcript,
                    "summary": data.get(
                        "summary",
                        ""
                    ),
                    "action_count": len(
                        data.get(
                            "action_items",
                            []
                        )
                    )
                })

                st.success(
                    "🎉 Voice note processed successfully!"
                )


            except json.JSONDecodeError:

                st.error(
                    "AI returned an invalid format. "
                    "Please try processing again."
                )


            except Exception as e:

                st.error(
                    f"Processing error: {str(e)}"
                )


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    if st.session_state.result:

        data = st.session_state.result

        st.divider()

        st.markdown(
            "## 📊 AI Analysis Results"
        )


        # ====================================================
        # METRICS
        # ====================================================

        metric1, metric2, metric3 = st.columns(3)

        action_count = len(
            data.get(
                "action_items",
                []
            )
        )

        deadline_count = len(
            data.get(
                "deadlines",
                []
            )
        )

        people_count = len(
            data.get(
                "key_people",
                []
            )
        )

        metric1.metric(
            "✅ Action Items",
            action_count
        )

        metric2.metric(
            "📅 Deadlines",
            deadline_count
        )

        metric3.metric(
            "👥 People Mentioned",
            people_count
        )


        # ====================================================
        # RESULT TABS
        # ====================================================

        result_tab1, result_tab2, result_tab3, result_tab4 = (
            st.tabs([
                "📝 Transcript",
                "✨ Summary",
                "✅ Tasks",
                "📅 Details"
            ])
        )


        # ----------------------------------------------------
        # TRANSCRIPT
        # ----------------------------------------------------

        with result_tab1:

            st.markdown(
                "### Complete Transcript"
            )

            st.text_area(
                "Transcript",
                value=st.session_state.transcript,
                height=250,
                disabled=True,
                label_visibility="collapsed"
            )


        # ----------------------------------------------------
        # SUMMARY
        # ----------------------------------------------------

        with result_tab2:

            st.markdown(
                "### ✨ AI Summary"
            )

            st.success(
                data.get(
                    "summary",
                    "No summary generated."
                )
            )


        # ----------------------------------------------------
        # ACTION ITEMS
        # ----------------------------------------------------

        with result_tab3:

            action_items = data.get(
                "action_items",
                []
            )

            if action_items:

                for index, item in enumerate(
                    action_items,
                    start=1
                ):

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f"### {index}. "
                            f"{item.get('task', 'Task')}"
                        )

                        col1, col2 = st.columns(2)

                        with col1:

                            st.write(
                                "📅 **Deadline:** "
                                f"{item.get('deadline', 'Not specified')}"
                            )

                        with col2:

                            priority = item.get(
                                "priority",
                                "Medium"
                            )

                            st.write(
                                f"⚡ **Priority:** {priority}"
                            )

            else:

                st.info(
                    "No action items were detected."
                )


        # ----------------------------------------------------
        # DEADLINES + PEOPLE
        # ----------------------------------------------------

        with result_tab4:

            col1, col2 = st.columns(2)

            with col1:

                st.markdown(
                    "### 📅 Important Dates"
                )

                deadlines = data.get(
                    "deadlines",
                    []
                )

                if deadlines:

                    for deadline in deadlines:

                        st.write(
                            f"📌 {deadline}"
                        )

                else:

                    st.info(
                        "No deadlines mentioned."
                    )


            with col2:

                st.markdown(
                    "### 👥 People Mentioned"
                )

                people = data.get(
                    "key_people",
                    []
                )

                if people:

                    for person in people:

                        st.write(
                            f"👤 {person}"
                        )

                else:

                    st.info(
                        "No people detected."
                    )


# ============================================================
# TAB 2 - HISTORY
# ============================================================

with tab2:

    st.markdown(
        "## 📚 Processing History"
    )

    history = st.session_state.history

    if history:

        for index, item in enumerate(
            reversed(history),
            start=1
        ):

            with st.expander(
                f"Voice Note {index} — "
                f"{item['action_count']} Tasks"
            ):

                st.markdown(
                    "### ✨ Summary"
                )

                st.write(
                    item["summary"]
                )

                st.markdown(
                    "### 📝 Transcript"
                )

                st.write(
                    item["transcript"]
                )

    else:

        st.info(
            "Your processed voice notes "
            "will appear here."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🎙️ VoiceNotes AI • "
    "AI-powered Speech-to-Text & Action Item Extraction"
                )

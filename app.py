import streamlit as st
from groq import Groq
import json
from datetime import datetime

# ------------------------------------------------------------
# Voice Notes -> Action Items
# Groq Speech-to-Text + LLM Summary + Action Extraction
# ------------------------------------------------------------

st.set_page_config(
    page_title="VoiceNotes AI",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------- STYLE ---------------------------

st.markdown("""
<style>
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 3rem 3.2rem;
        border-radius: 28px;
        background: linear-gradient(135deg, #1f4db7 0%, #6b2ccf 100%);
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 12px 30px rgba(43, 55, 130, 0.18);
    }

    .hero h1 {
        color: white;
        font-size: 3.2rem;
        line-height: 1.05;
        margin-bottom: 1rem;
    }

    .hero p {
        color: rgba(255,255,255,0.88);
        font-size: 1.2rem;
        max-width: 720px;
    }

    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    .feature-card {
        padding: 1.5rem;
        border: 1px solid rgba(49, 51, 63, 0.15);
        border-radius: 18px;
        min-height: 180px;
        background: rgba(255,255,255,0.03);
    }

    .result-card {
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid rgba(49, 51, 63, 0.15);
        margin-bottom: 1rem;
        background: rgba(255,255,255,0.04);
    }

    .action-item {
        padding: 0.85rem 1rem;
        margin: 0.55rem 0;
        border-left: 4px solid #6b2ccf;
        border-radius: 8px;
        background: rgba(107, 44, 207, 0.07);
    }

    .small-muted {
        color: #6b7280;
        font-size: 0.92rem;
    }
</style>
""", unsafe_allow_html=True)


# ----------------------- INITIAL STATE -----------------------

if "history" not in st.session_state:
    st.session_state.history = []

if "last_result" not in st.session_state:
    st.session_state.last_result = None


# ------------------------- API CLIENT -------------------------

def get_client():
    """Create a Groq client using Streamlit Secrets."""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        st.error(
            "Groq API key not found. Add GROQ_API_KEY to Streamlit Secrets."
        )
        st.stop()

    if not api_key or not str(api_key).strip():
        st.error("Your GROQ_API_KEY is empty. Please check Streamlit Secrets.")
        st.stop()

    return Groq(api_key=str(api_key).strip())


# ----------------------- AI FUNCTIONS ------------------------

def transcribe_audio(client, audio_file, language=None):
    """Convert uploaded/recorded audio to text using Groq Whisper."""

    audio_bytes = audio_file.getvalue()

    filename = getattr(audio_file, "name", None)

    if not filename:
        filename = "voice_note.wav"

    kwargs = {
        "file": (filename, audio_bytes),
        "model": "whisper-large-v3-turbo",
        "response_format": "json",
        "temperature": 0.0,
    }

    if language and language != "Auto Detect":
        kwargs["language"] = language

    transcription = client.audio.transcriptions.create(**kwargs)

    return transcription.text


def analyze_transcript(client, transcript):
    """Create summary, key points, action items and deadlines."""

    prompt = f"""
You are an intelligent meeting and voice-note assistant.

Analyze the transcript below and return ONLY valid JSON.
Do not include markdown or text outside the JSON.

Transcript:
{transcript}

Use exactly this structure:

{{
  "title": "short descriptive title",
  "summary": "clear concise paragraph summary",
  "key_points": [
    "point 1",
    "point 2"
  ],
  "action_items": [
    {{
      "task": "specific action",
      "owner": "person if mentioned, otherwise Unassigned",
      "priority": "High, Medium, or Low",
      "deadline": "deadline if mentioned, otherwise Not specified"
    }}
  ],
  "deadlines": [
    "deadline 1"
  ],
  "decisions": [
    "decision 1"
  ]
}}

Rules:

- Extract only information supported by the transcript.
- If there are no action items, return an empty list.
- If no deadline is mentioned, return an empty deadlines list.
- Make the summary professional and easy to read.
"""

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",

        messages=[
            {
                "role": "system",
                "content": (
                    "You extract structured and accurate information "
                    "from voice transcripts. Always return valid JSON."
                ),
            },

            {
                "role": "user",
                "content": prompt,
            },
        ],

        temperature=0.2,

        response_format={
            "type": "json_object"
        },
    )

    content = completion.choices[0].message.content

    return json.loads(content)


# ---------------------- DISPLAY RESULTS ----------------------

def display_results(transcript, analysis):

    st.markdown("---")

    st.markdown("## ✨ Your AI Results")

    title = analysis.get(
        "title",
        "Voice Note Analysis"
    )

    summary = analysis.get(
        "summary",
        ""
    )

    st.markdown(f"### 📌 {title}")


    # SUMMARY

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True
    )

    st.markdown("### 📝 Smart Summary")

    st.write(
        summary or
        "No summary generated."
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # KEY POINTS + DEADLINES

    col1, col2 = st.columns(2)


    with col1:

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True
        )

        st.markdown("### 🔑 Key Points")

        points = analysis.get(
            "key_points",
            []
        )

        if points:

            for point in points:

                st.markdown(
                    f"- {point}"
                )

        else:

            st.write(
                "No key points identified."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    with col2:

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True
        )

        st.markdown("### 📅 Deadlines")

        deadlines = analysis.get(
            "deadlines",
            []
        )

        if deadlines:

            for deadline in deadlines:

                st.markdown(
                    f"- {deadline}"
                )

        else:

            st.write(
                "No specific deadlines identified."
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # ACTION ITEMS

    st.markdown(
        '<div class="result-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        "### ✅ Action Items"
    )

    actions = analysis.get(
        "action_items",
        []
    )

    if actions:

        for index, action in enumerate(
            actions,
            start=1
        ):

            task = action.get(
                "task",
                "Action item"
            )

            owner = action.get(
                "owner",
                "Unassigned"
            )

            priority = action.get(
                "priority",
                "Medium"
            )

            deadline = action.get(
                "deadline",
                "Not specified"
            )


            st.markdown(
                f"""
                <div class="action-item">

                    <b>{index}. {task}</b><br>

                    👤 Owner: {owner}<br>

                    🎯 Priority: {priority}<br>

                    📅 Deadline: {deadline}

                </div>
                """,

                unsafe_allow_html=True
            )

    else:

        st.write(
            "No action items were identified."
        )


    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )


    # DECISIONS

    decisions = analysis.get(
        "decisions",
        []
    )

    if decisions:

        st.markdown(
            '<div class="result-card">',
            unsafe_allow_html=True
        )

        st.markdown(
            "### 🤝 Decisions"
        )

        for decision in decisions:

            st.markdown(
                f"- {decision}"
            )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


    # TRANSCRIPT

    with st.expander(
        "📄 View Full Transcript"
    ):

        st.text_area(
            "Transcript",

            value=transcript,

            height=260,

            key="transcript_display",
        )


    # DOWNLOAD

    export_data = {

        "transcript": transcript,

        "analysis": analysis,

    }


    st.download_button(

        "⬇️ Download Results as JSON",

        data=json.dumps(
            export_data,
            indent=2,
            ensure_ascii=False
        ),

        file_name="voice_notes_analysis.json",

        mime="application/json",

        use_container_width=True,

    )


# --------------------------- HERO ----------------------------

st.markdown(
"""
<div class="hero">

    <h1>
        🎙️ Voice Notes →<br>
        Action Items
    </h1>

    <p>
        Transform your voice notes into accurate transcripts,
        clear summaries, actionable tasks and important deadlines.
    </p>

</div>
""",

unsafe_allow_html=True
)


# --------------------------- TABS ----------------------------

tab1, tab2 = st.tabs(

    [
        "🎙️ Process Voice Note",
        "📚 History"
    ]

)


# ------------------------- PROCESS TAB -----------------------

with tab1:


    st.markdown(

        '<div class="section-title">'
        '🎙️ Add Your Voice Note'
        '</div>',

        unsafe_allow_html=True

    )


    st.caption(

        "Upload an audio file or record a new "
        "voice note directly in the app."

    )


    input_method = st.radio(

        "Choose input method",

        [
            "📁 Upload Audio",
            "🎤 Record Audio"
        ],

        horizontal=True,

    )


    language = st.selectbox(

        "Spoken language",

        [

            "Auto Detect",

            "en",

            "hi",

            "mr",

            "te",

            "ta",

            "kn",

            "bn",

        ],

        help=(
            "Choose Auto Detect "
            "if you are unsure."
        ),

    )


    audio_file = None


    # UPLOAD AUDIO

    if input_method == "📁 Upload Audio":

        audio_file = st.file_uploader(

            "Upload an audio file",

            type=[

                "mp3",

                "wav",

                "m4a",

                "ogg",

                "webm",

                "mp4",

                "mpeg",

            ],

            help=(
                "Supported: MP3, WAV, M4A, "
                "OGG and WEBM."
            ),

        )


    # RECORD AUDIO

    else:

        audio_file = st.audio_input(

            "Record your voice note"

        )


    # PROCESS AUDIO

    if audio_file is not None:


        st.audio(
            audio_file
        )


        if st.button(

            "🚀 Transcribe & Analyze",

            type="primary",

            use_container_width=True,

        ):


            try:


                client = get_client()


                progress = st.progress(

                    0,

                    text=(
                        "Preparing your voice note..."
                    )

                )


                progress.progress(

                    25,

                    text=(
                        "Converting speech to text..."
                    )

                )


                transcript = transcribe_audio(

                    client,

                    audio_file,

                    language=language,

                )


                if not transcript or not transcript.strip():

                    raise ValueError(

                        "No speech could be detected "
                        "in the audio."

                    )


                progress.progress(

                    60,

                    text=(
                        "AI is understanding "
                        "the transcript..."
                    )

                )


                analysis = analyze_transcript(

                    client,

                    transcript

                )


                progress.progress(

                    100,

                    text=(
                        "Completed successfully!"
                    )

                )


                st.session_state.last_result = {

                    "transcript": transcript,

                    "analysis": analysis,

                    "created_at": datetime.now().strftime(

                        "%d %b %Y, %I:%M %p"

                    ),

                }


                st.session_state.history.insert(

                    0,

                    st.session_state.last_result,

                )


                display_results(

                    transcript,

                    analysis

                )


            except Exception as error:


                error_text = str(error)


                if (

                    "credit_balance_exhausted"
                    in error_text

                    or

                    "no credits"
                    in error_text.lower()

                ):


                    st.error(

                        "Groq API request failed "
                        "because your API account "
                        "has no available credits "
                        "or quota."

                    )


                elif (

                    "api_key"
                    in error_text.lower()

                    or

                    "authentication"
                    in error_text.lower()

                ):


                    st.error(

                        "Groq API authentication failed. "
                        "Please check that your "
                        "GROQ_API_KEY in Streamlit Secrets "
                        "is correct."

                    )


                else:


                    st.error(

                        f"Processing error: {error_text}"

                    )


    else:


        st.info(

            "Upload or record a voice note "
            "to begin."

        )


    # AI PROCESSING SECTION

    st.markdown("---")

    st.markdown(
        "## 🤖 AI Processing"
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        st.markdown(

        """
        <div class="feature-card">

            <h3>
                1️⃣ Speech Recognition
            </h3>

            <p>
                Your voice is converted
                into an accurate text
                transcript.
            </p>

        </div>
        """,

        unsafe_allow_html=True

        )


    with c2:

        st.markdown(

        """
        <div class="feature-card">

            <h3>
                2️⃣ AI Understanding
            </h3>

            <p>
                The AI identifies important
                information and context.
            </p>

        </div>
        """,

        unsafe_allow_html=True

        )


    with c3:

        st.markdown(

        """
        <div class="feature-card">

            <h3>
                3️⃣ Smart Extraction
            </h3>

            <p>
                Tasks, priorities, owners
                and deadlines are automatically
                identified.
            </p>

        </div>
        """,

        unsafe_allow_html=True

        )


# ------------------------- HISTORY TAB -----------------------

with tab2:


    st.markdown(

        '<div class="section-title">'
        '📚 Processing History'
        '</div>',

        unsafe_allow_html=True

    )


    if not st.session_state.history:


        st.info(

            "Your processed voice notes "
            "will appear here during "
            "this session."

        )


    else:


        for index, item in enumerate(

            st.session_state.history

        ):


            analysis = item["analysis"]


            title = analysis.get(

                "title",

                "Voice Note"

            )


            created_at = item.get(

                "created_at",

                ""

            )


            with st.expander(

                f"📝 {title} — {created_at}"

            ):


                st.markdown(
                    "### Summary"
                )


                st.write(

                    analysis.get(
                        "summary",
                        ""
                    )

                )


                st.markdown(
                    "### Action Items"
                )


                actions = analysis.get(

                    "action_items",

                    []

                )


                if actions:


                    for action in actions:


                        st.markdown(

                            f"- **{action.get('task', 'Task')}** "
                            f"({action.get('priority', 'Medium')} "
                            f"priority)"

                        )


                else:


                    st.write(
                        "No action items."
                    )


                with st.expander(
                    "View Transcript"
                ):


                    st.write(
                        item["transcript"]
                    )


        if st.button(
            "🗑️ Clear History"
        ):


            st.session_state.history = []


            st.rerun()


# --------------------------- FOOTER --------------------------

st.markdown("---")

st.markdown(

    """
    <p class='small-muted'>
        🎙️ VoiceNotes AI •
        AI-powered Speech-to-Text,
        Summaries & Action Item Extraction
    </p>
    """,

    unsafe_allow_html=True

    )

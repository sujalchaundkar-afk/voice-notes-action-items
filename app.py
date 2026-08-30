import streamlit as st
from google import genai
import os
import json
import tempfile
from datetime import datetime


# ============================================================
# APP SETTINGS
# ============================================================

APP_NAME = "VoiceNotes AI"

APP_TAGLINE = (
    "Turn voice notes into transcripts, summaries, "
    "tasks, priorities and deadlines."
)

GEMINI_MODEL = "gemini-3.7-flash"


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROFESSIONAL UI CSS
# ============================================================

st.markdown(
    """
<style>

.block-container {

    max-width: 1180px;

    padding-top: 1.5rem;

    padding-bottom: 4rem;

}


/* HERO */

.hero {

    padding: 3rem;

    border-radius: 28px;

    background:
        linear-gradient(
            135deg,
            #1d4ed8,
            #4f46e5,
            #7c3aed
        );

    color: white;

    box-shadow:
        0 18px 50px
        rgba(49,46,129,.20);

    margin-bottom: 1.5rem;

}


.hero h1 {

    color: white;

    font-size:
        clamp(
            2.4rem,
            5vw,
            4.5rem
        );

    line-height: 1.02;

    margin: 0;

}


.hero p {

    color:
        rgba(
            255,
            255,
            255,
            .90
        );

    font-size: 1.08rem;

    max-width: 760px;

    margin-top: 1rem;

}


.pill {

    display: inline-block;

    padding:
        .4rem
        .75rem;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            .30
        );

    border-radius: 999px;

    background:
        rgba(
            255,
            255,
            255,
            .12
        );

    font-size: .84rem;

    margin-bottom: 1rem;

}


/* GENERAL CARDS */

.card {

    border:
        1px solid
        rgba(
            120,
            120,
            130,
            .18
        );

    border-radius: 18px;

    padding: 1.25rem;

    background:
        rgba(
            255,
            255,
            255,
            .03
        );

    margin-bottom: 1rem;

}


.task-card {

    border:
        1px solid
        rgba(
            120,
            120,
            130,
            .18
        );

    border-left:
        5px solid
        #7c3aed;

    border-radius: 14px;

    padding: 1rem;

    margin:
        .7rem
        0;

    background:
        rgba(
            124,
            58,
            237,
            .055
        );

}


.deadline-card {

    border:
        1px solid
        rgba(
            120,
            120,
            130,
            .18
        );

    border-radius: 14px;

    padding:
        .9rem
        1rem;

    margin:
        .55rem
        0;

    background:
        rgba(
            37,
            99,
            235,
            .05
        );

}


/* METRICS */

div[data-testid="stMetric"] {

    border:
        1px solid
        rgba(
            120,
            120,
            130,
            .18
        );

    border-radius: 16px;

    padding: 1rem;

    background:
        rgba(
            255,
            255,
            255,
            .025
        );

}


/* BUTTONS */

.stButton > button {

    border-radius: 14px;

    min-height: 3rem;

    font-weight: 700;

}


.stDownloadButton > button {

    border-radius: 14px;

    min-height: 2.8rem;

}


/* MOBILE */

@media(max-width:700px) {

    .hero {

        padding:
            2rem
            1.4rem;

        border-radius: 22px;

    }


    .hero p {

        font-size: 1rem;

    }


    .block-container {

        padding-top: 1rem;

    }

}

</style>
""",

    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:

    st.session_state.history = []


if "transcript" not in st.session_state:

    st.session_state.transcript = ""


if "analysis" not in st.session_state:

    st.session_state.analysis = None


if "audio_name" not in st.session_state:

    st.session_state.audio_name = ""


if "ask_answer" not in st.session_state:

    st.session_state.ask_answer = ""


# ============================================================
# GEMINI API KEY
# ============================================================

def get_api_key():

    try:

        key = st.secrets[
            "GEMINI_API_KEY"
        ]

        if key:

            return str(
                key
            ).strip()

    except Exception:

        pass


    key = os.getenv(
        "GEMINI_API_KEY"
    )


    if key:

        return key.strip()


    return None


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

def get_client():

    key = get_api_key()


    if not key:

        st.error(
            "🔑 Gemini API key is not configured."
        )


        st.info(
            'Add GEMINI_API_KEY = "your_key" '
            "inside Streamlit Secrets."
        )


        st.stop()


    return genai.Client(
        api_key=key
    )


# ============================================================
# TEMP AUDIO FUNCTIONS
# ============================================================

def save_audio_temp(
    audio_file
):

    original_name = getattr(
        audio_file,
        "name",
        None
    )


    if not original_name:

        original_name = (
            "voice_note.wav"
        )


    extension = os.path.splitext(
        original_name
    )[1]


    if not extension:

        extension = ".wav"


    temp_file = (
        tempfile
        .NamedTemporaryFile(
            delete=False,
            suffix=extension
        )
    )


    try:

        temp_file.write(
            audio_file.getvalue()
        )


        temp_file.flush()


    finally:

        temp_file.close()


    return (

        temp_file.name,

        original_name

    )


# ============================================================
# DELETE TEMP FILE
# ============================================================

def remove_temp_file(
    path
):

    if not path:

        return


    try:

        if os.path.exists(
            path
        ):

            os.remove(
                path
            )

    except Exception:

        pass


# ============================================================
# AUDIO TRANSCRIPTION
# ============================================================

def transcribe_audio(

    gemini_client,

    audio_file,

    language

):


    temp_path = None

    uploaded_audio = None


    try:


        temp_path, original_name = (
            save_audio_temp(
                audio_file
            )
        )


        # -----------------------------
        # Upload audio to Gemini
        # -----------------------------

        uploaded_audio = (
            gemini_client
            .files
            .upload(
                file=temp_path
            )
        )


        # -----------------------------
        # Language
        # -----------------------------

        if language == "Auto Detect":

            language_instruction = (
                "Automatically detect "
                "the spoken language."
            )

        else:

            language_instruction = (

                "The expected spoken "
                f"language is {language}."

            )


        transcription_prompt = f"""

You are a professional
speech-to-text assistant.

Transcribe the attached
audio accurately.

Instructions:

- {language_instruction}

- Preserve names.

- Preserve dates.

- Preserve times.

- Preserve numbers.

- Preserve important
  task details.

- Do not summarize.

- Do not add commentary.

- Do not invent information.

- Use readable punctuation.

Return ONLY the transcript.

"""


        response = (
            gemini_client
            .models
            .generate_content(

                model=GEMINI_MODEL,

                contents=[

                    transcription_prompt,

                    uploaded_audio

                ]

            )
        )


        transcript = (

            response.text

            or ""

        ).strip()


        if not transcript:

            raise ValueError(

                "Gemini returned "
                "an empty transcript."

            )


        return (

            transcript,

            uploaded_audio,

            original_name

        )


    finally:

        remove_temp_file(
            temp_path
        )


# ============================================================
# CLEAN JSON RESPONSE
# ============================================================

def clean_json(
    text
):


    if not text:

        return "{}"


    text = text.strip()


    text = text.replace(
        "```json",
        ""
    )


    text = text.replace(
        "```JSON",
        ""
    )


    text = text.replace(
        "```",
        ""
    )


    text = text.strip()


    start = text.find(
        "{"
    )


    end = text.rfind(
        "}"
    )


    if (
        start >= 0
        and
        end >= 0
    ):

        text = text[
            start:
            end + 1
        ]


    return text


# ============================================================
# SAFE JSON PARSER
# ============================================================

def parse_json(
    text
):


    try:

        return json.loads(
            clean_json(
                text
            )
        )


    except Exception:


        return {

            "title":
                "Voice Note Analysis",

            "summary":
                text or
                "No summary generated.",

            "key_points":
                [],

            "action_items":
                [],

            "deadlines":
                [],

            "people":
                [],

            "decisions":
                [],

            "overall_priority":
                "Medium",

            "sentiment":
                "Neutral"

        }


# ============================================================
# AI ANALYSIS
# ============================================================

def analyze_transcript(

    gemini_client,

    transcript

):


    prompt = f"""

You are VoiceNotes AI.

You are an expert productivity
assistant.

Analyze the voice note transcript.

TRANSCRIPT:

{transcript}


Return ONLY valid JSON.

Use this exact structure:


{{
    "title":
        "Short descriptive title",

    "summary":
        "Short professional summary",

    "key_points":
        [
            "Important point"
        ],

    "action_items":
        [
            {{
                "task":
                    "Specific task",

                "owner":
                    "Person or Unassigned",

                "priority":
                    "High, Medium, or Low",

                "deadline":
                    "Deadline or Not specified",

                "status":
                    "To Do"
            }}
        ],

    "deadlines":
        [
            {{
                "label":
                    "What deadline is for",

                "when":
                    "Date/time exactly mentioned"
            }}
        ],

    "people":
        [
            "Person name"
        ],

    "decisions":
        [
            "Decision"
        ],

    "overall_priority":
        "High, Medium, or Low",

    "sentiment":
        "Positive, Neutral, Mixed, or Urgent"
}}


Rules:

1. Use only information
   from the transcript.

2. Do not invent people.

3. Do not invent deadlines.

4. Do not invent tasks.

5. Convert actionable
   instructions into tasks.

6. If no owner exists,
   use Unassigned.

7. If no deadline exists,
   use Not specified.

8. Return JSON only.

"""


    response = (
        gemini_client
        .models
        .generate_content(

            model=GEMINI_MODEL,

            contents=prompt,

            config={

                "response_mime_type":
                    "application/json"

            }

        )
    )


    return parse_json(

        response.text

        or ""

    )


# ============================================================
# ASK MY NOTE FEATURE
# ============================================================

def ask_note(

    gemini_client,

    transcript,

    question

):


    prompt = f"""

Answer the user's question
ONLY using the transcript.

TRANSCRIPT:

{transcript}


QUESTION:

{question}


Rules:

- Do not invent information.

- If information is missing,
  say:

  "That information was not
   mentioned in the voice note."

- Keep the answer concise.

"""


    response = (
        gemini_client
        .models
        .generate_content(

            model=GEMINI_MODEL,

            contents=prompt

        )
    )


    return (

        response.text

        or ""

    ).strip()


# ============================================================
# TEXT REPORT
# ============================================================

def create_text_report(

    transcript,

    analysis,

    audio_name

):


    lines = []


    lines.append(
        "VOICENOTES AI REPORT"
    )


    lines.append(
        "=" * 60
    )


    lines.append(
        f"Audio: {audio_name}"
    )


    lines.append(

        "Generated: "

        + datetime.now().strftime(

            "%d %b %Y, "
            "%I:%M %p"

        )

    )


    lines.append(
        ""
    )


    lines.append(
        "TITLE"
    )


    lines.append(
        "-" * 60
    )


    lines.append(

        analysis.get(

            "title",

            "Voice Note Analysis"

        )

    )


    lines.append(
        ""
    )


    lines.append(
        "SUMMARY"
    )


    lines.append(
        "-" * 60
    )


    lines.append(

        analysis.get(

            "summary",

            ""

        )

    )


    lines.append(
        ""
    )


    lines.append(
        "KEY POINTS"
    )


    lines.append(
        "-" * 60
    )


    for point in analysis.get(

        "key_points",

        []

    ):


        lines.append(

            f"- {point}"

        )


    lines.append(
        ""
    )


    lines.append(
        "ACTION ITEMS"
    )


    lines.append(
        "-" * 60
    )


    actions = analysis.get(

        "action_items",

        []

    )


    for index, item in enumerate(

        actions,

        start=1

    ):


        lines.append(

            f"{index}. "
            f"{item.get('task', 'Task')}"

        )


        lines.append(

            "   Owner: "
            f"{item.get('owner', 'Unassigned')}"

        )


        lines.append(

            "   Priority: "
            f"{item.get('priority', 'Medium')}"

        )


        lines.append(

            "   Deadline: "
            f"{item.get('deadline', 'Not specified')}"

        )


    lines.append(
        ""
    )


    lines.append(
        "TRANSCRIPT"
    )


    lines.append(
        "-" * 60
    )


    lines.append(
        transcript
    )


    return "\n".join(
        lines
    )


# ============================================================
# JSON REPORT
# ============================================================

def create_json_report(

    transcript,

    analysis,

    audio_name

):


    data = {

        "audio_name":
            audio_name,

        "generated_at":
            datetime.now().isoformat(),

        "transcript":
            transcript,

        "analysis":
            analysis

    }


    return json.dumps(

        data,

        indent=2,

        ensure_ascii=False

    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:


    st.markdown(

        "## 🎙️ VoiceNotes AI"

    )


    st.caption(

        APP_TAGLINE

    )


    st.divider()


    if get_api_key():


        st.success(

            "Gemini API connected"

        )


    else:


        st.warning(

            "Gemini API key missing"

        )


    st.markdown(

        "### ⚙️ Features"

    )


    st.write(
        "🎧 Speech-to-Text"
    )


    st.write(
        "✨ AI Summaries"
    )


    st.write(
        "✅ Action Items"
    )


    st.write(
        "📅 Deadlines"
    )


    st.write(
        "👥 People Detection"
    )


    st.write(
        "⚡ Priority Analysis"
    )


    st.write(
        "💬 Ask My Note"
    )


    st.divider()


    st.metric(

        "Notes Processed",

        len(
            st.session_state.history
        )

    )


    if st.button(

        "🗑️ Clear History",

        use_container_width=True

    ):


        st.session_state.history = []


        st.session_state.transcript = ""


        st.session_state.analysis = None


        st.session_state.audio_name = ""


        st.session_state.ask_answer = ""


        st.rerun()


    st.divider()


    st.caption(

        "Keep GEMINI_API_KEY "
        "inside Streamlit Secrets."

    )


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """

<div class="hero">

    <div class="pill">

        ✨ AI Productivity Assistant

    </div>


    <h1>

        Voice Notes →<br>

        Action Items

    </h1>


    <p>

        Record or upload your voice note
        and instantly transform it into an
        accurate transcript, intelligent
        summary, structured tasks,
        priorities and deadlines.

    </p>

</div>

""",

    unsafe_allow_html=True
)


# ============================================================
# TOP METRICS
# ============================================================

metric1, metric2, metric3, metric4 = (

    st.columns(
        4
    )

)


metric1.metric(

    "AI Engine",

    "Gemini"

)


metric2.metric(

    "Input",

    "Voice / Audio"

)


metric3.metric(

    "Output",

    "Tasks + Summary"

)


metric4.metric(

    "History",

    len(
        st.session_state.history
    )

)


# ============================================================
# MAIN TABS
# ============================================================

process_tab, history_tab, about_tab = (

    st.tabs(
        [

            "🎙️ Process Voice Note",

            "📚 History",

            "ℹ️ About"

        ]
    )

)


# ============================================================
# PROCESS TAB
# ============================================================

with process_tab:


    st.markdown(

        "## 🎤 Add Your Voice Note"

    )


    st.caption(

        "Upload audio or record "
        "directly from your device."

    )


    left, right = st.columns(

        [
            1.15,
            0.85
        ],

        gap="large"

    )


    audio_file = None


    # --------------------------------------------------------
    # LEFT COLUMN
    # --------------------------------------------------------

    with left:


        st.markdown(

            '<div class="card">',

            unsafe_allow_html=True

        )


        input_method = st.radio(

            "Input Method",

            [

                "📁 Upload Audio",

                "🎤 Record Audio"

            ],

            horizontal=True

        )


        if input_method == "📁 Upload Audio":


            audio_file = st.file_uploader(

                "Upload Audio File",

                type=[

                    "mp3",

                    "wav",

                    "m4a",

                    "ogg",

                    "webm",

                    "mp4",

                    "mpeg",

                    "aac",

                    "flac"

                ]

            )


        else:


            audio_file = st.audio_input(

                "Record Your Voice Note"

            )


        language = st.selectbox(

            "Expected Language",

            [

                "Auto Detect",

                "English",

                "Hindi",

                "Marathi",

                "Telugu",

                "Tamil",

                "Kannada",

                "Bengali",

                "Gujarati"

            ]

        )


        if audio_file is not None:


            st.audio(
                audio_file
            )


            audio_size = (

                len(
                    audio_file.getvalue()
                )

                /

                (
                    1024
                    *
                    1024
                )

            )


            st.caption(

                f"Audio ready • "
                f"{audio_size:.2f} MB"

            )


        st.markdown(

            "</div>",

            unsafe_allow_html=True

        )


    # --------------------------------------------------------
    # RIGHT COLUMN
    # --------------------------------------------------------

    with right:


        st.markdown(
            """

<div class="card">

    <h3>

        🤖 How It Works

    </h3>


    <p>

        <b>1️⃣ Listen</b><br>

        Gemini understands your audio.

    </p>


    <p>

        <b>2️⃣ Organize</b><br>

        AI finds tasks, people
        and deadlines.

    </p>


    <p>

        <b>3️⃣ Act</b><br>

        You receive a clean
        productivity dashboard.

    </p>

</div>

""",

            unsafe_allow_html=True
        )


    # --------------------------------------------------------
    # PROCESS BUTTON
    # --------------------------------------------------------

    process_button = st.button(

        "✨ Process Voice Note with Gemini",

        type="primary",

        use_container_width=True,

        disabled=(
            audio_file is None
        )

    )


    # ========================================================
    # PROCESS AUDIO
    # ========================================================

    if (
        process_button
        and
        audio_file is not None
    ):


        uploaded_gemini_file = None

        gemini_client = None


        try:


            gemini_client = (
                get_client()
            )


            progress = st.progress(

                5,

                text="Preparing audio..."

            )


            progress.progress(

                25,

                text=(
                    "🎧 Transcribing audio "
                    "with Gemini..."
                )

            )


            transcript, uploaded_gemini_file, audio_name = (

                transcribe_audio(

                    gemini_client,

                    audio_file,

                    language

                )

            )


            progress.progress(

                60,

                text=(
                    "🤖 Extracting tasks "
                    "and deadlines..."
                )

            )


            analysis = (

                analyze_transcript(

                    gemini_client,

                    transcript

                )

            )


            progress.progress(

                90,

                text=(
                    "📊 Building "
                    "your dashboard..."
                )

            )


            st.session_state.transcript = (

                transcript

            )


            st.session_state.analysis = (

                analysis

            )


            st.session_state.audio_name = (

                audio_name

            )


            st.session_state.ask_answer = ""


            history_item = {

                "created_at":

                    datetime.now().strftime(

                        "%d %b %Y, "
                        "%I:%M %p"

                    ),

                "audio_name":

                    audio_name,

                "transcript":

                    transcript,

                "analysis":

                    analysis

            }


            st.session_state.history.insert(

                0,

                history_item

            )


            progress.progress(

                100,

                text="Completed!"

            )


            st.success(

                "🎉 Voice note processed successfully."

            )


        except Exception as error:


            error_message = str(
                error
            )


            if (

                "429"
                in error_message

                or

                "quota"
                in error_message.lower()

            ):


                st.error(

                    "Gemini API quota or "
                    "rate limit reached. "
                    "Please try again later."

                )


            elif (

                "api key"
                in error_message.lower()

                or

                "api_key"
                in error_message.lower()

            ):


                st.error(

                    "Gemini API authentication failed. "
                    "Check GEMINI_API_KEY "
                    "inside Streamlit Secrets."

                )


            else:


                st.error(

                    f"Processing error: "
                    f"{error_message}"

                )


        finally:


            if (

                uploaded_gemini_file
                is not None

                and

                gemini_client
                is not None

            ):


                try:


                    gemini_client.files.delete(

                        name=(
                            uploaded_gemini_file.name
                        )

                    )


                except Exception:

                    pass


    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    if (

        st.session_state.transcript

        and

        st.session_state.analysis

    ):


        transcript = (

            st.session_state.transcript

        )


        analysis = (

            st.session_state.analysis

        )


        audio_name = (

            st.session_state.audio_name

        )


        st.divider()


        st.markdown(

            "## 📊 AI Analysis Dashboard"

        )


        action_items = analysis.get(

            "action_items",

            []

        )


        deadlines = analysis.get(

            "deadlines",

            []

        )


        people = analysis.get(

            "people",

            []

        )


        # ----------------------------------------------------
        # RESULT METRICS
        # ----------------------------------------------------

        result1, result2, result3, result4 = (

            st.columns(
                4
            )

        )


        result1.metric(

            "✅ Action Items",

            len(
                action_items
            )

        )


        result2.metric(

            "📅 Deadlines",

            len(
                deadlines
            )

        )


        result3.metric(

            "👥 People",

            len(
                people
            )

        )


        result4.metric(

            "⚡ Priority",

            analysis.get(

                "overall_priority",

                "Medium"

            )

        )


        # ----------------------------------------------------
        # RESULT TABS
        # ----------------------------------------------------

        result_tabs = st.tabs(

            [

                "✨ Summary",

                "✅ Tasks",

                "📅 Details",

                "📝 Transcript",

                "💬 Ask My Note"

            ]

        )


        # ====================================================
        # SUMMARY TAB
        # ====================================================

        with result_tabs[0]:


            st.markdown(

                "### "
                + analysis.get(

                    "title",

                    "Voice Note Analysis"

                )

            )


            st.info(

                analysis.get(

                    "summary",

                    "No summary available."

                )

            )


            st.markdown(

                "### 🔑 Key Points"

            )


            key_points = analysis.get(

                "key_points",

                []

            )


            if key_points:


                for point in key_points:


                    st.markdown(

                        f"- {point}"

                    )


            else:


                st.caption(

                    "No key points identified."

                )


            decisions = analysis.get(

                "decisions",

                []

            )


            if decisions:


                st.markdown(

                    "### 🤝 Decisions"

                )


                for decision in decisions:


                    st.markdown(

                        f"- {decision}"

                    )


            st.caption(

                "Tone detected: "
                + analysis.get(

                    "sentiment",

                    "Neutral"

                )

            )


        # ====================================================
        # TASKS TAB
        # ====================================================

        with result_tabs[1]:


            st.markdown(

                "### ✅ Action Items"

            )


            if action_items:


                for index, item in enumerate(

                    action_items,

                    start=1

                ):


                    task = item.get(

                        "task",

                        "Task"

                    )


                    owner = item.get(

                        "owner",

                        "Unassigned"

                    )


                    priority = item.get(

                        "priority",

                        "Medium"

                    )


                    deadline = item.get(

                        "deadline",

                        "Not specified"

                    )


                    status = item.get(

                        "status",

                        "To Do"

                    )


                    st.markdown(
                        f"""

<div class="task-card">

    <b>

        {index}. {task}

    </b>

    <br><br>

    👤 <b>Owner:</b>
    {owner}

    <br>

    ⚡ <b>Priority:</b>
    {priority}

    <br>

    📅 <b>Deadline:</b>
    {deadline}

    <br>

    📌 <b>Status:</b>
    {status}

</div>

""",

                        unsafe_allow_html=True
                    )


            else:


                st.info(

                    "No actionable tasks found."

                )


        # ====================================================
        # DETAILS TAB
        # ====================================================

        with result_tabs[2]:


            detail_left, detail_right = (

                st.columns(
                    2
                )

            )


            with detail_left:


                st.markdown(

                    "### 📅 Deadlines"

                )


                if deadlines:


                    for deadline_item in deadlines:


                        if isinstance(

                            deadline_item,

                            dict

                        ):


                            label = deadline_item.get(

                                "label",

                                "Deadline"

                            )


                            when = deadline_item.get(

                                "when",

                                "Not specified"

                            )


                            st.markdown(
                                f"""

<div class="deadline-card">

    <b>

        {label}

    </b>

    <br>

    📆 {when}

</div>

""",

                                unsafe_allow_html=True
                            )


                        else:


                            st.markdown(

                                f"- 📆 {deadline_item}"

                            )


                else:


                    st.info(

                        "No deadlines mentioned."

                    )


            with detail_right:


                st.markdown(

                    "### 👥 People Mentioned"

                )


                if people:


                    for person in people:


                        st.markdown(

                            f"- 👤 {person}"

                        )


                else:


                    st.info(

                        "No people mentioned."

                    )


        # ====================================================
        # TRANSCRIPT TAB
        # ====================================================

        with result_tabs[3]:


            st.markdown(

                "### 📝 Complete Transcript"

            )


            st.text_area(

                "Transcript",

                value=transcript,

                height=330,

                key="transcript_output"

            )


        # ====================================================
        # ASK MY NOTE TAB
        # ====================================================

        with result_tabs[4]:


            st.markdown(

                "### 💬 Ask My Note"

            )


            st.caption(

                "Ask questions about "
                "your voice note."

            )


            question = st.text_input(

                "Your Question",

                placeholder=(
                    "What are my most "
                    "urgent tasks?"
                )

            )


            ask_button = st.button(

                "Ask Gemini",

                use_container_width=True

            )


            if (
                ask_button
                and
                question.strip()
            ):


                try:


                    gemini_client = (

                        get_client()

                    )


                    with st.spinner(

                        "Searching the voice note..."

                    ):


                        answer = ask_note(

                            gemini_client,

                            transcript,

                            question

                        )


                    st.session_state.ask_answer = (

                        answer

                    )


                except Exception as error:


                    st.error(

                        f"Question error: "
                        f"{error}"

                    )


            if st.session_state.ask_answer:


                st.success(

                    st.session_state.ask_answer

                )


        # ====================================================
        # DOWNLOAD RESULTS
        # ====================================================

        st.divider()


        st.markdown(

            "### 📥 Export Results"

        )


        download_left, download_right = (

            st.columns(
                2
            )

        )


        with download_left:


            st.download_button(

                "⬇️ Download TXT Report",

                data=create_text_report(

                    transcript,

                    analysis,

                    audio_name

                ),

                file_name=(
                    "voice_notes_ai_report.txt"
                ),

                mime="text/plain",

                use_container_width=True

            )


        with download_right:


            st.download_button(

                "⬇️ Download JSON Data",

                data=create_json_report(

                    transcript,

                    analysis,

                    audio_name

                ),

                file_name=(
                    "voice_notes_ai_report.json"
                ),

                mime="application/json",

                use_container_width=True

            )


# ============================================================
# HISTORY TAB
# ============================================================

with history_tab:


    st.markdown(

        "## 📚 Processing History"

    )


    st.caption(

        "History stays for the "
        "current Streamlit session."

    )


    if not st.session_state.history:


        st.info(

            "No voice notes processed yet."

        )


    else:


        for index, item in enumerate(

            st.session_state.history,

            start=1

        ):


            history_analysis = item.get(

                "analysis",

                {}

            )


            history_title = (

                history_analysis.get(

                    "title",

                    f"Voice Note {index}"

                )

            )


            with st.expander(

                "🎙️ "
                + history_title
                + " • "
                + item.get(
                    "created_at",
                    ""
                )

            ):


                st.caption(

                    "Source: "
                    + item.get(

                        "audio_name",

                        "Audio"

                    )

                )


                st.markdown(

                    "#### Summary"

                )


                st.write(

                    history_analysis.get(

                        "summary",

                        ""

                    )

                )


                history_actions = (

                    history_analysis.get(

                        "action_items",

                        []

                    )

                )


                st.markdown(

                    "#### Action Items "
                    f"({len(history_actions)})"

                )


                if history_actions:


                    for action in history_actions:


                        st.markdown(

                            "- **"
                            + action.get(
                                "task",
                                "Task"
                            )
                            + "** — "
                            + action.get(
                                "priority",
                                "Medium"
                            )
                            + " priority"

                        )


                else:


                    st.caption(

                        "No action items."

                    )


                with st.expander(

                    "View Transcript"

                ):


                    st.write(

                        item.get(

                            "transcript",

                            ""

                        )

                    )


# ============================================================
# ABOUT TAB
# ============================================================

with about_tab:


    st.markdown(

        "## ℹ️ About VoiceNotes AI"

    )


    st.write(

        "VoiceNotes AI converts spoken "
        "notes into structured productivity "
        "information for students, teams, "
        "meetings and everyday planning."

    )


    feature1, feature2, feature3 = (

        st.columns(
            3
        )

    )


    with feature1:


        st.markdown(
            """

<div class="card">

    <h3>

        🎧 Understand

    </h3>

    <p>

        Gemini turns your voice
        into an accurate transcript.

    </p>

</div>

""",

            unsafe_allow_html=True
        )


    with feature2:


        st.markdown(
            """

<div class="card">

    <h3>

        ✨ Organize

    </h3>

    <p>

        AI extracts summaries,
        people, decisions
        and deadlines.

    </p>

</div>

""",

            unsafe_allow_html=True
        )


    with feature3:


        st.markdown(
            """

<div class="card">

    <h3>

        ✅ Act

    </h3>

    <p>

        Action items contain
        priorities, owners
        and deadlines.

    </p>

</div>

""",

            unsafe_allow_html=True
        )


    st.divider()


    st.markdown(

        "### 🔐 Gemini API Security"

    )


    st.write(

        "Keep your Gemini API key "
        "inside Streamlit Cloud Secrets."

    )


    st.code(

        'GEMINI_API_KEY = "your_key_here"',

        language="toml"

    )


    st.warning(

        "Never paste your real "
        "Gemini API key inside app.py "
        "or your GitHub repository."

    )


    st.markdown(

        "### 🧰 Technology Stack"

    )


    st.write(

        "Python • Streamlit • "
        "Google Gemini API • "
        "google-genai"

    )


# ============================================================
# FOOTER
# ============================================================

st.divider()


footer_left, footer_right = (

    st.columns(
        2
    )

)


with footer_left:


    st.caption(

        "🎙️ VoiceNotes AI • "
        "Voice → Transcript → Action"

    )


with footer_right:


    st.caption(

        "Powered by Google Gemini • "
        + GEMINI_MODEL

    )

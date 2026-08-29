import streamlit as st
from groq import Groq
import os
import tempfile
from datetime import datetime


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="Voice Notes AI",
    page_icon="🎙️",
    layout="wide"
)


# -------------------------------------------------
# GET GROQ API KEY
# -------------------------------------------------

def get_api_key():
    try:
        return st.secrets["GROQ_API_KEY"]
    except Exception:
        return os.getenv("GROQ_API_KEY")


api_key = get_api_key()


# -------------------------------------------------
# APP HEADER
# -------------------------------------------------

st.title("🎙️ Voice Notes AI")
st.subheader("AI-powered Speech-to-Text, Summaries & Action Items")

st.write(
    "Upload a voice note and let AI automatically convert it into text, "
    "generate a summary, and identify important tasks and action items."
)

st.divider()


# -------------------------------------------------
# CHECK API KEY
# -------------------------------------------------

if not api_key:
    st.error("Groq API key not found.")

    st.info("""
Add your API key in Streamlit Secrets using exactly:

GROQ_API_KEY = "your_groq_api_key_here"
""")

    st.stop()


# -------------------------------------------------
# CREATE GROQ CLIENT
# -------------------------------------------------

try:
    client = Groq(api_key=api_key)
except Exception as e:
    st.error(f"Unable to initialize Groq client: {e}")
    st.stop()


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []


# -------------------------------------------------
# TABS
# -------------------------------------------------

tab1, tab2 = st.tabs([
    "🎙️ Process Voice Note",
    "📚 History"
])


# =================================================
# PROCESS VOICE NOTE TAB
# =================================================

with tab1:

    st.header("🎤 Add Your Voice Note")

    st.write(
        "Upload an audio file and Voice Notes AI will transcribe "
        "and analyze it automatically."
    )

    uploaded_file = st.file_uploader(
        "Upload Audio File",
        type=[
            "mp3",
            "wav",
            "m4a",
            "ogg",
            "webm",
            "mp4",
            "mpeg",
            "mpga"
        ]
    )

    if uploaded_file is not None:

        st.success(f"Audio uploaded: {uploaded_file.name}")

        st.audio(uploaded_file)

        process_button = st.button(
            "✨ Process Voice Note",
            use_container_width=True
        )

        if process_button:

            temp_path = None

            try:

                # -----------------------------------------
                # SAVE TEMPORARY AUDIO FILE
                # -----------------------------------------

                suffix = os.path.splitext(uploaded_file.name)[1]

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_file:

                    temp_file.write(uploaded_file.getvalue())
                    temp_path = temp_file.name


                # -----------------------------------------
                # SPEECH RECOGNITION
                # -----------------------------------------

                with st.spinner("🎧 Converting speech to text..."):

                    with open(temp_path, "rb") as audio_file:

                        transcription = (
                            client.audio.transcriptions.create(
                                file=(
                                    uploaded_file.name,
                                    audio_file.read()
                                ),
                                model="whisper-large-v3-turbo",
                                response_format="json"
                            )
                        )

                    transcript = transcription.text


                st.success("Speech converted successfully!")


                # -----------------------------------------
                # DISPLAY TRANSCRIPT
                # -----------------------------------------

                st.divider()

                st.header("📝 Speech Recognition")

                st.text_area(
                    "Transcript",
                    value=transcript,
                    height=250
                )


                # -----------------------------------------
                # AI ANALYSIS
                # -----------------------------------------

                with st.spinner(
                    "🤖 AI is analyzing your voice note..."
                ):

                    prompt = f"""
You are an intelligent assistant that analyzes voice notes.

Analyze the following transcript carefully.

TRANSCRIPT:
{transcript}

Return the answer using exactly these sections:

## 📌 Summary
Write a clear and concise summary.

## 🎯 Key Points
List the most important points using bullet points.

## ✅ Action Items
Extract all tasks or actions.

For every action item include:
- Task
- Priority: High, Medium, or Low
- Owner if mentioned
- Deadline if mentioned

If information is not mentioned, write "Not specified".

Do not invent information that is not present in the transcript.
"""


                    completion = (
                        client.chat.completions.create(
                            model="llama-3.3-70b-versatile",
                            messages=[
                                {
                                    "role": "system",
                                    "content": (
                                        "You are an expert assistant "
                                        "for analyzing meeting notes "
                                        "and voice transcripts."
                                    )
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            temperature=0.3,
                            max_tokens=2000
                        )
                    )

                    analysis = (
                        completion
                        .choices[0]
                        .message
                        .content
                    )


                # -----------------------------------------
                # DISPLAY ANALYSIS
                # -----------------------------------------

                st.divider()

                st.header("🤖 AI Understanding")

                st.markdown(analysis)


                # -----------------------------------------
                # SAVE HISTORY
                # -----------------------------------------

                st.session_state.history.insert(
                    0,
                    {
                        "filename": uploaded_file.name,
                        "date": datetime.now().strftime(
                            "%d %B %Y, %I:%M %p"
                        ),
                        "transcript": transcript,
                        "analysis": analysis
                    }
                )


                # -----------------------------------------
                # DOWNLOAD RESULTS
                # -----------------------------------------

                st.divider()

                st.header("📥 Download Results")

                result_text = f"""
VOICE NOTES AI REPORT

File: {uploaded_file.name}

========================
TRANSCRIPT
========================

{transcript}

========================
AI ANALYSIS
========================

{analysis}
"""


                st.download_button(
                    label="⬇️ Download Report",
                    data=result_text,
                    file_name="voice_notes_ai_report.txt",
                    mime="text/plain",
                    use_container_width=True
                )


            except Exception as e:

                st.error("Processing error occurred.")

                st.exception(e)


            finally:

                if temp_path is not None:

                    try:
                        os.remove(temp_path)

                    except Exception:
                        pass


# =================================================
# HISTORY TAB
# =================================================

with tab2:

    st.header("📚 Processing History")

    if len(st.session_state.history) == 0:

        st.info(
            "No voice notes processed yet. "
            "Upload an audio file in the Process Voice Note tab."
        )

    else:

        for index, item in enumerate(
            st.session_state.history
        ):

            with st.expander(
                f"🎙️ {item['filename']} — {item['date']}"
            ):

                st.subheader("📝 Transcript")

                st.write(item["transcript"])

                st.subheader("🤖 AI Analysis")

                st.markdown(item["analysis"])


# -------------------------------------------------
# FOOTER
# -------------------------------------------------

st.divider()

st.caption(
    "🎙️ Voice Notes AI • AI-powered Speech-to-Text, "
    "Summaries & Action Item Extraction"
)

import streamlit as st
from openai import OpenAI
import os
import json

# Page configuration
st.set_page_config(
    page_title="Voice Notes → Action Items",
    page_icon="🎙️",
    layout="wide"
)

# -----------------------------
# PAGE HEADER
# -----------------------------

st.title("🎙️ Voice Notes → Action Items")
st.subheader(
    "Turn your voice notes into summaries, tasks, and deadlines using AI"
)

st.divider()

# -----------------------------
# API KEY
# -----------------------------

api_key = os.getenv("OPENAI_API_KEY")

# -----------------------------
# AUDIO INPUT
# -----------------------------

st.header("🎤 Upload or Record Your Voice Note")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "wav", "m4a", "ogg"]
)

audio_value = st.audio_input(
    "Or record a voice note"
)

audio_file = uploaded_file if uploaded_file else audio_value


# -----------------------------
# AUDIO PROCESSING
# -----------------------------

if audio_file:

    st.audio(audio_file)

    if st.button(
        "✨ Process Voice Note",
        use_container_width=True
    ):

        if not api_key:

            st.error(
                "OpenAI API key not found. "
                "Configure OPENAI_API_KEY in your deployment secrets."
            )

        else:

            try:

                client = OpenAI(
                    api_key=api_key
                )

                # -----------------------------
                # SPEECH TO TEXT
                # -----------------------------

                with st.spinner(
                    "🗣️ Converting speech to text..."
                ):

                    transcription = (
                        client.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file
                        )
                    )

                transcript = transcription.text

                st.success(
                    "Voice note processed successfully!"
                )

                # -----------------------------
                # TRANSCRIPT
                # -----------------------------

                st.subheader(
                    "📝 Transcript"
                )

                st.info(
                    transcript
                )

                st.divider()

                # -----------------------------
                # AI ANALYSIS
                # -----------------------------

                with st.spinner(
                    "🤖 AI is analyzing your voice note..."
                ):

                    prompt = f"""
Analyze the following voice note transcript.

Return ONLY valid JSON.

Use exactly this structure:

{{
    "summary": "Short clear summary",

    "action_items": [
        {{
            "task": "Task description",
            "deadline": "Deadline if mentioned, otherwise Not specified",
            "priority": "High, Medium, or Low"
        }}
    ],

    "deadlines": [
        "List all deadlines or dates mentioned"
    ]
}}

Rules:

1. Create a short and useful summary.
2. Extract all actionable tasks.
3. Detect dates, deadlines, and time references.
4. Assign a reasonable priority to each task.
5. Do not include markdown.
6. Return only valid JSON.

Transcript:

{transcript}
"""

                    response = (
                        client.chat.completions.create(

                            model="gpt-4o-mini",

                            messages=[
                                {
                                    "role": "system",

                                    "content": (
                                        "You are an AI assistant that "
                                        "analyzes voice notes and extracts "
                                        "structured action items."
                                    )
                                },

                                {
                                    "role": "user",

                                    "content": prompt
                                }
                            ]
                        )
                    )

                result = (
                    response
                    .choices[0]
                    .message
                    .content
                )

                data = json.loads(
                    result
                )

                # -----------------------------
                # SUMMARY
                # -----------------------------

                st.subheader(
                    "✨ AI Summary"
                )

                st.success(
                    data.get(
                        "summary",
                        "No summary available."
                    )
                )

                # -----------------------------
                # ACTION ITEMS
                # -----------------------------

                st.subheader(
                    "✅ Action Items"
                )

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
                                f"### {index}. {item.get('task')}"
                            )

                            col1, col2 = st.columns(2)

                            with col1:

                                st.write(
                                    "📅 **Deadline:** "
                                    f"{item.get('deadline')}"
                                )

                            with col2:

                                st.write(
                                    "⚡ **Priority:** "
                                    f"{item.get('priority')}"
                                )

                else:

                    st.info(
                        "No action items detected."
                    )

                # -----------------------------
                # DEADLINES
                # -----------------------------

                st.subheader(
                    "📅 Important Dates & Deadlines"
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


            except json.JSONDecodeError:

                st.error(
                    "AI returned an unexpected format. "
                    "Please try again."
                )


            except Exception as e:

                st.error(
                    f"Error processing voice note: {str(e)}"
                )


# -----------------------------
# PROJECT FEATURES
# -----------------------------

st.divider()

col1, col2, col3 = st.columns(3)

with col1:

    st.subheader(
        "🗣️ Speech to Text"
    )

    st.write(
        "Convert voice notes into "
        "accurate transcripts."
    )


with col2:

    st.subheader(
        "✨ AI Summary"
    )

    st.write(
        "Understand long voice notes "
        "quickly with concise summaries."
    )


with col3:

    st.subheader(
        "✅ Action Items"
    )

    st.write(
        "Automatically extract tasks, "
        "priorities, and deadlines."
                                )

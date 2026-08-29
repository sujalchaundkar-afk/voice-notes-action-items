import streamlit as st
from openai import OpenAI
import os

# Page configuration
st.set_page_config(
    page_title="Voice Notes → Action Items",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Voice Notes → Action Items")
st.subheader("Turn your voice notes into summaries and actionable tasks using AI")

st.divider()

# API key check
api_key = os.getenv("OPENAI_API_KEY")

# Audio Input
st.header("🎤 Upload or Record Your Voice Note")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "wav", "m4a", "ogg"]
)

audio_value = st.audio_input("Or record a voice note")

# Select audio source
audio_file = uploaded_file if uploaded_file else audio_value

if audio_file:
    st.audio(audio_file)

    if st.button("✨ Process Voice Note", use_container_width=True):

        if not api_key:
            st.error(
                "OpenAI API key not found. Add OPENAI_API_KEY to your .env file."
            )

        else:
            try:
                client = OpenAI(api_key=api_key)

                with st.spinner("🗣️ Converting speech to text..."):

                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )

                transcript = transcription.text

                st.success("Speech converted successfully!")

                # Display transcript
                st.subheader("📝 Transcript")
                st.write(transcript)

                st.divider()

                # AI processing
                with st.spinner("🤖 AI is analyzing your voice note..."):

                    prompt = f"""
                    Analyze the following voice note transcript.

                    Provide:
                    1. A short and clear summary.
                    2. A list of action items.
                    3. Any deadlines or dates mentioned.

                    Transcript:
                    {transcript}
                    """

                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    "You extract useful information from voice notes "
                                    "and return clear, structured results."
                                )
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )

                result = response.choices[0].message.content

                st.subheader("🤖 AI Analysis")
                st.write(result)

            except Exception as e:
                st.error(f"Error processing audio: {str(e)}")

st.divider()

# Features section
col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("🗣️ Speech to Text")
    st.write("Convert your voice note into an accurate transcript.")

with col2:
    st.subheader("✨ AI Summary")
    st.write("Get a clear and concise summary of your voice note.")

with col3:
    st.subheader("✅ Action Items")
    st.write("Automatically extract important tasks and next steps.")

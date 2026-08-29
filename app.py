import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Voice Notes → Action Items",
    page_icon="🎙️",
    layout="wide"
)

# Title
st.title("🎙️ Voice Notes → Action Items")
st.subheader("Turn your voice notes into summaries and actionable tasks using AI")

st.divider()

# Upload section
st.header("🎤 Upload Your Voice Note")

uploaded_file = st.file_uploader(
    "Upload an audio file",
    type=["mp3", "wav", "m4a", "ogg"]
)

# Recording section
st.subheader("Or record your voice")

audio_value = st.audio_input("Record a voice note")

st.divider()

# Process button
if uploaded_file or audio_value:
    if st.button("✨ Process Voice Note", use_container_width=True):

        st.info("⏳ Audio processing will be added in the next step.")

        # Display uploaded/recorded audio
        if uploaded_file:
            st.audio(uploaded_file)

        elif audio_value:
            st.audio(audio_value)

# Information section
st.divider()

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

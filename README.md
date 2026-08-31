# 🎙️ Voice Notes → Action Items

An AI-powered application that converts voice notes into accurate transcripts, summaries, actionable tasks, and important deadlines using the **Google Gemini API** and **Streamlit**.

---

## ✨ Features

- 🗣️ **Multimodal Speech-to-Text**: Direct audio input processing using Gemini multimodal capabilities.
- 📝 **Verbatim Transcripts**: Generates full transcriptions of recorded or uploaded audio.
- ⚡ **AI Summaries**: Concise and structured summary generation.
- ✅ **Action Item Extraction**: Automatic extraction of actionable tasks with priorities (High, Medium, Low).
- 📅 **Deadline & Mention Detection**: Identifies target dates and key individuals mentioned in the recording.
- 📚 **Session History**: Track, review, and expand past processed notes within the app interface.

---

## 🛠️ Tech Stack

- **Framework**: [Streamlit](https://streamlit.io/)
- **AI Model**: [Google GenAI SDK](https://pypi.org/project/google-genai/) (`gemini-3.6-flash`)
- **Language**: Python 3.9+

---

## 🚀 Run locally 

### 1. Prerequisites

Make sure you have Python 3.9 or higher installed. You will also need a **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/).

### 2. Clone the Repository

```bash
git clone https://github.com/sujalchaundkar-afk/voice-notes-action-items
cd voice-notes-action-items
### 3.pip install -r requirements.txt
---
### 4.GEMINI_API_KEY=your_gemini_api_key_here

### 5.streamlit run app.py

Open your browser at http://localhost:8501 to use the application.

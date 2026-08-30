# 🎙️ Voice Notes → Action Items

### AI-Powered Voice Productivity Assistant

Voice Notes → Action Items is an AI-powered application that transforms voice notes and unstructured text into clear, organized, and actionable information.

The application processes voice input, converts it into text, and uses AI to generate summaries, action items, priorities, deadlines, and responsibilities.

Built using **Python, Streamlit, and OpenAI API**.

---

## 🚀 What It Does

Voice Notes → Action Items helps users turn conversations, meetings, lectures, ideas, and voice notes into structured information.

### Input

- 🎤 Voice notes
- 📁 Audio files
- 📝 Text input

### AI Output

- 📝 Transcription
- ✨ Summary
- 📋 Action items
- 🎯 Task priorities
- 📅 Deadlines
- 👥 Responsibilities
- 💡 Important points

---

## ✨ Features

- 🎤 Voice note recording
- 📁 Audio file upload
- 📝 Speech-to-text conversion
- 🤖 AI-powered analysis
- ✨ Automatic summarization
- 📋 Action item extraction
- 🎯 Priority detection
- 📅 Deadline identification
- 👥 Responsibility detection
- 💬 Text input support
- 🎨 Modern and user-friendly interface
- 🔐 Secure API key configuration

---


## ⚙️ Run Locally

To run **Voice Notes → Action Items** locally, create a virtual environment, activate it, install the required dependencies, configure your OpenAI API key, and start the Streamlit application:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py




## 🧠 How It Works

```text
🎤 Voice Note / 📝 Text Input
            │
            ▼
     Speech-to-Text
      (Voice Input)
            │
            ▼
       Transcription
            │
            ▼
       OpenAI API
            │
            ▼
      AI Analysis
            │
            ▼
┌───────────────────────────┐
│ ✨ Summary                │
│ 📋 Action Items           │
│ 🎯 Priorities             │
│ 📅 Deadlines              │
│ 👥 Responsibilities       │
└───────────────────────────┘

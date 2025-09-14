# 🤖 Jarvis - Voice Assistant (with System Control)

Jarvis is a **voice-enabled assistant** built with **Streamlit**.  
It can perform **web searches, Wikipedia lookup, open websites, speak responses, and control your system** (shutdown, restart, sleep, lock, etc.) when run locally.

---

## ✨ Features
- 🎤 **Voice Commands** using SpeechRecognition  
- 🗣️ **Text-to-Speech (TTS)** with gTTS  
- 🔍 **Wikipedia Search**  
- 🌐 **Open Websites** (Google, YouTube, StackOverflow)  
- ⏰ **Tell Current Time**  
- ⚡ **System Control Commands** (only on local run):
  - Shutdown, Restart, Sleep, Lock, Logout
  - Battery status, CPU usage, RAM usage  

---

## 📂 Project Structure
📦 Jarvis-Voice-Assistant
┣ 📜 virtual-assistant.py # Main app
┣ 📜 requirements.txt # Dependencies
┗ 📜 README.md # Project description

yaml
Copy code

---

## ⚙️ Installation

1. Clone the repo
   ```bash
   git clone https://github.com/<your-username>/Jarvis-Voice-Assistant.git
   cd Jarvis-Voice-Assistant
Create a virtual environment (optional but recommended)

bash
Copy code
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
Install dependencies

bash
Copy code
pip install -r requirements.txt
🚀 Run Locally
bash
Copy code
streamlit run virtual-assistant.py
Then open the given http://localhost:8501 link in your browser.

🌐 Deployment
You can deploy on Streamlit Cloud / Render / Hugging Face Spaces,
but note:

🎤 Microphone-based voice recognition &

⚡ System control commands

👉 These will only work on your local machine, not on the cloud server.
On cloud deployment, manual input + Wikipedia + web browsing + TTS will work.

📌 Example Commands
"Open YouTube"

"Search Python in Wikipedia"

"What is the time"

"Shutdown my system"

"What's my battery status"

🛠️ Tech Stack
Streamlit – UI framework

SpeechRecognition – Voice input

gTTS – Text-to-speech

psutil – System monitoring

Wikipedia API – Information search


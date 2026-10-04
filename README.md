
# 📚 Snap & Study AI

Snap & Study AI is an AI-powered study assistant that helps students understand questions, notes, textbook pages, diagrams, and study material using text and image input.

## ✨ Features

- 💬 AI-powered study chat
- 📸 Upload notes, textbook pages, diagrams, or questions
- 🧠 AI explanation in simple language
- 🧮 Step-by-step problem solving
- 📝 Generate revision summaries
- 💡 Explain difficult concepts from basics
- 🗂️ Conversation memory during the session
- 📧 Send generated study summaries to email
- 🔐 Secure API credentials using Streamlit secrets

## 🛠️ Technology Stack

- Python
- Streamlit
- Google Gemini API
- Gemini Vision
- Gmail SMTP
- HTML/Markdown
- Python `smtplib`

## 📂 Project Structure

```text
snap-study-ai/
│
├── app.py
├── prompts.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── .streamlit/
│   ├── secrets.toml
│   └── secrets.toml.example
│
└── venv/


⚙️ Setup

1. Clone the repository
git clone 
cd snap-study-ai

2. Create a virtual environment
python -m venv venv

Activate it on Windows:

venv\Scripts\activate
3. Install dependencies
pip install -r requirements.txt
4. Configure API credentials

Create:

.streamlit/secrets.toml

Add:

GEMINI_API_KEY = "your_gemini_api_key"

GMAIL_SENDER_EMAIL = "your_gmail@gmail.com"

GMAIL_APP_PASSWORD = "your_gmail_app_password"

Never upload secrets.toml to GitHub.

5. Run the application
streamlit run app.py

The application will open in your browser.

🧠 How It Works
Student enters their name and email.
Student starts a study session.
Student can type a question or upload an image.
Gemini analyzes the question or image.
The AI provides a structured explanation or solution.
The conversation is maintained during the session.
Student can generate a revision summary.
The summary can be sent to the student's email.
🔐 Security

API keys and Gmail credentials are stored using Streamlit secrets.

The following file should never be committed:

.streamlit/secrets.toml
🚀 Future Improvements
PDF upload and analysis
Voice-based questions
Automatic quiz generation
Flashcard generation
Subject-wise study history
Personalized learning recommendations
Cloud deployment
Multi-language explanations
👩‍💻 Author

Ashwini Dound

Built as an AI-powered learning project using Python, Streamlit, and Gemini.
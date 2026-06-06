###MENTAL-HEALTH-CHATBOT
An AI-powered emotional wellness and journaling web app built with Streamlit and Google Gemini API.
This chatbot offers gentle, empathetic conversations to help students reflect on their emotions, track moods, and maintain a personal journal — all stored securely in the browser session.

🧠 Features
- AI Chatbot (Gemini 2.5 Flash)
Offers supportive and kind responses about feelings and studies.
Asks gentle follow-up questions to keep the conversation going.
Avoids medical or diagnostic advice to stay safe and ethical.

- Mood Tracker
Choose your current mood (Normal, Sad, Calm, Angry, etc.).
The bot tailors its tone accordingly.

- Personal Journal
Write daily reflections about your emotions or studies.
Entries are stored locally (not uploaded anywhere).
View past reflections in an expandable list.

- Safe & User-Friendly Design
Automatically softens sensitive words to prevent API safety blocking.
Handles blocked responses gracefully.
Adjustable creativity (temperature) and response length.

🧩 Tech Stack
Component	Description
Frontend	Streamlit
AI Model	Google Gemini 2.5 Flash
Language	Python 3.12.0
Storage	Streamlit Session State (in-browser)

IMORTANT NOTE - This app requires a Google Gemini API key to run. The key is not included in this repository for security reasons.

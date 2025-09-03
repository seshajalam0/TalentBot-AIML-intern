# 🤖 TalentScout – AI Hiring Assistant (Streamlit)

An intelligent chatbot for initial candidate screening. It collects essential details, generates **tech-stack-specific** technical questions, maintains conversational context, and stores anonymized sessions locally.

---

## ✨ Features
- Friendly greeting and clear purpose
- Collects: Full Name, Email, Phone, Years of Experience, Desired Position(s), Location, Tech Stack
- Generates **3–5** tailored technical questions for the declared stack
- Context-aware chat and polite fallbacks
- Conversation-ending keywords: **bye / exit / quit**
- Local storage with **masked PII**
- Works with **OpenAI** or **Mock (offline)** mode

---

## 🧱 Tech Stack
- Python 3.10+
- Streamlit (UI)
- OpenAI Chat Completions (LLM) – optional
- JSON file (simulated DB) for storage

---

## 🚀 Quickstart

### 1) Clone & install
```bash
pip install -r requirements.txt
```

### 2) Set API key (optional, for OpenAI mode)
```bash
export OPENAI_API_KEY=sk-...
```
Windows (Powershell):
```powershell
setx OPENAI_API_KEY "sk-..."
```
> If no key is provided, the app automatically uses **Mock (offline)** logic to generate reasonable questions.

### 3) Run
```bash
streamlit run app.py
```

---

## 🕹️ Usage
1. Fill your **Candidate Details** in the form.
2. Use the chat box to interact (e.g., *"Ready to start"*).
3. Click **Generate 3–5 Technical Questions** to see tailored questions for your stack.
4. Click **Save Interview to Local Store** to persist a masked copy in `storage/candidates.json`.
5. Type **bye** to end.

---

## 🔐 Data Privacy
- PII fields (**email, phone**) are **hashed** before saving.
- All data remains **local** to your machine (no external DB by default).
- Avoid uploading real personal data for demos.

---

## 🧠 Prompt Design
- **System prompt** ensures the bot keeps replies short, stays on purpose (hiring intake), and handles off-topic inputs gracefully.
- **Question prompt** requests practical, non-trivia questions focused on design decisions and trade-offs.
- **Fallback prompt** keeps the conversation on track with polite clarification requests.

See `prompts.py` for the exact templates.

---

## 🧩 Architecture
```
app.py          # Streamlit UI and chat loop
chatbot.py      # LLM client (OpenAI + Mock), routing, question generator
prompts.py      # Prompt templates
storage.py      # Local JSON storage with PII masking
.streamlit/
  config.toml   # Theme
storage/
  candidates.json (created at first save)
```

---

## 🧪 Example
Tech Stack: `Python, Django, PostgreSQL`  
Sample Questions:
- Explain how Django ORM translates queries to SQL with PostgreSQL.
- What are migrations and how do you manage schema changes safely?
- How would you structure settings and environments for a production Django app?
- When do indexes hurt performance in PostgreSQL?
- How do you write efficient queries and profile slow ones?

---

## ☁️ Deployment (Bonus)
- **Streamlit Community Cloud**: Push to GitHub → “New app” → select repo → deploy.
- **Docker** (optional):
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY . .
  RUN pip install -r requirements.txt
  EXPOSE 8501
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
  ```

---

## 📹 Demo
Record a quick walkthrough with **Loom** showing:
- Filling details
- Chatting
- Generating questions
- Saving the session

---

## 🧭 Evaluation Mapping
- **Functionality**: All required flows implemented, end keywords supported.
- **Technical**: Clear modular code, OpenAI + Mock paths, context retention.
- **Problem-Solving**: Targeted prompts; dictionary-backed fallback.
- **UX**: Clean Streamlit layout, helpful messaging, theme.
- **Docs**: This README outlines setup, design, and privacy.
- **Enhancements** (ideas): Sentiment analysis on answers, multilingual support, role-based question libraries, cloud DB with encryption.

---

## 📝 License
MIT

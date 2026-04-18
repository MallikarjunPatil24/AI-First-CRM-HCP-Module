# 🧠 AI-First CRM – HCP Interaction Module

A modern, AI-driven Customer Relationship Management (CRM) system designed for Life Sciences and Pharma field representatives. This application enables users to log and manage interactions with Healthcare Professionals (HCPs) using natural language, powered by **LangGraph + LLMs**, with **zero manual form entry**.

---

# About Project 

Traditional CRM systems require manual data entry, which is time-consuming and error-prone.

This project introduces an **AI-first approach**, where:

* Users interact via a **chat interface**
* AI extracts structured data
* The **form is auto-filled and controlled entirely by AI**

---

# 🎯 Key Features

* 🧠 AI-controlled form (no manual input)
* 💬 Natural language interaction logging
* 🔄 Real-time form updates using Redux
* 🛠️ LangGraph-based tool execution
* ⚡ Fast inference using Groq LLMs
* 🧾 Automated summaries and suggestions
* ✅ Pharma compliance validation

---

# 🖥️ Application UI

The application follows a **split-screen layout**:

* **Left Panel (Read-Only Form)**
  Displays structured interaction data.

* **Right Panel (AI Chat Assistant)**
  User interacts with the system using natural language.

---

# 🧱 Tech Stack

## Frontend

* React.js (Vite)
* Redux Toolkit
* CSS (Custom styling)
* Google Font: Inter

## Backend

* Python (FastAPI)

## AI Layer

* LangGraph (workflow orchestration)
* Groq LLMs:

  * `gemma2-9b-it` (primary)
  * `llama-3.3-70b-versatile` (fallback)

## Database

* PostgreSQL

---

# 🧠 System Architecture

```plaintext
User Input (Chat UI)
        ↓
React Frontend (Redux State)
        ↓
FastAPI Backend
        ↓
LangGraph Agent
        ↓
LLM (Groq)
        ↓
Tool Execution
        ↓
Structured JSON Output
        ↓
Redux Update
        ↓
UI Auto-Refresh
```

---

# 🧩 Core Concepts

## 🔹 AI-First Design

The application is built such that:

* The **AI controls all logic**
* The form acts only as a **display layer**
* Users cannot directly modify data fields

---

## 🔹 LangGraph

LangGraph is used to:

* Manage AI workflow
* Detect user intent
* Route tasks to appropriate tools

---

## 🔹 Tools (AI Actions)

The system implements **5 tools**:

### 1. Log Interaction Tool

Extracts structured data from user input.

### 2. Edit Interaction Tool

Updates specific fields without affecting others.

### 3. Smart Suggestion Tool

Provides next-step recommendations.

### 4. Compliance Checker Tool

Ensures pharma regulatory compliance.

### 5. Auto Summary Tool

Generates concise summaries of interactions.

---

# 📦 Project Structure

```plaintext
ai-crm-hcp/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── redux/
│   │   ├── pages/
│   │   └── App.jsx
│   └── index.html
│
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── langgraph/
│   ├── tools/
│   └── models/
│
├── database/
│   └── schema.sql
│
├── .env
└── README.md
```

---

# ⚙️ Installation & Setup

## 🔹 Prerequisites

* Node.js (v18+)
* Python (3.10+)
* PostgreSQL
* Groq API Key

---

## 🔹 Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create `.env`:

```env
GROQ_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/crm_db
```

Run server:

```bash
uvicorn main:app --reload
```

---

## 🔹 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

# 🗄️ Database Schema

```sql
CREATE TABLE interactions (
  id SERIAL PRIMARY KEY,
  hcp_name TEXT,
  date DATE,
  interaction_type TEXT,
  sentiment TEXT,
  products JSONB,
  materials JSONB,
  follow_up BOOLEAN,
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

# 🔌 API Endpoints

## POST `/chat`

### Request:

```json
{
  "message": "Met Dr. Rao today...",
  "current_form": {}
}
```

### Response:

```json
{
  "updated_form": {},
  "ai_message": "Interaction logged successfully"
}
```

---

# 🔄 Data Flow

1. User enters message in chat
2. Frontend sends request to backend
3. LangGraph processes input
4. LLM extracts meaning
5. Tool executes action
6. Backend returns structured data
7. Redux updates form
8. UI refreshes automatically

---

# 🧪 Example Interaction

### User Input:

```
Met Dr. Mehta today, discussed oncology drug, shared brochure
```

### Output (Auto-filled form):

* HCP Name: Dr. Mehta
* Product: Oncology Drug
* Material: Brochure
* Sentiment: Neutral

---

# 🚨 Important Constraints

* ❌ No manual form entry allowed
* ❌ No hardcoded extraction logic
* ✅ Must use LangGraph for workflow
* ✅ Must use LLM for processing

---

# 💡 What I Learned

* How to build AI-first systems where AI controls UI logic
* How to use LangGraph for structured workflows
* How LLMs can replace traditional rule-based systems
* Importance of modular tool-based architecture

---

# 🔮 Future Improvements

* Add voice input support
* Multi-language support
* Integration with real CRM systems
* Advanced analytics dashboard

---

# 🙌 Acknowledgements

* Groq for fast LLM inference
* LangGraph for agent orchestration
* React & FastAPI communities

---

# 📌 Conclusion

This project demonstrates how AI can transform traditional enterprise systems into intelligent, user-friendly platforms by removing manual effort and enabling natural interaction.

---

⭐ If you found this useful, consider giving it a star!

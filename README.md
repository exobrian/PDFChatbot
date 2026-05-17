# PDF Chatbot - Robust RAG Application
PDF Chatbot is a production-ready, full-stack Retrieval-Augmented Generation (RAG) web application. It allows authenticated users to upload PDF documents, extract their textual content asynchronously, and have contextualized conversations with an AI model based on the uploaded material. 

The application utilizes a decoupled frontend/backend architecture, password cryptography, and a flexible NoSQL database layer for long-term user and chat history persistence.

---

## 🏗️ Architecture & Component Stack

The application relies on the **Separation of Concerns** principle to maximize modularity and maintainability:

*   **Frontend UI (HTML5 / CSS3):** A clean, split-screen layout with a drag-and-drop PDF ingestion interface and a real-time responsive chat window.
*   **Frontend Logic (Vanilla JavaScript):** Asynchronous `fetch` calls decouple network interaction from layout rendering, preventing page refreshes during file processing or AI thinking states.
*   **Backend Server (Python / Flask):** Acts as the orchestrator handling session states, multi-part file routing, cryptographic operations, and template context injection.
*   **AI Orchestration Layer (LiteLLM):** A provider-agnostic bridge that routes system and user message frames to your chosen AI model (Local Ollama instances, OpenAI GPT, Anthropic Claude, etc.) without altering backend code.
*   **Database Layer (NoSQL / MongoDB):** Stores unstructured profile data and time-stamped interaction payloads securely.

---

## ⚙️ Environment Configuration

The application's global behaviors (such as its public branding name, database routing, and AI models) are managed through a root-level `.env` configuration file.

```text
APP_NAME=PDF Chatbot
LLM_MODEL=ollama/gemma4:31b-cloud
MONGO_URL=mongodb://localhost:27017
SECRET_KEY=super-secure-production-key-12345

# Remote AI Target Options (Uncomment if using cloud or external servers)
# OLLAMA_API_BASE=http://YOUR_REMOTE_AI_SERVER_IP:11434
# OPENAI_API_KEY=sk-proj-YOUR_OPENAI_API_KEY
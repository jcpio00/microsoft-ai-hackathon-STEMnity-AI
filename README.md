# STEMnity AI

A conversational AI STEM tutor for K-12, built with FastAPI, React, and open-source LLMs. STEMnity AI can solve math and science problems, explain step-by-step reasoning, and use specialized tools for algebra, factoring, unit conversion, and physical constants—all with multi-turn memory and safe moderation.

---

## 🚀 Project Goal

Empower students with an interactive, explainable, and safe AI STEM tutor that leverages open-source models and tools for real-world educational impact.

---

## 🏆 Microsoft AI Agents Hackathon 2025

This project was developed as part of the [Microsoft AI Agents Hackathon 2025](https://microsoft.com/ai-agents-hackathon).

---

## 🎥 Demo Video

_Coming soon!_

---

## ✨ Features

- **Conversational STEM Tutor:** Friendly, step-by-step explanations for math and science questions.
- **Tool-Augmented Reasoning:** Uses Python tools for algebraic equation solving, expression factoring, unit conversion, and physical constant lookup.
- **Math Rendering:** Beautiful LaTeX math output using MathJax in the chat UI.
- **Multi-Turn Memory:** Remembers conversation context per session for natural, multi-step problem solving.
- **Content Moderation:** Basic keyword moderation to keep conversations safe and on-topic.
- **Modern UI:** Responsive React chat interface with timestamps, typing indicators, and error boundaries.
- **Open Source Stack:** No proprietary dependencies—runs on your hardware or cloud.

---

## 🛠️ Tech Stack

- **Frontend:** React, Vite, better-react-mathjax, uuid
- **Backend:** FastAPI, LangGraph, LangChain, Azure AI Inference SDK, SymPy, SciPy, Pint, python-dotenv
- **LLM:** GitHub Models (DeepSeek-V3-0324 or compatible)
- **Memory:** LangGraph MemorySaver (per-session, in-memory)
- **Other:** ESLint, Prettier, dotenv

---

## 🏗️ Architecture Overview

```
[User] ⇄ [React Frontend] ⇄ [FastAPI Backend] ⇄ [LangGraph Agent]
                                         ⇓
                              [Python Tools: Math, Science]
                                         ⇓
                                 [LLM (GitHub Models)]
```

- **Frontend:** Handles chat UI, session/thread management, and math rendering.
- **Backend:** Receives chat, moderates, manages memory, and orchestrates the agent.
- **LangGraph Agent:** Implements the ReAct pattern, tool use, and memory.
- **Tools:** Python functions for math/science tasks.
- **LLM:** Generates reasoning, decides tool use, and explains answers.

See [ARCHITECTURE.md](ARCHITECTURE.md) for more details.

---

## ⚙️ Setup & Installation

### 1. **Clone the Repo**

```sh
git clone https://github.com/jcpio00/microsoft-ai-hackathon-STEMnity-AI
cd STEMnity-AI
```

### 2. **Backend Setup**

```sh
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

- Copy `.env.example` to `.env` and fill in your model credentials:

  ```
  GITHUB_PAT="your_github_pat_here"
  GITHUB_MODEL_ID="deepseek/DeepSeek-V3-0324"
  ```

- Start the backend:
  ```sh
  uvicorn main:app --reload
  ```

### 3. **Frontend Setup**

```sh
cd ../frontend
npm install
npm run dev
```

- The app will be available at [http://localhost:5173](http://localhost:5173).

---

## 🖥️ Running the App

1. Open [http://localhost:5173](http://localhost:5173) in your browser.
2. Ask a STEM question (e.g., "Solve 2x + 5 = 15" or "Convert 10 meters to feet").
3. Enjoy step-by-step explanations and beautiful math rendering!

---

## 🔒 Environment Variables

See `backend/.env.example` for required variables.

---

## 📝 Known Issues / Future Work

- **Memory is in-memory only:** Sessions are lost if the backend restarts. For production, use a persistent checkpointer.
- **Moderation is basic:** Consider integrating a more robust moderation service.
- **LLM output format:** Some models may not always follow the ReAct format; prompt engineering or model selection may be needed.
- **Tool coverage:** Expand toolset for more STEM domains.

---

## 📄 License

MIT License. See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Pull requests welcome! Please open issues for suggestions or bugs.

---

## 📚 Credits

- [LangChain](https://github.com/langchain-ai/langchain)
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [SymPy](https://www.sympy.org/)
- [SciPy](https://www.scipy.org/)
- [Pint](https://pint.readthedocs.io/)
- [better-react-mathjax](https://github.com/fast-reflexes/better-react-mathjax)
- [Microsoft AI Agents Hackathon](https://microsoft.com/ai-agents-hackathon)

---

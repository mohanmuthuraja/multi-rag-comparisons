# 🔬 Multi RAG Comparison App

A **Streamlit application** that demonstrates and compares **5 Retrieval-Augmented Generation (RAG) architectures** using **LangChain, OpenAI, and ChromaDB**.

The application allows users to ask a question and see how different RAG strategies respond using the same knowledge base.

---

# 🚀 RAG Techniques Implemented

| RAG Type | Description |
|------|------|
| Self RAG | The model first decides whether retrieval is required |
| Fusion RAG | Generates multiple search queries and merges retrieved results |
| Advanced RAG | Rewrites the user query for better retrieval |
| Speculative RAG | Generates a quick answer and then verifies using retrieved documents |
| Corrective RAG | Detects outdated assumptions and corrects them |

---

# 🧠 How It Works

1. Documents are converted into **embeddings**
2. Stored in **Chroma Vector Database**
3. User asks a question
4. Each RAG strategy retrieves context differently
5. LLM generates answers based on retrieved information
6. Results are shown side-by-side for comparison

---

# 🛠 Tech Stack

- Python
- Streamlit
- LangChain
- OpenAI
- ChromaDB
- python-dotenv

---

# 📂 Project Structure

```
multi-rag-comparision
│
├── multi_rag_comparison.py
├── requirements.txt
├── .env
└── README.md
```

---

# ⚙️ Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/multi-rag-comparision.git
cd multi-rag-comparision
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate the environment

Windows

```bash
venv\Scripts\activate
```

Mac / Linux

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Add OpenAI API Key

Create a `.env` file in the project root.

```
OPENAI_API_KEY=your_openai_api_key
```

---

# ▶️ Run the Application

```bash (run only this program)
streamlit run multi_rag_comparison.py
```

Open browser:

```
http://localhost:8501
```

---

# 📊 Example Question

Try asking:

```
When does employee insurance start?
```

Each RAG architecture will generate its own answer based on the same documents.

---

# 🧾 Sample Documents

The demo uses small example documents such as:

```
The 90-day waiting period was removed in 2024.
Insurance now starts on day one.
```

These are embedded and stored in the vector database.

---

# 🔍 RAG Strategy Overview

### Self RAG
The LLM determines if document retrieval is needed before answering.

### Fusion RAG
Multiple search queries are generated to retrieve more diverse context.

### Advanced RAG
The question is rewritten to improve retrieval accuracy.

### Speculative RAG
The model produces a quick answer and then verifies it using retrieved documents.

### Corrective RAG
The system checks for outdated assumptions and corrects them using updated documents.

---

# 📈 Possible Improvements

- Upload PDF documents
- Add hybrid search (BM25 + embeddings)
- Add reranking
- Support larger document collections
- Compare embedding models
- Track latency and token usage
- Add RAG evaluation metrics

---

# 🎯 Purpose of This Project

This project demonstrates how different **RAG architectures behave for the same query**, which helps understand trade-offs in:

- accuracy
- retrieval quality
- latency
- reasoning ability

---

# 👨‍💻 Author

**Mohanraj M**

SAP Data Migration Consultant exploring  
**AI • RAG Systems • Data Engineering**

---

⭐ If you find this project useful, consider giving the repository a star.

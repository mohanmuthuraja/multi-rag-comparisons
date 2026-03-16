# 🦜 LangChain Corrective RAG System

**Insurance Policy Q&A with Automatic Correction**

Built with LangChain + OpenAI + Streamlit

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_lc.txt
```

### 2. Run the App
```bash

streamlit run multi_rag_comparison.py
```

### 3. Enter Your OpenAI API Key
- Paste your key in the sidebar
- Wait for initialization
- Start asking questions!

---

## 🎯 What It Does

This system demonstrates **Corrective RAG** using LangChain:

**❌ User says:** "I heard there's a 90-day waiting period for insurance"

**✅ System responds:** "That's outdated! The 90-day period was eliminated Jan 1, 2024. Insurance now starts Day 1."

---

## 🦜 LangChain Components Used

```python
OpenAIEmbeddings      # Text to vectors
Chroma                # Vector database  
ChatOpenAI            # GPT-3.5/GPT-4
RetrievalQA           # RAG chain
PromptTemplate        # Custom prompts
```

---

## 📁 Files

- `langchain_app.py` - Main Streamlit application
- `requirements_lc.txt` - Python dependencies
- `LANGCHAIN_VSCODE_GUIDE.md` - Detailed setup guide

---

## 💰 Cost

- **GPT-3.5-turbo**: ~$0.00005 per question (recommended for testing)
- **GPT-4**: ~$0.001 per question (better quality)

Switch models in code (line 28):
```python
model_name="gpt-3.5-turbo"  # or "gpt-4"
```

---

## 🎨 Features

✅ Automatic correction of outdated info  
✅ Source document citations  
✅ Beautiful web interface  
✅ Sample insurance policies included  
✅ LangChain framework (industry standard)  

---

## 📚 Try These Questions

```
When does my health insurance start? I heard there's a 90-day waiting period.

How many vacation days do I get as a new employee?

Can I work from home 4 days a week?

What health insurance plans are available?
```

---

## 🔧 Customization

### Add Your Own Documents

In `get_sample_documents()`, add:
```python
{
    'text': """Your policy text...""",
    'metadata': {
        'source': 'Policy.pdf',
        'last_updated': '2024-03-14'
    }
}
```

### Change Retrieval Count

Line 62:
```python
search_kwargs={"k": 3}  # Change to 5 for more docs
```

---

## 🆘 Troubleshooting

**"No module named 'langchain'"**
```bash
pip install langchain
```

**"Invalid API key"**  
Get one at: https://platform.openai.com/api-keys

**Port already in use**
```bash
streamlit run langchain_app.py --server.port 8502
```

---

## 📖 Full Guide

See **LANGCHAIN_VSCODE_GUIDE.md** for:
- Step-by-step VS Code setup
- Detailed troubleshooting
- LangChain architecture explanation
- Customization examples

---

**Made with 🦜 LangChain**

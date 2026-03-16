# 🦜 LangChain Corrective RAG - Complete VS Code Setup Guide

## 📋 What You'll Build

A **LangChain-powered Corrective RAG system** with:
- 🦜 LangChain framework (industry standard)
- 🤖 OpenAI GPT-3.5-turbo or GPT-4
- 🎨 Beautiful Streamlit web interface
- ✅ Automatic correction of outdated information
- 📚 Insurance policy example (easy to understand)

---

## 🎯 STEP-BY-STEP SETUP IN VS CODE

### **STEP 1: Open VS Code and Create Project Folder**

1. **Open VS Code**
2. Click `File` → `Open Folder`
3. Create a new folder named: `langchain-corrective-rag`
4. Select the folder and click `Open`

---

### **STEP 2: Download the Files**

Save these **2 files** in your `langchain-corrective-rag` folder:

1. ✅ **langchain_app.py** (main application - 500 lines)
2. ✅ **requirements_lc.txt** (dependencies)

Your folder structure:
```
langchain-corrective-rag/
├── langchain_app.py
└── requirements_lc.txt
```

---

### **STEP 3: Open Terminal in VS Code**

**Windows/Linux:** Press **`Ctrl + ` `** (backtick key, above Tab)

**Mac:** Press **`Cmd + ` `**

Or go to: `Terminal` → `New Terminal`

You should see a terminal at the bottom of VS Code.

---

### **STEP 4: Install Python Dependencies**

In the terminal, run this command:

```bash
pip install -r requirements_lc.txt
```

**Alternative (if above doesn't work):**
```bash
pip install openai langchain chromadb streamlit tiktoken
```

**Or with pip3:**
```bash
pip3 install openai langchain chromadb streamlit tiktoken
```

⏳ **Wait 3-5 minutes** - This will download:
- LangChain framework (~200MB)
- OpenAI SDK
- ChromaDB vector database
- Streamlit web framework

You'll see progress bars showing installations.

---

### **STEP 5: Verify Installation**

Check if everything installed correctly:

```bash
python -c "import langchain; print('LangChain:', langchain.__version__)"
```

You should see: `LangChain: 0.1.x` (or similar)

**If you see an error**, try:
```bash
python3 -c "import langchain; print('LangChain:', langchain.__version__)"
```

---

### **STEP 6: Run the Application**

Now run the Streamlit app:

```bash
streamlit run langchain_app.py
```

**Alternative:**
```bash
python -m streamlit run langchain_app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

🎉 **Your browser will automatically open!**

If not, manually go to: **http://localhost:8501**

---

### **STEP 7: Enter Your OpenAI API Key**

In the web interface:

1. Look at the **left sidebar**
2. Find the **"OpenAI API Key"** text box
3. **Paste your API key** (starts with `sk-...`)
4. **Press Enter**

The system will initialize (takes 5-10 seconds):
- ✅ Creating LangChain components
- ✅ Loading OpenAI embeddings
- ✅ Creating Chroma vector store
- ✅ Loading 4 sample documents

When done, you'll see:
- ✅ "LangChain Initialized"
- 📚 "4 documents loaded"

---

### **STEP 8: Ask Your First Question!**

#### **Option A: Use Sample Questions (Easiest)**

In the sidebar, click any sample question button:
- "When does my health insurance start? I heard there's a 90-day waiting period."

The system will automatically answer!

#### **Option B: Type Your Own Question**

In the main area:
1. Type in the text box
2. Click **"🔍 Ask"** button

---

## 🐛 TROUBLESHOOTING

### **Problem 1: "streamlit: command not found"**
```bash
python -m streamlit run langchain_app.py
```

### **Problem 2: "No module named 'langchain'"**
```bash
pip install langchain
```

### **Problem 3: "Invalid API key"**
- Check it starts with `sk-`
- Verify at https://platform.openai.com/api-keys

### **Problem 4: "Port 8501 already in use"**
```bash
streamlit run langchain_app.py --server.port 8502
```

---

## ✅ SUCCESS CHECKLIST

- [ ] VS Code open
- [ ] Files downloaded
- [ ] Dependencies installed
- [ ] OpenAI API key ready
- [ ] App running
- [ ] Ready to test!

---

**Run this and you're done:**
```bash
streamlit run langchain_app.py
```

🎉 **Enjoy your LangChain Corrective RAG system!**

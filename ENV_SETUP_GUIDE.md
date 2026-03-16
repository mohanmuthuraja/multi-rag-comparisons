# 🔒 Complete Guide: Secure API Key Setup with .env in VS Code

## 🎯 Why Use .env Files?

**Security Benefits:**
- ✅ Keeps API keys out of your code
- ✅ Prevents accidental commits to Git
- ✅ Easy to share code without sharing keys
- ✅ Different keys for different environments

---

## 📁 Project Structure

Your folder should look like this:

```
langchain-rag/
├── langchain_corrective_rag_secure.py  ← Updated main app
├── requirements_secure.txt             ← Updated requirements
├── .env                                ← Your API key (YOU CREATE THIS)
├── .env.example                        ← Template file
├── .gitignore                          ← Protects .env from Git
├── test_langchain_setup.py
└── README files...
```

---

## 🚀 Step-by-Step Setup in VS Code

### **STEP 1: Open Your Project in VS Code**

1. Open VS Code
2. Click `File` → `Open Folder`
3. Select your `langchain-rag` folder
4. You should see all files in the left sidebar

---

### **STEP 2: Create the .env File**

#### **Method A: Using VS Code UI (Easiest)**

1. In VS Code, right-click in the file explorer (left sidebar)
2. Click **"New File"**
3. Name it exactly: `.env` (with the dot at the beginning!)
4. Press Enter

#### **Method B: Using Terminal**

1. Open terminal in VS Code (Ctrl + `)
2. Type:
   ```bash
   touch .env
   ```
3. Press Enter

**Important:** The file MUST be named `.env` exactly - with the dot!

---

### **STEP 3: Add Your API Key to .env**

1. **Open the `.env` file** you just created (double-click it)

2. **Add this line** (replace with your actual key):
   ```
   OPENAI_API_KEY=sk-proj-your-actual-api-key-here
   ```

3. **Example** (DO NOT copy this - use your own key!):
   ```
   OPENAI_API_KEY=sk-proj-aBcDeFgHiJkLmNoPqRsTuVwXyZ1234567890
   ```

4. **Save the file** (Ctrl + S)

**Your .env file should look like this:**
```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**That's it!** Just one line.

---

### **STEP 4: Verify .gitignore is Working**

1. **Open `.gitignore`** file (should already exist)

2. **Check it contains** this line:
   ```
   .env
   ```

3. **Look at the file explorer** in VS Code:
   - `.env` should appear **grayed out** or **faded**
   - This means Git is ignoring it ✅

**If .env is NOT grayed out:**
- Make sure `.gitignore` has `.env` on its own line
- Save `.gitignore`
- Restart VS Code

---

### **STEP 5: Install Updated Dependencies**

Open terminal (Ctrl + `) and run:

```bash
pip install -r requirements_secure.txt
```

This installs `python-dotenv` which loads the .env file.

**Or install manually:**
```bash
pip install python-dotenv
```

---

### **STEP 6: Run the Secure Version**

In the terminal, run:

```bash
streamlit run langchain_corrective_rag_secure.py
```

**What you'll see:**

The app opens and in the sidebar you'll see:
```
✅ API Key loaded from .env file
🔒 Your API key is secure and not displayed
```

**Success!** Your API key is now secure! 🎉

---

## 🎨 Visual Guide - What You'll See in VS Code

```
┌─────────────────────────────────────────────────────────┐
│  VS Code - langchain-rag                               │
├─────────────────────────────────────────────────────────┤
│  EXPLORER                                               │
│  📁 langchain-rag                                       │
│    📄 langchain_corrective_rag_secure.py               │
│    📄 requirements_secure.txt                          │
│    📄 .env                    ← Grayed out/faded       │
│    📄 .env.example                                     │
│    📄 .gitignore                                       │
│    📄 test_langchain_setup.py                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔍 How It Works

### **Before (Insecure):**

```python
# API key in code - BAD! ❌
api_key = "sk-proj-xxxxx"  # Visible in code
```

### **After (Secure):**

```python
# API key in .env file - GOOD! ✅
from dotenv import load_dotenv
import os

load_dotenv()  # Loads .env file
api_key = os.getenv("OPENAI_API_KEY")  # Gets key from environment
```

**Your .env file:**
```
OPENAI_API_KEY=sk-proj-xxxxx
```

**Your .gitignore:**
```
.env
```

**Result:** API key stays on your computer, never goes to Git! 🔒

---

## ✅ Verification Checklist

Before running, verify:

- [ ] `.env` file exists
- [ ] `.env` contains: `OPENAI_API_KEY=sk-...`
- [ ] `.gitignore` contains: `.env`
- [ ] `.env` appears grayed out in VS Code
- [ ] `python-dotenv` is installed
- [ ] Using `langchain_corrective_rag_secure.py` (the secure version)

---

## 🧪 Test Your Setup

### **Test 1: Check if .env is Loaded**

In terminal:
```bash
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('✅ Works!' if os.getenv('OPENAI_API_KEY') else '❌ Not loaded')"
```

**Expected output:** `✅ Works!`

### **Test 2: Run the App**

```bash
streamlit run langchain_corrective_rag_secure.py
```

**Expected in sidebar:**
```
✅ API Key loaded from .env file
🔒 Your API key is secure and not displayed
```

---

## 🐛 Troubleshooting

### **Issue 1: "API Key not loaded from .env"**

**Possible causes:**
- File is named `.env.txt` instead of `.env`
- Extra spaces in the file
- Wrong format

**Solution:**
1. Open `.env` file
2. Make sure it contains EXACTLY:
   ```
   OPENAI_API_KEY=sk-your-key-here
   ```
3. No spaces around `=`
4. No quotes around the key
5. Save and restart the app

---

### **Issue 2: .env File Not Showing in VS Code**

**Solution:**
1. Make sure "Show hidden files" is enabled
2. Press `Ctrl + ,` (Settings)
3. Search for "files.exclude"
4. Make sure `.env` is NOT in the exclude list

---

### **Issue 3: Git is Still Tracking .env**

**Check if .env is ignored:**
```bash
git status
```

**If .env appears in the list:**
1. Make sure `.gitignore` has `.env` line
2. Run:
   ```bash
   git rm --cached .env
   git add .gitignore
   git commit -m "Add .env to gitignore"
   ```

---

### **Issue 4: "No module named 'dotenv'"**

**Solution:**
```bash
pip install python-dotenv
```

---

## 📝 .env File Examples

### ✅ **CORRECT:**

```
OPENAI_API_KEY=sk-proj-abc123xyz789
```

### ❌ **WRONG:**

```
OPENAI_API_KEY = sk-proj-abc123xyz789  ← Extra spaces
OPENAI_API_KEY="sk-proj-abc123xyz789" ← Quotes not needed
OpenAI_API_Key=sk-proj-abc123xyz789   ← Wrong case
OPENAI_API_KEY=your-api-key-here      ← Placeholder not replaced
```

---

## 🔐 Security Best Practices

### **DO:**
- ✅ Keep `.env` in `.gitignore`
- ✅ Use different API keys for dev/prod
- ✅ Share `.env.example` (without real keys)
- ✅ Regenerate keys if accidentally exposed
- ✅ Use environment variables in production

### **DON'T:**
- ❌ Commit `.env` to Git
- ❌ Share `.env` file with others
- ❌ Put API keys directly in code
- ❌ Upload `.env` to cloud storage
- ❌ Screenshot `.env` contents

---

## 📤 Sharing Your Project

### **What to Share:**
- ✅ All `.py` files
- ✅ `requirements_secure.txt`
- ✅ `.env.example` (template)
- ✅ `.gitignore`
- ✅ README files

### **What NOT to Share:**
- ❌ `.env` file (has your key!)
- ❌ Any file with actual API keys

### **Instructions for Others:**

Tell them to:
1. Copy `.env.example` to `.env`
2. Add their own API key
3. Run the app

---

## 🎯 Quick Reference

### **Create .env:**
```bash
touch .env
```

### **Edit .env:**
```
OPENAI_API_KEY=sk-proj-your-key-here
```

### **Install dotenv:**
```bash
pip install python-dotenv
```

### **Run secure app:**
```bash
streamlit run langchain_corrective_rag_secure.py
```

### **Check if it works:**
Look for: `✅ API Key loaded from .env file`

---

## 🌟 Comparison: Manual vs .env

### **Without .env (Manual Input):**

**Pros:**
- Quick for testing
- No file setup needed

**Cons:**
- ❌ Must enter key every time
- ❌ Key visible in sidebar
- ❌ Easy to accidentally share
- ❌ Not professional

### **With .env (Recommended):**

**Pros:**
- ✅ Automatic key loading
- ✅ Key hidden from UI
- ✅ Safe from Git
- ✅ Professional setup
- ✅ Easy to switch keys

**Cons:**
- Requires initial setup (5 minutes)

---

## 🎓 Understanding the Code

### **How the app loads your key:**

```python
# 1. Import libraries
from dotenv import load_dotenv
import os

# 2. Load .env file
load_dotenv()  # Reads .env and loads into environment

# 3. Get the API key
api_key = os.getenv("OPENAI_API_KEY")

# 4. Check if loaded
if api_key:
    print("✅ Loaded from .env")
else:
    print("❌ Not found, asking user")
```

---

## 📊 File Priority

If you have both methods:

1. **First**: Check `.env` file
2. **Second**: Ask user for input

**This means:**
- If `.env` exists → use it (automatic)
- If `.env` missing → show input field (manual)

---

## 🚀 You're All Set!

**Final Checklist:**
- [ ] `.env` file created
- [ ] API key added to `.env`
- [ ] `.gitignore` includes `.env`
- [ ] `python-dotenv` installed
- [ ] App running with secure version

**Run this command:**
```bash
streamlit run langchain_corrective_rag_secure.py
```

**You should see:**
```
✅ API Key loaded from .env file
🔒 Your API key is secure and not displayed
```

**Perfect! Your API key is now secure! 🎉🔒**

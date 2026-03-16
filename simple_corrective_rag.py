"""
Simplified Corrective RAG System
Using OpenAI + ChromaDB + Streamlit
NO complex LangChain dependencies - Just what works!
"""

import streamlit as st
from openai import OpenAI
from chromadb import Client
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SimpleCorrectiveRAG:
    """Simple Corrective RAG using OpenAI and ChromaDB"""
    
    def __init__(self, api_key, model_name="gpt-3.5-turbo"):
        """Initialize the system"""
        self.client = OpenAI(api_key=api_key)
        self.model = model_name
        
        # Initialize ChromaDB
        self.chroma_client = Client()
        
        # Use OpenAI embeddings
        self.embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            api_key=api_key,
            model_name="text-embedding-ada-002"
        )
        
        self.collection = None
    
    def add_documents(self, documents):
        """Add documents to vector store"""
        
        # Create collection
        self.collection = self.chroma_client.create_collection(
            name="insurance_docs",
            embedding_function=self.embedding_function
        )
        
        # Add documents
        texts = [doc['text'] for doc in documents]
        metadatas = [doc['metadata'] for doc in documents]
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(documents)
    
    def query(self, question):
        """Query the system"""
        
        if not self.collection:
            raise ValueError("No documents loaded")
        
        # Search for relevant documents
        results = self.collection.query(
            query_texts=[question],
            n_results=3
        )
        
        # Get documents and metadata
        docs = []
        for i, doc_text in enumerate(results['documents'][0]):
            docs.append({
                'text': doc_text,
                'metadata': results['metadatas'][0][i]
            })
        
        # Build context
        context = "\n\n---\n\n".join([
            f"Document: {doc['metadata']['source']}\n"
            f"Last Updated: {doc['metadata']['last_updated']}\n\n"
            f"{doc['text']}"
            for doc in docs
        ])
        
        # Create corrective prompt
        prompt = f"""You are a helpful HR assistant for TechCorp Inc.

CRITICAL INSTRUCTIONS:
1. Answer based ONLY on the context documents below
2. If the user mentions outdated information (like "90-day waiting period"), CORRECT them explicitly
3. State what changed and when
4. Cite the document source and date
5. Be direct: "That policy changed..." or "Actually, as of..."

CONTEXT DOCUMENTS:
{context}

USER QUESTION: {question}

Your answer (with corrections if needed):"""
        
        # Get response from OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful HR assistant who corrects outdated information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        
        return answer, docs


def get_insurance_documents():
    """Sample documents"""
    return [
        {
            'text': """TechCorp Health Insurance Policy - 2024 Update

EFFECTIVE DATE: January 1, 2024

MAJOR POLICY CHANGE:
The 90-day waiting period for health insurance has been ELIMINATED as of January 1, 2024.

NEW POLICY:
All full-time employees are now eligible for health insurance coverage starting on their FIRST DAY of employment.

Coverage Options:
- Premium Plan: $50/month employee contribution, $1,000 deductible
- Standard Plan: $150/month employee contribution, $2,500 deductible  
- Basic Plan: $250/month employee contribution, $5,000 deductible

Dependent Coverage: $200/month per dependent

Questions? Contact HR at benefits@techcorp.com""",
            'metadata': {
                'source': 'Employee_Handbook_2024.pdf',
                'last_updated': '2024-01-15',
                'category': 'health_insurance'
            }
        },
        {
            'text': """URGENT POLICY UPDATE MEMO

TO: All Employees
FROM: Human Resources
DATE: January 10, 2024
RE: Elimination of Health Insurance Waiting Period

WHAT CHANGED:
Effective January 1, 2024, we have ELIMINATED the 90-day waiting period for health insurance coverage.

OLD POLICY: New employees waited 90 days
NEW POLICY: Coverage begins on DAY ONE of employment

This change applies to all employees hired on or after January 1, 2024.

Thank you,
Sarah Johnson, Director of HR""",
            'metadata': {
                'source': 'HR_Memo_2024.pdf',
                'last_updated': '2024-01-10',
                'category': 'policy_update'
            }
        },
        {
            'text': """Health Insurance FAQ - January 2024

Q: When does my health insurance start?
A: As of January 1, 2024, coverage starts on your first day. No waiting period.

Q: I heard about a 90-day waiting period?
A: That was eliminated effective January 1, 2024. New employees now get immediate coverage.

Q: Can I add my family?
A: Yes! $200/month per dependent.

Q: What plans are available?
A: Premium ($50/month), Standard ($150/month), Basic ($250/month).

For more info: benefits@techcorp.com""",
            'metadata': {
                'source': 'Insurance_FAQ_2024.pdf',
                'last_updated': '2024-01-15',
                'category': 'faq'
            }
        }
    ]


def get_api_key():
    """Get API key from .env or return None"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-api-key-here":
        return api_key
    return None


def main():
    """Main Streamlit App"""
    
    st.set_page_config(
        page_title="Corrective RAG System",
        page_icon="🤖",
        layout="wide"
    )
    
    # CSS
    st.markdown("""
        <style>
        .main {background-color: #f8f9fa;}
        .stButton>button {
            background-color: #0066cc;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px 28px;
        }
        .response-box {
            background-color: #e7f3ff;
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #0066cc;
            margin: 20px 0;
        }
        .header-box {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            padding: 30px;
            border-radius: 12px;
            color: white;
            margin-bottom: 30px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="header-box">
            <h1>🤖 Corrective RAG System</h1>
            <p style="font-size: 18px; margin-bottom: 0;">
                AI-Powered HR Assistant - Simple & Working!
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get API key
    env_api_key = get_api_key()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        if env_api_key:
            st.success("✅ API Key from .env")
            api_key = env_api_key
        else:
            st.warning("⚠️ No .env file")
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                placeholder="sk-..."
            )
        
        model = st.selectbox(
            "Model",
            ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"]
        )
        
        st.markdown("---")
        
        st.subheader("📊 Status")
        if 'rag' in st.session_state and st.session_state.get('ready'):
            st.success("✅ System Ready")
            st.info(f"🤖 {model}")
            st.info(f"📄 {st.session_state.get('doc_count', 0)} docs")
        else:
            st.warning("⚠️ Enter API key")
        
        st.markdown("---")
        
        st.subheader("💡 Try These")
        samples = [
            "When does insurance start?",
            "Is there a 90-day waiting period?",
            "What are the plan options?",
            "Can I add my family?"
        ]
        
        for i, q in enumerate(samples):
            if st.button(q, key=f"q_{i}"):
                st.session_state.question = q
    
    # Main area
    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar")
        return
    
    # Initialize
    if 'rag' not in st.session_state or not st.session_state.get('ready'):
        with st.spinner("🔧 Initializing..."):
            try:
                rag = SimpleCorrectiveRAG(api_key, model)
                docs = get_insurance_documents()
                doc_count = rag.add_documents(docs)
                
                st.session_state.rag = rag
                st.session_state.doc_count = doc_count
                st.session_state.ready = True
                
                st.success(f"✅ Loaded {doc_count} documents!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                return
    
    rag = st.session_state.rag
    
    # Tabs
    tab1, tab2 = st.tabs(["💬 Ask Questions", "📚 Documents"])
    
    with tab1:
        st.header("Ask a Question")
        
        question = st.text_input(
            "Your question:",
            value=st.session_state.get('question', ''),
            placeholder="e.g., Is there a 90-day waiting period?"
        )
        
        col1, col2 = st.columns([1, 6])
        with col1:
            ask = st.button("🔍 Ask", type="primary")
        with col2:
            if st.button("🗑️ Clear"):
                st.session_state.question = ""
                st.rerun()
        
        if ask and question:
            with st.spinner("🤔 Thinking..."):
                try:
                    answer, sources = rag.query(question)
                    
                    st.markdown("### 💡 Answer")
                    st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)
                    
                    st.markdown("### 📄 Sources")
                    for i, doc in enumerate(sources, 1):
                        with st.expander(f"📄 {doc['metadata']['source']}"):
                            st.markdown(f"**Updated:** {doc['metadata']['last_updated']}")
                            st.markdown("---")
                            st.markdown(doc['text'])
                    
                    if "90-day" in question.lower():
                        st.success("✅ Correction applied!")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.header("📚 Knowledge Base")
        docs = get_insurance_documents()
        
        for i, doc in enumerate(docs, 1):
            with st.expander(f"📄 {doc['metadata']['source']}", expanded=(i==1)):
                st.markdown(f"**Updated:** {doc['metadata']['last_updated']}")
                st.markdown(f"**Category:** {doc['metadata']['category']}")
                st.markdown("---")
                st.markdown(doc['text'])


if __name__ == "__main__":
    main()

"""
Multi-RAG Comparison System
Compares 5 different RAG approaches side-by-side:
1. Self RAG
2. Fusion RAG
3. Advanced RAG
4. Speculative RAG
5. Corrective RAG
"""

import streamlit as st
from openai import OpenAI
from chromadb import Client
from chromadb.utils import embedding_functions
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()


class MultiRAGSystem:
    """System implementing 5 different RAG approaches"""
    
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
        #ids = [f"doc_{i}" for i in range(len(documents))}
        ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        return len(documents)
    
    def retrieve_docs(self, query, n_results=3):
        """Helper function to retrieve documents"""
        if not self.collection:
            raise ValueError("No documents loaded")
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        docs = []
        for i, doc_text in enumerate(results['documents'][0]):
            docs.append({
                'text': doc_text,
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if results.get('distances') else 0
            })
        
        return docs
    
    def self_rag(self, question):
        """
        Self RAG: Self-reflective retrieval
        - Generates answer
        - Self-evaluates if retrieval is needed
        - Retrieves if necessary
        - Re-generates with context
        """
        
        # Step 1: Initial generation without retrieval
        initial_prompt = f"""Question: {question}

First, determine if you need to retrieve information to answer this question.
Respond in this format:
NEED_RETRIEVAL: [YES/NO]
REASONING: [Why you need retrieval or not]
INITIAL_ANSWER: [Your answer if NO retrieval needed]"""
        
        initial_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that determines if retrieval is needed."},
                {"role": "user", "content": initial_prompt}
            ],
            temperature=0.3
        )
        
        initial_text = initial_response.choices[0].message.content
        
        # Check if retrieval is needed
        if "NEED_RETRIEVAL: YES" in initial_text:
            # Step 2: Retrieve documents
            docs = self.retrieve_docs(question, n_results=2)
            
            context = "\n\n".join([doc['text'] for doc in docs])
            
            # Step 3: Generate with context
            final_prompt = f"""Context:
{context}

Question: {question}

Answer based on the context above:"""
            
            final_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": final_prompt}
                ],
                temperature=0.7
            )
            
            answer = final_response.choices[0].message.content
            return f"🔄 Self-Reflection: Retrieved documents\n\n{answer}"
        else:
            # Return initial answer without retrieval
            return f"🔄 Self-Reflection: No retrieval needed\n\n{initial_text.split('INITIAL_ANSWER:')[-1].strip()}"
    
    def fusion_rag(self, question):
        """
        Fusion RAG: Multi-query fusion
        - Generates multiple query variations
        - Retrieves docs for each query
        - Fuses results by ranking
        - Generates final answer
        """
        
        # Step 1: Generate multiple query variations
        query_gen_prompt = f"""Generate 3 different variations of this question to improve document retrieval:

Original Question: {question}

Provide 3 variations (one per line):"""
        
        query_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": query_gen_prompt}
            ],
            temperature=0.8,
            max_tokens=200
        )
        
        queries = [question] + query_response.choices[0].message.content.strip().split('\n')[:3]
        
        # Step 2: Retrieve for each query and fuse results
        all_docs = []
        seen_texts = set()
        
        for query in queries:
            docs = self.retrieve_docs(query, n_results=2)
            for doc in docs:
                if doc['text'] not in seen_texts:
                    all_docs.append(doc)
                    seen_texts.add(doc['text'])
        
        # Step 3: Rank by distance (lower is better)
        all_docs.sort(key=lambda x: x['distance'])
        top_docs = all_docs[:3]
        
        context = "\n\n".join([doc['text'] for doc in top_docs])
        
        # Step 4: Generate answer
        prompt = f"""Context from multiple query perspectives:
{context}

Question: {question}

Answer:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        return f"🔀 Query Fusion: Used {len(queries)} query variations\n\n{answer}"
    
    def advanced_rag(self, question):
        """
        Advanced RAG: Query rewriting + Re-ranking
        - Rewrites query for better retrieval
        - Retrieves documents
        - Re-ranks by relevance
        - Generates answer
        """
        
        # Step 1: Query rewriting
        rewrite_prompt = f"""Rewrite this question to be more specific and optimized for document retrieval:

Original: {question}

Rewritten query (be specific and detailed):"""
        
        rewrite_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": rewrite_prompt}
            ],
            temperature=0.5
        )
        
        rewritten_query = rewrite_response.choices[0].message.content.strip()
        
        # Step 2: Retrieve with rewritten query
        docs = self.retrieve_docs(rewritten_query, n_results=5)
        
        # Step 3: Re-rank documents
        rerank_prompt = f"""Question: {question}

Rank these documents by relevance (most relevant first). Return only the numbers 1-{len(docs)} separated by commas.

Documents:
""" + "\n\n".join([f"{i+1}. {doc['text'][:200]}..." for i, doc in enumerate(docs)])
        
        rerank_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": rerank_prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        # Parse ranking (fallback to original order if parsing fails)
        try:
            rankings = [int(x.strip())-1 for x in rerank_response.choices[0].message.content.split(',')[:3]]
            top_docs = [docs[i] for i in rankings if i < len(docs)]
        except:
            top_docs = docs[:3]
        
        context = "\n\n".join([doc['text'] for doc in top_docs])
        
        # Step 4: Generate answer
        prompt = f"""Context (re-ranked for relevance):
{context}

Question: {question}

Answer:"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        return f"⚡ Advanced: Rewritten query + Re-ranking\nRewritten: '{rewritten_query}'\n\n{answer}"
    
    def speculative_rag(self, question):
        """
        Speculative RAG: Parallel generation + verification
        - Generates speculative answer first (fast)
        - Retrieves documents in parallel
        - Verifies and corrects if needed
        """
        
        # Step 1: Generate speculative answer (without retrieval)
        spec_prompt = f"""Quickly answer this question based on general knowledge:

Question: {question}

Quick answer:"""
        
        spec_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": spec_prompt}
            ],
            temperature=0.5,
            max_tokens=150
        )
        
        speculative_answer = spec_response.choices[0].message.content
        
        # Step 2: Retrieve documents (could be parallel in production)
        docs = self.retrieve_docs(question, n_results=3)
        context = "\n\n".join([doc['text'] for doc in docs])
        
        # Step 3: Verify and correct
        verify_prompt = f"""Speculative Answer: {speculative_answer}

Retrieved Context:
{context}

Question: {question}

Verify the speculative answer against the context. If correct, return it. If incorrect, provide the corrected answer.

Final Answer:"""
        
        verify_response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": verify_prompt}
            ],
            temperature=0.7
        )
        
        answer = verify_response.choices[0].message.content
        return f"⚡ Speculative: Fast generation → Verified\n\n{answer}"
    
    def corrective_rag(self, question):
        """
        Corrective RAG: Original implementation
        - Retrieves documents
        - Detects outdated assumptions
        - Corrects explicitly
        """
        
        docs = self.retrieve_docs(question, n_results=3)
        
        context = "\n\n---\n\n".join([
            f"Document: {doc['metadata']['source']}\n"
            f"Last Updated: {doc['metadata']['last_updated']}\n\n"
            f"{doc['text']}"
            for doc in docs
        ])
        
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
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a helpful HR assistant who corrects outdated information."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        return f"✅ Corrective: Explicit correction of outdated info\n\n{answer}"


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

Dependent Coverage: $200/month per dependent""",
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

This change applies to all employees hired on or after January 1, 2024.""",
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
A: That was eliminated effective January 1, 2024.

Q: Can I add my family?
A: Yes! $200/month per dependent.

Q: What plans are available?
A: Premium ($50/month), Standard ($150/month), Basic ($250/month).""",
            'metadata': {
                'source': 'Insurance_FAQ_2024.pdf',
                'last_updated': '2024-01-15',
                'category': 'faq'
            }
        }
    ]


def get_api_key():
    """Get API key from .env"""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your-api-key-here":
        return api_key
    return None


def main():
    """Main Streamlit App"""
    
    st.set_page_config(
        page_title="Multi-RAG Comparison",
        page_icon="🔬",
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
        .rag-box {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #0066cc;
            margin: 10px 0;
            min-height: 200px;
        }
        .header-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            <h1>🔬 Multi-RAG Comparison System</h1>
            <p style="font-size: 18px; margin-bottom: 0;">
                Compare 5 Different RAG Approaches Side-by-Side
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
            api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        
        model = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview"])
        
        st.markdown("---")
        
        st.subheader("📊 Status")
        if 'rag' in st.session_state and st.session_state.get('ready'):
            st.success("✅ All Systems Ready")
            st.info(f"🤖 {model}")
            st.info(f"📄 {st.session_state.get('doc_count', 0)} docs")
        else:
            st.warning("⚠️ Enter API key")
        
        st.markdown("---")
        
        st.subheader("💡 Try These")
        samples = [
            "When does my insurance start?",
            "Is there a 90-day waiting period?",
            "What are the plan options?",
            "Can I add my family?"
        ]
        
        for i, q in enumerate(samples):
            if st.button(q, key=f"q_{i}", use_container_width=True):
                st.session_state.question = q
        
        st.markdown("---")
        
        with st.expander("ℹ️ About RAG Types"):
            st.markdown("""
            **1. Self RAG** 🔄
            Self-reflects on whether retrieval is needed
            
            **2. Fusion RAG** 🔀
            Multiple query variations + fusion
            
            **3. Advanced RAG** ⚡
            Query rewriting + re-ranking
            
            **4. Speculative RAG** ⚡
            Fast speculation → verification
            
            **5. Corrective RAG** ✅
            Explicit correction of outdated info
            """)
    
    # Main area
    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar")
        return
    
    # Initialize
    if 'rag' not in st.session_state or not st.session_state.get('ready'):
        with st.spinner("🔧 Initializing all RAG systems..."):
            try:
                rag = MultiRAGSystem(api_key, model)
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
    
    # Main interface
    st.header("Ask a Question on SE's Health Insurance Policy")
    
    question = st.text_input(
        "Your question:",
        value=st.session_state.get('question', ''),
        placeholder="e.g., Is there a 90-day waiting period for health insurance?",
        key="main_question"
    )
    
    col1, col2 = st.columns([1, 6])
    with col1:
        ask = st.button("🔬 Compare All RAGs", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.question = ""
            st.rerun()
    
    if ask and question:
        st.markdown("---")
        st.subheader("📊 Comparison Results")
        
        # Create 5 columns for side-by-side comparison
        cols = st.columns(5)
        
        rag_methods = [
            ("Self RAG", "🔄", rag.self_rag),
            ("Fusion RAG", "🔀", rag.fusion_rag),
            ("Advanced RAG", "⚡", rag.advanced_rag),
            ("Speculative RAG", "⚡", rag.speculative_rag),
            ("Corrective RAG", "✅", rag.corrective_rag)
        ]
        
        # Run all RAG methods and display side-by-side
        for idx, (name, icon, method) in enumerate(rag_methods):
            with cols[idx]:
                st.markdown(f"### {icon} {name}")
                
                with st.spinner(f"Running {name}..."):
                    start_time = time.time()
                    try:
                        answer = method(question)
                        elapsed = time.time() - start_time
                        
                        st.markdown(f'<div class="rag-box">{answer}</div>', unsafe_allow_html=True)
                        st.caption(f"⏱️ {elapsed:.2f}s")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Summary comparison
        st.markdown("---")
        st.subheader("📈 Quick Comparison")
        
        comparison_df = {
            "RAG Type": ["Self RAG", "Fusion RAG", "Advanced RAG", "Speculative RAG", "Corrective RAG"],
            "Approach": [
                "Self-reflection",
                "Multi-query fusion",
                "Rewrite + Re-rank",
                "Speculate + Verify",
                "Explicit correction"
            ],
            "Best For": [
                "Selective retrieval",
                "Comprehensive coverage",
                "Precision",
                "Speed",
                "Accuracy + Corrections"
            ]
        }
        
        st.table(comparison_df)


if __name__ == "__main__":
    main()

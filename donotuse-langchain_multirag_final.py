"""
Multi-RAG Comparison System with LangChain
Using the CORRECT LangChain packages (langchain-community, langchain-openai)
Based on working notebook setup
"""

import streamlit as st
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains.retrieval_qa.base import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_classic.chains import LLMChain
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()


class MultiRAGSystem:
    """Multi-RAG System using proper LangChain packages"""
    
    def __init__(self, api_key, model_name="gpt-3.5-turbo"):
        """Initialize with LangChain components"""
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            openai_api_key=api_key
        )
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        
        # Vector store
        self.vectorstore = None
    
    def add_documents(self, documents):
        """Add documents to vector store"""
        
        # Convert to LangChain Document format
        langchain_docs = []
        for doc in documents:
            langchain_docs.append(
                Document(
                    page_content=doc['text'],
                    metadata=doc['metadata']
                )
            )
        
        # Create ChromaDB vector store
        self.vectorstore = Chroma.from_documents(
            documents=langchain_docs,
            embedding=self.embeddings,
            collection_name="insurance_policies"
        )
        
        return len(documents)
    
    def self_rag(self, question):
        """Self RAG - Self-reflective retrieval"""
        
        # Step 1: Self-reflection - do we need retrieval?
        reflection_prompt = f"""Determine if you need to retrieve documents to answer this question.
Question: {question}

Respond with ONLY 'YES' or 'NO'.
If the question is about specific company policies, procedures, or facts: YES
If it's a general knowledge question: NO

Answer:"""
        
        reflection = self.llm.invoke(reflection_prompt).content.strip()
        
        if "YES" in reflection.upper():
            # Need retrieval - use RetrievalQA
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
            qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=retriever
            )
            answer = qa_chain.invoke({"query": question})['result']
            return f"🔄 Self-RAG: Retrieved documents\n\n{answer}"
        else:
            # No retrieval needed
            answer = self.llm.invoke(question).content
            return f"🔄 Self-RAG: No retrieval needed\n\n{answer}"
    
    def fusion_rag(self, question):
        """Fusion RAG - Multi-query fusion"""
        
        # Generate query variations
        variation_prompt = f"""Generate 2 variations of this question for better document retrieval.
Original: {question}

Variation 1:
Variation 2:"""
        
        variations = self.llm.invoke(variation_prompt).content.strip().split('\n')
        queries = [question] + [v.split(':', 1)[-1].strip() for v in variations if ':' in v][:2]
        
        # Retrieve for each query
        all_docs = []
        seen = set()
        
        for query in queries:
            retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
            docs = retriever.get_relevant_documents(query)
            for doc in docs:
                if doc.page_content not in seen:
                    all_docs.append(doc)
                    seen.add(doc.page_content)
        
        # Use fused results
        if all_docs:
            context = "\n\n".join([doc.page_content for doc in all_docs[:3]])
            
            prompt = f"""Context: {context}

Question: {question}

Answer:"""
            answer = self.llm.invoke(prompt).content
            return f"🔀 Fusion RAG: Used {len(queries)} query variations\n\n{answer}"
        else:
            return "🔀 Fusion RAG: No documents found"
    
    def advanced_rag(self, question):
        """Advanced RAG - Query rewriting + Re-ranking"""
        
        # Rewrite query
        rewrite_prompt = f"""Rewrite this question to be more specific for document search:
Original: {question}

Rewritten:"""
        
        rewritten = self.llm.invoke(rewrite_prompt).content.strip()
        
        # Retrieve with rewritten query
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever
        )
        
        answer = qa_chain.invoke({"query": rewritten})['result']
        return f"⚡ Advanced RAG: Rewritten query\nOriginal: {question}\nRewritten: {rewritten}\n\n{answer}"
    
    def speculative_rag(self, question):
        """Speculative RAG - Fast speculation + verification"""
        
        # Fast speculation
        spec_answer = self.llm.invoke(f"Quickly answer: {question}").content
        
        # Retrieve and verify
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2})
        docs = retriever.get_relevant_documents(question)
        
        if docs:
            context = "\n\n".join([doc.page_content for doc in docs])
            
            verify_prompt = f"""Speculative answer: {spec_answer}

Context from documents:
{context}

Question: {question}

Verify the speculative answer. If correct, return it. If wrong, provide corrected answer:"""
            
            final_answer = self.llm.invoke(verify_prompt).content
            return f"⚡ Speculative RAG: Generated then verified\n\n{final_answer}"
        else:
            return f"⚡ Speculative RAG: {spec_answer}"
    
    def corrective_rag(self, question):
        """Corrective RAG - Explicit correction of outdated info"""
        
        # Retrieve documents
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(question)
        
        if not docs:
            return "✅ Corrective RAG: No documents found"
        
        context = "\n\n---\n\n".join([
            f"Document: {doc.metadata.get('source', 'Unknown')}\n"
            f"Last Updated: {doc.metadata.get('last_updated', 'Unknown')}\n\n"
            f"{doc.page_content}"
            for doc in docs
        ])
        
        # Create corrective prompt
        prompt_template = PromptTemplate(
            template="""You are an HR assistant for TechCorp Inc.

CRITICAL INSTRUCTIONS:
1. Answer based ONLY on the context documents
2. If the user mentions outdated information (like "90-day waiting period"), CORRECT them explicitly
3. State what changed and when
4. Cite the document source and date

CONTEXT:
{context}

QUESTION: {question}

ANSWER (with corrections if needed):""",
            input_variables=["context", "question"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt_template)
        answer = chain.run(context=context, question=question)
        
        return f"✅ Corrective RAG: Explicit corrections\n\n{answer}"


def get_insurance_documents():
    """Sample insurance documents"""
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
        page_title="LangChain Multi-RAG",
        page_icon="🔗",
        layout="wide"
    )
    
    # CSS
    st.markdown("""
        <style>
        .main {background-color: #f8f9fa;}
        .stButton>button {
            background-color: #667eea;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px 28px;
        }
        .rag-box {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #667eea;
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
            <h1>🔗 LangChain Multi-RAG Comparison</h1>
            <p style="font-size: 18px; margin-bottom: 0;">
                Compare 5 RAG Approaches Using Real LangChain Framework
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
            st.success("✅ LangChain Ready")
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
            if st.button(q, key=f"q_{i}", use_container_width=True):
                st.session_state.question = q
        
        st.markdown("---")
        
        with st.expander("🔗 LangChain Packages Used"):
            st.code("""
langchain-community
langchain-openai
langchain-core
chromadb
            """)
    
    # Main area
    if not api_key:
        st.info("👈 Enter your OpenAI API key in the sidebar")
        return
    
    # Initialize
    if 'rag' not in st.session_state or not st.session_state.get('ready'):
        with st.spinner("🔧 Initializing LangChain RAG systems..."):
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
    st.header("Ask a Question")
    
    question = st.text_input(
        "Your question:",
        value=st.session_state.get('question', ''),
        placeholder="e.g., Is there a 90-day waiting period?",
        key="main_question"
    )
    
    col1, col2 = st.columns([1, 6])
    with col1:
        ask = st.button("🔬 Compare All", type="primary", use_container_width=True)
    with col2:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state.question = ""
            st.rerun()
    
    if ask and question:
        st.markdown("---")
        st.subheader("📊 5 RAG Approaches Side-by-Side")
        
        # Create 5 columns
        cols = st.columns(5)
        
        rag_methods = [
            ("Self RAG", "🔄", rag.self_rag),
            ("Fusion RAG", "🔀", rag.fusion_rag),
            ("Advanced RAG", "⚡", rag.advanced_rag),
            ("Speculative RAG", "⚡", rag.speculative_rag),
            ("Corrective RAG", "✅", rag.corrective_rag)
        ]
        
        # Run all RAG methods
        for idx, (name, icon, method) in enumerate(rag_methods):
            with cols[idx]:
                st.markdown(f"### {icon} {name}")
                
                with st.spinner(f"Running..."):
                    start_time = time.time()
                    try:
                        answer = method(question)
                        elapsed = time.time() - start_time
                        
                        st.markdown(f'<div class="rag-box">{answer}</div>', unsafe_allow_html=True)
                        st.caption(f"⏱️ {elapsed:.2f}s")
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Comparison table
        st.markdown("---")
        st.subheader("📈 Quick Comparison")
        
        comparison_data = {
            "RAG Type": ["Self RAG", "Fusion RAG", "Advanced RAG", "Speculative", "Corrective"],
            "Approach": ["Self-reflection", "Multi-query", "Rewrite+Rank", "Speculate+Verify", "Explicit correction"],
            "Best For": ["Efficiency", "Coverage", "Precision", "Speed", "Accuracy"]
        }
        
        st.table(comparison_data)


if __name__ == "__main__":
    main()

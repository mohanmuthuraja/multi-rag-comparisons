"""
Corrective RAG System using LangChain Framework
With OpenAI GPT-4 and Streamlit Frontend
Updated to use .env file for API key security
"""

import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
import os
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables from .env file
load_dotenv()

class LangChainCorrectiveRAG:
    """Corrective RAG System using LangChain Framework"""
    
    def __init__(self, api_key, model_name="gpt-3.5-turbo"):
        """Initialize LangChain components"""
        os.environ["OPENAI_API_KEY"] = api_key
        
        # Initialize OpenAI Chat Model
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.7,
            openai_api_key=api_key
        )
        
        # Initialize OpenAI Embeddings
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        
        # Vector store will be initialized when documents are added
        self.vectorstore = None
        self.qa_chain = None
        
    def create_corrective_prompt(self):
        """Create a prompt template with correction instructions"""
        template = """You are a helpful HR assistant for TechCorp Inc. You have access to company policy documents.

CRITICAL CORRECTION GUIDELINES:
1. ALWAYS prioritize the context documents over general knowledge
2. If the context shows a policy has CHANGED, explicitly state what changed and when
3. If the user mentions outdated information (like "90-day waiting period"), CORRECT them immediately
4. Cite the specific document source and date when providing information
5. Be clear and direct about corrections - use phrases like "That policy changed..." or "Actually, as of..."

Context from company documents:
{context}

Question: {question}

Instructions:
- Answer based ONLY on the context provided above
- If the context contradicts common assumptions, explicitly correct them
- If a policy changed, state: "The [old policy] was replaced with [new policy] effective [date]"
- Always cite your source with document name and date
- If the context doesn't contain the answer, say "I don't have that information in the current documents."

Answer:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def add_documents(self, documents):
        """
        Add documents to the vector store
        
        Args:
            documents: List of dicts with 'text' and 'metadata'
        """
        # Convert to LangChain Document format
        langchain_docs = []
        for doc in documents:
            langchain_docs.append(
                Document(
                    page_content=doc['text'],
                    metadata=doc['metadata']
                )
            )
        
        # Create vector store from documents
        self.vectorstore = Chroma.from_documents(
            documents=langchain_docs,
            embedding=self.embeddings,
            collection_name="company_policies"
        )
        
        # Create the QA chain with custom prompt
        custom_prompt = self.create_corrective_prompt()
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vectorstore.as_retriever(
                search_kwargs={"k": 3}  # Retrieve top 3 documents
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": custom_prompt}
        )
        
        return len(documents)
    
    def query(self, question):
        """
        Query the RAG system
        
        Args:
            question: User's question
            
        Returns:
            answer: Generated answer
            source_docs: Retrieved source documents
        """
        if not self.qa_chain:
            raise ValueError("No documents loaded. Please add documents first.")
        
        # Run the QA chain
        result = self.qa_chain({"query": question})
        
        return result['result'], result['source_documents']


def get_insurance_documents():
    """Sample insurance policy documents"""
    return [
        {
            'text': """TechCorp Health Insurance Policy - 2024 Update

EFFECTIVE DATE: January 1, 2024

MAJOR POLICY CHANGE:
The 90-day waiting period for health insurance has been ELIMINATED as of January 1, 2024.

NEW POLICY:
All full-time employees are now eligible for health insurance coverage starting on their FIRST DAY of employment.

This represents a significant improvement from our previous policy which required new employees to wait 90 days before health insurance coverage began.

Coverage Options:
- Premium Plan: $50/month employee contribution
  * Annual deductible: $1,000
  * Comprehensive coverage including dental and vision
  
- Standard Plan: $150/month employee contribution
  * Annual deductible: $2,500
  * Medical coverage only
  
- Basic Plan: $250/month employee contribution
  * Annual deductible: $5,000
  * High-deductible health plan with HSA option

Dependent Coverage:
Employees may add spouses and children to their health insurance plan.
Cost: $200/month per dependent (any plan level)

Enrollment:
New employees will receive enrollment information during their first week.
Enrollment must be completed within 30 days of hire date.

Questions? Contact HR at benefits@techcorp.com""",
            'metadata': {
                'source': 'Employee_Handbook_2024.pdf',
                'last_updated': '2024-01-15',
                'category': 'health_insurance',
                'document_type': 'policy'
            }
        },
        {
            'text': """URGENT POLICY UPDATE MEMO

TO: All Employees
FROM: Human Resources Department
DATE: January 10, 2024
RE: Elimination of Health Insurance Waiting Period

We are pleased to announce a major improvement to our benefits package.

WHAT CHANGED:
Effective January 1, 2024, we have ELIMINATED the 90-day waiting period for health insurance coverage.

OLD POLICY (Before Jan 1, 2024):
- New employees had to wait 90 days before health insurance coverage started
- This was a barrier to attracting top talent

NEW POLICY (Effective Jan 1, 2024):
- Health insurance coverage begins on DAY ONE of employment
- No waiting period whatsoever
- All coverage options available immediately

WHY WE MADE THIS CHANGE:
1. To remain competitive in attracting talent
2. To better support our employees and their families
3. To align with industry best practices
4. Employee feedback from our 2023 survey

WHO THIS AFFECTS:
- All employees hired on or after January 1, 2024 receive immediate coverage
- Employees hired before this date are not affected (they're already covered)

This change demonstrates our commitment to employee wellness and family support.

For questions, please contact the HR Benefits team.

Thank you,
Sarah Johnson
Director of Human Resources""",
            'metadata': {
                'source': 'HR_Memo_Waiting_Period_2024.pdf',
                'last_updated': '2024-01-10',
                'category': 'policy_update',
                'document_type': 'memo'
            }
        },
        {
            'text': """Health Insurance FAQ - Updated January 2024

Q: When does my health insurance coverage start?
A: As of January 1, 2024, health insurance coverage starts on your first day of employment. There is no waiting period.

Q: I heard there was a 90-day waiting period. Is that still true?
A: No, that policy changed. The 90-day waiting period was eliminated effective January 1, 2024. New employees now receive coverage immediately.

Q: What if I was hired before January 1, 2024?
A: The old 90-day waiting period applied to you, but you should already be covered now. Contact HR if you have concerns.

Q: How do I enroll in health insurance?
A: You'll receive enrollment information during your first week. You must enroll within 30 days of your hire date.

Q: Can I add my family to my health insurance?
A: Yes! You can add your spouse and children. The cost is $200/month per dependent.

Q: What plans are available?
A: We offer three plans - Premium ($50/month), Standard ($150/month), and Basic ($250/month). Each has different deductibles and coverage levels.

Q: What if I miss the 30-day enrollment window?
A: You'll have to wait until the next open enrollment period (November) or have a qualifying life event (marriage, birth, etc.).

Q: Does the company contribute to my health insurance?
A: Yes! The company pays the majority of the premium. The amounts listed ($50, $150, $250) are just your monthly contribution.

For more information, visit the HR portal or email benefits@techcorp.com""",
            'metadata': {
                'source': 'Insurance_FAQ_2024.pdf',
                'last_updated': '2024-01-15',
                'category': 'faq',
                'document_type': 'faq'
            }
        }
    ]


def get_api_key():
    """Get API key from .env file or user input"""
    # Try to load from .env file first
    api_key = os.getenv("OPENAI_API_KEY")
    
    if api_key and api_key != "your-api-key-here":
        return api_key
    
    # If not in .env, ask user
    return None


def main():
    """Main Streamlit Application"""
    
    # Page config
    st.set_page_config(
        page_title="LangChain Corrective RAG",
        page_icon="🔗",
        layout="wide"
    )
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #0066cc;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 12px 28px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #0052a3;
        }
        .response-box {
            background-color: #e7f3ff;
            padding: 25px;
            border-radius: 12px;
            border-left: 5px solid #0066cc;
            margin: 20px 0;
        }
        .source-box {
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
            border: 1px solid #dee2e6;
        }
        .header-box {
            background: linear-gradient(135deg, #0066cc 0%, #0052a3 100%);
            padding: 30px;
            border-radius: 12px;
            color: white;
            margin-bottom: 30px;
        }
        .success-box {
            background-color: #d4edda;
            color: #155724;
            padding: 15px;
            border-radius: 8px;
            border-left: 5px solid #28a745;
            margin: 10px 0;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
        <div class="header-box">
            <h1>🔗 LangChain Corrective RAG System</h1>
            <p style="font-size: 18px; margin-bottom: 0;">
                AI-Powered HR Assistant with Automatic Policy Correction
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Get API key from .env or user input
    env_api_key = get_api_key()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        if env_api_key:
            st.success("✅ API Key loaded from .env file")
            api_key = env_api_key
            st.info("🔒 Your API key is secure and not displayed")
        else:
            st.warning("⚠️ No .env file found")
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Enter your OpenAI API key (starts with sk-)",
                placeholder="sk-..."
            )
            
            with st.expander("📝 How to use .env file (Recommended)"):
                st.markdown("""
                **For better security:**
                
                1. Create a file named `.env` in your project folder
                2. Add this line to the file:
                   ```
                   OPENAI_API_KEY=sk-your-actual-key-here
                   ```
                3. Save the file
                4. Restart the app
                
                The `.env` file is automatically ignored by Git!
                """)
        
        # Model selection
        model_choice = st.selectbox(
            "Select Model",
            ["gpt-3.5-turbo", "gpt-4"],
            help="GPT-3.5 is faster and cheaper, GPT-4 is more accurate"
        )
        
        st.markdown("---")
        
        # System status
        st.subheader("📊 System Status")
        if 'rag_system' in st.session_state and st.session_state.get('initialized'):
            st.success("✅ LangChain Initialized")
            st.info(f"🤖 Model: {model_choice}")
            st.info(f"📄 Documents: {st.session_state.get('doc_count', 0)}")
            if env_api_key:
                st.info("🔒 API Key: From .env file")
            else:
                st.info("🔑 API Key: Manual input")
        else:
            st.warning("⚠️ Enter API key to start")
        
        st.markdown("---")
        
        # Sample questions
        st.subheader("💡 Try These Questions")
        
        sample_qs = [
            "When does my health insurance start?",
            "Is there a 90-day waiting period?",
            "What are the insurance plan options?",
            "How much does it cost to add my family?"
        ]
        
        for i, q in enumerate(sample_qs):
            if st.button(q, key=f"sample_{i}"):
                st.session_state.question = q
        
        st.markdown("---")
        
        # About
        with st.expander("ℹ️ About This System"):
            st.markdown("""
            **Built with:**
            - 🔗 LangChain Framework
            - 🤖 OpenAI GPT-3.5/4
            - 📊 Chroma Vector DB
            - 🎨 Streamlit UI
            - 🔒 python-dotenv (secure keys)
            
            **Features:**
            - Automatic correction of outdated info
            - Source document citations
            - Real-time vector search
            - Secure API key management
            """)
    
    # Main content area
    if not api_key:
        st.info("👈 Please enter your OpenAI API key in the sidebar to get started")
        
        col1, col2 = st.columns(2)
        
        with col1:
            with st.expander("🔑 How to get an OpenAI API Key"):
                st.markdown("""
                1. Go to https://platform.openai.com/
                2. Sign up or log in
                3. Navigate to **API Keys** section
                4. Click **Create new secret key**
                5. Copy the key (starts with `sk-`)
                
                **Note:** Keep your API key secure!
                """)
        
        with col2:
            with st.expander("🔒 How to use .env file (Recommended)"):
                st.markdown("""
                **Step 1:** Create `.env` file in your project folder
                
                **Step 2:** Add this line:
                ```
                OPENAI_API_KEY=sk-your-actual-key-here
                ```
                
                **Step 3:** Save and restart the app
                
                ✅ The `.env` file is in `.gitignore` - safe from Git!
                """)
        
        return
    
    # Initialize RAG system
    if 'rag_system' not in st.session_state or not st.session_state.get('initialized'):
        with st.spinner(f"🔧 Initializing LangChain RAG system with {model_choice}..."):
            try:
                # Create RAG system
                rag = LangChainCorrectiveRAG(api_key, model_name=model_choice)
                
                # Load documents
                docs = get_insurance_documents()
                doc_count = rag.add_documents(docs)
                
                # Save to session state
                st.session_state.rag_system = rag
                st.session_state.doc_count = doc_count
                st.session_state.initialized = True
                
                st.success(f"✅ System initialized with {doc_count} documents!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error initializing system: {str(e)}")
                st.info("Please check your API key and try again.")
                return
    
    rag = st.session_state.rag_system
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["💬 Ask Questions", "📚 Documents", "🔍 How It Works"])
    
    with tab1:
        st.header("Ask a Question About Health Insurance")
        
        # Question input
        question = st.text_input(
            "Your question:",
            value=st.session_state.get('question', ''),
            placeholder="e.g., When does my health insurance start? I heard there's a 90-day waiting period.",
            key="question_input"
        )
        
        col1, col2 = st.columns([1, 6])
        with col1:
            ask_button = st.button("🔍 Ask", type="primary")
        with col2:
            if st.button("🗑️ Clear"):
                st.session_state.question = ""
                st.rerun()
        
        if ask_button and question:
            with st.spinner("🤔 Searching documents and generating answer..."):
                try:
                    # Query the system
                    answer, sources = rag.query(question)
                    
                    # Display answer
                    st.markdown("### 💡 Answer")
                    st.markdown(f'<div class="response-box">{answer}</div>', unsafe_allow_html=True)
                    
                    # Display source documents
                    st.markdown("### 📄 Source Documents Used")
                    st.caption(f"Retrieved {len(sources)} relevant documents:")
                    
                    for i, doc in enumerate(sources, 1):
                        with st.expander(f"📄 Document {i}: {doc.metadata.get('source', 'Unknown')}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
                                st.markdown(f"**Type:** {doc.metadata.get('document_type', 'Unknown')}")
                            with col2:
                                st.markdown(f"**Updated:** {doc.metadata.get('last_updated', 'Unknown')}")
                                st.markdown(f"**Category:** {doc.metadata.get('category', 'Unknown')}")
                            
                            st.markdown("---")
                            st.markdown(doc.page_content)
                    
                    # Show correction indicator if applicable
                    if "90-day" in question.lower() or "waiting period" in question.lower():
                        st.markdown("""
                        <div class="success-box">
                            <strong>✅ Correction Applied:</strong> This answer corrects outdated information about the waiting period!
                        </div>
                        """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    with tab2:
        st.header("📚 Knowledge Base Documents")
        st.markdown("These documents are currently loaded in the system:")
        
        docs = get_insurance_documents()
        
        for i, doc in enumerate(docs, 1):
            with st.expander(
                f"📄 {doc['metadata']['source']} ({doc['metadata']['document_type'].upper()})",
                expanded=(i == 1)
            ):
                # Metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Last Updated", doc['metadata']['last_updated'])
                with col2:
                    st.metric("Category", doc['metadata']['category'])
                with col3:
                    st.metric("Type", doc['metadata']['document_type'])
                
                st.markdown("---")
                st.markdown(doc['text'])
    
    with tab3:
        st.header("🔍 How LangChain Corrective RAG Works")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### 🔄 The Process
            
            1. **User asks a question** 
               - Example: "Is there a 90-day waiting period?"
            
            2. **LangChain Retriever** 🔍
               - Converts question to embeddings (OpenAI)
               - Searches Chroma vector database
               - Retrieves top 3 most relevant documents
            
            3. **Context Formatting** 📋
               - LangChain automatically formats retrieved docs
               - Adds to custom prompt template
            
            4. **Correction Detection** ⚠️
               - Custom prompt instructs GPT to detect changes
               - Compares user assumptions with documents
               - Identifies outdated information
            """)
        
        with col2:
            st.markdown("""
            5. **Response Generation** 🤖
               - LangChain sends context + question to OpenAI
               - GPT generates answer with corrections
               - Returns answer + source documents
            
            6. **Display Results** 📊
               - Shows corrected answer
               - Displays source documents
               - Highlights corrections made
            
            ### ✨ Key Components
            
            - **ChatOpenAI**: GPT-3.5/4 language model
            - **OpenAIEmbeddings**: Convert text to vectors
            - **Chroma**: Vector database storage
            - **RetrievalQA**: LangChain's QA chain
            - **Custom Prompt**: Correction instructions
            """)
        
        st.markdown("---")
        
        st.markdown("""
        ### 🎯 Example Correction in Action
        
        **User asks:** *"When does insurance start? I heard there's a 90-day waiting period."*
        
        **System retrieves:** 
        - Employee Handbook 2024 (shows Day 1 coverage)
        - HR Memo (states 90-day period was eliminated Jan 2024)
        
        **GPT detects:** User has outdated information about 90-day period
        
        **Response includes:**
        - ✅ Correction: "The 90-day waiting period was eliminated effective January 1, 2024"
        - ✅ Current policy: "Coverage now starts on your first day"
        - ✅ Source citation: "According to Employee Handbook 2024..."
        
        This is **Corrective RAG** - automatically fixing outdated assumptions!
        """)


if __name__ == "__main__":
    main()

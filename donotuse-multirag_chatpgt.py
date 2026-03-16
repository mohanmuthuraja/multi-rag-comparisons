import streamlit as st
import os
import time
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_classic.chains import LLMChain

load_dotenv()


class MultiRAG:

    def __init__(self, api_key, model="gpt-3.5-turbo"):
        os.environ["OPENAI_API_KEY"] = api_key

        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7
        )

        self.embeddings = OpenAIEmbeddings()

        self.vectorstore = None


    # -------------------------------
    # Load Documents
    # -------------------------------

    def load_documents(self, docs):

        lang_docs = []

        for d in docs:
            lang_docs.append(
                Document(
                    page_content=d["text"],
                    metadata=d["metadata"]
                )
            )

        self.vectorstore = Chroma.from_documents(
            documents=lang_docs,
            embedding=self.embeddings
        )


    # -------------------------------
    # Helper Retriever
    # -------------------------------

    def retrieve(self, query, k=3):

        retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": k}
        )

        docs = retriever.invoke(query)

        return docs


    # -------------------------------
    # Self RAG
    # -------------------------------

    def self_rag(self, question):

        reflection = self.llm.invoke(
            f"Do we need documents to answer: {question}? Answer YES or NO."
        ).content

        if "YES" in reflection:

            docs = self.retrieve(question, 2)

            context = "\n\n".join([d.page_content for d in docs])

            answer = self.llm.invoke(
                f"Context:\n{context}\n\nQuestion:{question}\nAnswer:"
            ).content

            return "🔄 Retrieved docs\n\n" + answer

        else:

            return self.llm.invoke(question).content


    # -------------------------------
    # Fusion RAG
    # -------------------------------

    def fusion_rag(self, question):

        query_variations = self.llm.invoke(
            f"Generate 2 alternative search queries for: {question}"
        ).content.split("\n")

        queries = [question] + query_variations[:2]

        all_docs = []
        seen = set()

        for q in queries:

            docs = self.retrieve(q, 2)

            for d in docs:

                if d.page_content not in seen:
                    all_docs.append(d)
                    seen.add(d.page_content)

        context = "\n\n".join([d.page_content for d in all_docs[:3]])

        answer = self.llm.invoke(
            f"Context:\n{context}\n\nQuestion:{question}\nAnswer:"
        ).content

        return f"🔀 Used {len(queries)} queries\n\n{answer}"


    # -------------------------------
    # Advanced RAG
    # -------------------------------

    def advanced_rag(self, question):

        rewritten = self.llm.invoke(
            f"Rewrite this question for better document retrieval:\n{question}"
        ).content

        docs = self.retrieve(rewritten, 3)

        context = "\n\n".join([d.page_content for d in docs])

        answer = self.llm.invoke(
            f"Context:\n{context}\n\nQuestion:{question}\nAnswer:"
        ).content

        return f"⚡ Rewritten Query: {rewritten}\n\n{answer}"


    # -------------------------------
    # Speculative RAG
    # -------------------------------

    def speculative_rag(self, question):

        speculative = self.llm.invoke(
            f"Quick answer: {question}"
        ).content

        docs = self.retrieve(question, 3)

        context = "\n\n".join([d.page_content for d in docs])

        verified = self.llm.invoke(
            f"""Speculative Answer: {speculative}

Context:
{context}

Verify and correct if needed."""
        ).content

        return "⚡ Speculate → Verify\n\n" + verified


    # -------------------------------
    # Corrective RAG
    # -------------------------------

    def corrective_rag(self, question):

        docs = self.retrieve(question, 3)

        context = "\n\n".join([
            f"{d.metadata.get('source')} ({d.metadata.get('last_updated')})\n{d.page_content}"
            for d in docs
        ])

        prompt = PromptTemplate(
            template="""
You are an HR assistant.

Context:
{context}

Question:
{question}

If user assumption is outdated, correct them explicitly.

Answer:
""",
            input_variables=["context", "question"]
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)

        answer = chain.run(context=context, question=question)

        return "✅ Corrective RAG\n\n" + answer


# -----------------------------------
# Sample Documents
# -----------------------------------

def sample_docs():

    return [

        {
            "text": "The 90-day waiting period was removed in 2024. Insurance now starts on day one.",
            "metadata": {
                "source": "Employee Handbook",
                "last_updated": "2024"
            }
        },

        {
            "text": "Employees can choose Premium, Standard or Basic plans.",
            "metadata": {
                "source": "Benefits Guide",
                "last_updated": "2024"
            }
        }

    ]


# -----------------------------------
# Streamlit UI
# -----------------------------------

def main():

    st.title("🔬 Multi RAG Comparison")

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        st.warning("Add OPENAI_API_KEY in .env")
        return

    if "rag" not in st.session_state:

        rag = MultiRAG(api_key)

        rag.load_documents(sample_docs())

        st.session_state.rag = rag


    rag = st.session_state.rag

    question = st.text_input("Ask a question")

    if st.button("Run All RAGs") and question:

        cols = st.columns(5)

        methods = [
            ("Self", rag.self_rag),
            ("Fusion", rag.fusion_rag),
            ("Advanced", rag.advanced_rag),
            ("Speculative", rag.speculative_rag),
            ("Corrective", rag.corrective_rag)
        ]

        for i, (name, method) in enumerate(methods):

            with cols[i]:

                st.subheader(name)

                start = time.time()

                try:
                    ans = method(question)
                    st.write(ans)

                except Exception as e:
                    st.error(e)

                st.caption(f"{time.time()-start:.2f}s")


if __name__ == "__main__":
    main()
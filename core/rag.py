import os
from langchain_classic.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langchain_classic.chains import RetrievalQA
from langchain_classic.schema import Document
from langchain_classic.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# Load dokumen TXT
docs_folder = "docs"
docs = []
for file_name in os.listdir(docs_folder):
    if file_name.endswith(".txt"):
        with open(os.path.join(docs_folder, file_name), "r", encoding="utf-8") as f:
            content = f.read()
            docs.append(Document(page_content=content))

splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = splitter.split_documents(docs)
text_chunks = [doc.page_content for doc in texts]

embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectordb = Chroma.from_texts(text_chunks, embedding=embedding_model)
retriever = vectordb.as_retriever()

rag_prompt_template = PromptTemplate(
    input_variables=["context", "question"],
    template="""Kamu adalah asisten Persib Bandung yang ramah dan helpful.
Gunakan konteks berikut untuk menjawab pertanyaan user.
Jawab selalu dalam Bahasa Indonesia, singkat, dan natural.
Jika informasi tidak ada di konteks, katakan dengan jujur bahwa kamu tidak tahu.

Konteks:
{context}

Pertanyaan: {question}
Jawaban:"""
)

HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Pakai task="conversational" sesuai yang disupport provider
llm_endpoint = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    huggingfacehub_api_token=HUGGINGFACEHUB_API_TOKEN,
    temperature=0.7,
    max_new_tokens=512,
    task="conversational",
)

# Wrap dengan ChatHuggingFace agar bisa dipakai di chain
llm = ChatHuggingFace(llm=llm_endpoint)

rag_qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    chain_type_kwargs={"prompt": rag_prompt_template}
)
from dotenv import load_dotenv
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters.character import CharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import os

# Load environment variables
load_dotenv()

working_dir = os.getcwd()

def load_documents(file_path):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    return documents

def setup_vectorstore(documents):
    embeddings = HuggingFaceEmbeddings()
    text_splitter = CharacterTextSplitter(
        separator="/n",
        chunk_size=1000,
        chunk_overlap=200
    )
    doc_chunks = text_splitter.split_documents(documents)
    vectorstores = FAISS.from_documents(doc_chunks, embeddings)
    return vectorstores

def create_chain(vectorstores):
    llm = ChatGroq(
        model="llama-3.1-70b-versatile",
        temperature=0
    )
    retriever = vectorstores.as_retriever()
    memory = ConversationBufferMemory(
        llm=llm,
        output_key="answer",
        memory_key="chat_history",
        return_messages=True
    )
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        verbose=True
    )
    return chain

st.set_page_config(
    page_title="Chat with your documents",
    page_icon="📑",
    layout="centered"
)

st.title("📝Chat With your docs 😎")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

uploaded_file = st.file_uploader(label="Upload your PDF")

if uploaded_file:
    file_path = f"{working_dir}{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if "vectorstores" not in st.session_state:
        st.session_state.vectorstores = setup_vectorstore(load_documents(file_path))

    if "conversation_chain" not in st.session_state:
        st.session_state.conversation_chain = create_chain(st.session_state.vectorstores)

for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask any questions relevant to uploaded pdf")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = st.session_state.conversation_chain({"question": user_input})
        assistant_response = response["answer"]
        st.markdown(assistant_response)
        st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

# from langchain_groq import ChatGroq
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters.character import CharacterTextSplitter, RecursiveCharacterTextSplitter
# from langchain_community.vectorstores import FAISS
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ConversationBufferMemory
# import streamlit as st
# import time

# class Chatbot:
#     def __init__(self, conn, session_id:str):
#         options = st.session_state.session_options
#         self.language = options['language']
#         self.model = options['model']
#         self.temperature = options['temperature']
#         self.max_tokens = options['max_tokens']
#         self.conn = conn
#         self.session_id = session_id

#     def get_prompt(self) -> ChatPromptTemplate:
#         template = """
#         You are a highly qualified and versatile virtual assistant, capable of providing support in various areas of my daily life, and your name is 'Kronos'. Your goal is to be efficient, clear, and useful, providing responses adapted to the context of each request.

#         Your competencies include:
#         * Task Management and Productivity: Organize my daily and weekly activities in an effective manner. Prioritize tasks according to urgency and importance, suggest rest intervals, and offer strategies to increase my productivity.
#         * Technical Support: Solve technical problems with electronic devices, networks, and software. Ask diagnostic questions to better understand the problem and provide clear, step-by-step instructions to resolve it.
#         * Research and Information Provision: Conduct in-depth research on complex topics (e.g., climate change, technological advancements, historical events) and summarize the information in a precise and accessible manner. Provide reliable sources and organize the content to facilitate understanding.
#         * Tutoring and Education: Explain academic and technical concepts in a clear manner, such as mathematics, programming, or science, adapting the level of detail to my knowledge. Offer practical examples and simplified methods to facilitate learning.
#         * Creativity and Idea Generation: Contribute creative suggestions, such as names for projects or companies, development of synopses for books or films, or brainstorming for advertising campaigns. Base your suggestions on keywords or themes I provide.
#         * Financial Consulting: Assist in creating and managing a monthly budget based on my expenses and income. Provide tips on saving, cutting unnecessary expenses, and increasing investments to achieve short-term and long-term goals.

#         I will always respond in a clear, objective, and precise manner, asking additional questions when necessary to better understand the context and provide a more accurate help.
#         I will adapt my tone according to the subject, being technical, friendly, or formal as needed.

#         Your human is called 'João' and you need to answer all the questions in {language}.

#         Chat history: {chat_history}

#         Question: {question}

#         Output:"""

#         return ChatPromptTemplate.from_template(template)

#     def load_documents(self, file_path):
#         try:
#             loader = PyPDFLoader(file_path)
#             documents = loader.load()

#             embeddings = HuggingFaceEmbeddings()
#             text_splitter = RecursiveCharacterTextSplitter( chunk_size=1000, chunk_overlap=200 )
#             docs = text_splitter.split_documents(documents)
#             vectorstores = FAISS.from_documents(docs, embeddings)
#         except Exception as e:
#             raise e

#         return vectorstores.as_retriever()

#     def create_chain(self, vectorstores=None):
#         try:
#             llm = ChatGroq(model=self.model, temperature=self.temperature, max_tokens=self.max_tokens, streaming=True)

#             if vectorstores:

#                 memory = ConversationBufferMemory(
#                         chat_memory=self.conn,
#                         llm=llm,
#                         input_key='question',
#                         memory_key="chat_history",
#                         return_messages=True
#                     )

#                 chain = ConversationalRetrievalChain.from_llm(
#                     llm=llm,
#                     retriever=vectorstores,
#                     memory=memory,
#                     verbose=True
#                 )

#             else:

#                 base_chain = self.get_prompt() | llm | StrOutputParser()
#                 chain = RunnableWithMessageHistory(
#                     base_chain,
#                     lambda session_id: self.conn,
#                     input_messages_key='question',
#                     history_messages_key="chat_history"
#                 )

#         except Exception as e:
#             raise e

#         return chain

#     def bot_response(self, prompt:str, file=None):

#         if file is not None:
#             with st.spinner("Processando o arquivo..."):
#                 vectorstore = self.load_documents(file)
#                 chain = self.create_chain(vectorstore)

#                 response = chain.stream( {
#                             "question": prompt,
#                             "language": self.language
#                         } , config={"configurable": {"session_id": self.session_id } } )

#                 response_container = st.chat_message("assistant")
#                 response_text = response_container.empty()
#                 full_response = ''

#                 for content in response:
#                     full_response += content["answer"]
#                     response_text.markdown(full_response + "█ ")
#                     time.sleep(0.02)

#                 response_text.markdown(full_response)

#         else:
#             chain = self.create_chain()

#             response = chain.stream( {
#                         "question": prompt,
#                         "language": self.language
#                     } , config={"configurable": {"session_id": self.session_id } } )

#             response_container = st.chat_message("assistant")
#             response_text = response_container.empty()
#             full_response = ''

#             for content in response:
#                 full_response += content
#                 response_text.markdown(full_response + "█ ")
#                 time.sleep(0.02)

#             response_text.markdown(full_response)

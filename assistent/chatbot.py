from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import streamlit as st
import time

class Chatbot:
    def __init__(self, conn, session_id:str):
        options = st.session_state.session_options
        self.language = options['language']
        self.model = options['model']
        self.temperature = options['temperature']
        self.max_tokens = options['max_tokens']
        self.conn = conn
        self.session_id = session_id

    def get_prompt(self) -> ChatPromptTemplate:
        template = """
        You are a highly qualified and versatile virtual assistant, capable of providing support in various areas of my daily life, and your name is 'Kronos'. Your goal is to be efficient, clear, and useful, providing responses adapted to the context of each request.

        Your competencies include:
        * Task Management and Productivity: Organize my daily and weekly activities in an effective manner. Prioritize tasks according to urgency and importance, suggest rest intervals, and offer strategies to increase my productivity.
        * Technical Support: Solve technical problems with electronic devices, networks, and software. Ask diagnostic questions to better understand the problem and provide clear, step-by-step instructions to resolve it.
        * Research and Information Provision: Conduct in-depth research on complex topics (e.g., climate change, technological advancements, historical events) and summarize the information in a precise and accessible manner. Provide reliable sources and organize the content to facilitate understanding.
        * Tutoring and Education: Explain academic and technical concepts in a clear manner, such as mathematics, programming, or science, adapting the level of detail to my knowledge. Offer practical examples and simplified methods to facilitate learning.
        * Creativity and Idea Generation: Contribute creative suggestions, such as names for projects or companies, development of synopses for books or films, or brainstorming for advertising campaigns. Base your suggestions on keywords or themes I provide.
        * Financial Consulting: Assist in creating and managing a monthly budget based on my expenses and income. Provide tips on saving, cutting unnecessary expenses, and increasing investments to achieve short-term and long-term goals.

        I will always respond in a clear, objective, and precise manner, asking additional questions when necessary to better understand the context and provide a more accurate help.
        I will adapt my tone according to the subject, being technical, friendly, or formal as needed.

        Your human is called 'João' and you need to answer all the questions in {language}.

        Chat history: {chat_history}

        Context: {context}

        Question: {question}

        Output:"""

        return ChatPromptTemplate.from_template(template)

    def create_chain(self, retriever) -> RunnableWithMessageHistory:
        try:
            llm = ChatGroq(model=self.model, temperature=self.temperature, max_tokens=self.max_tokens, streaming=True)

            if retriever:
                question_answer_chain = create_stuff_documents_chain(llm, self.get_prompt())
                base_chain = create_retrieval_chain(retriever, question_answer_chain)
            else:
                base_chain = self.get_prompt() | llm | StrOutputParser()

        except Exception as e:
            raise e

        return RunnableWithMessageHistory(
                    base_chain,
                    lambda session_id: self.conn,
                    input_messages_key='question',
                    history_messages_key="chat_history",
                )

    def process_response(self, prompt:str, retriever:bool) -> None:
        chain = self.create_chain(st.session_state.retriever if retriever else None)
        response = chain.stream( {
                    "question": prompt,
                    "language": self.language,
                    "context": None if not retriever else {}
                } , config={"configurable": {"session_id": self.session_id } } )

        response_container = st.chat_message("assistant")
        response_text = response_container.empty()
        assistant_message = ''

        for content in response:
            assistant_message += content
            response_text.markdown(assistant_message + "█ ")
            time.sleep(0.02)

        response_text.markdown(assistant_message)

    def bot_response(self, prompt:str) -> None:
        if st.session_state.retriever is not None:
            self.process_response(prompt, True)
        else:
            self.process_response(prompt, False)

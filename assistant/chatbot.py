from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from utils import *
import streamlit as st
import time

class Chatbot:
    def __init__(self):
        options = st.session_state.session_options
        self.conn = st.session_state.db_connection
        self.language = options['language']
        self.model = options['model']
        self.developer = options['developer']
        self.temperature = options['temperature']
        self.max_tokens = options['max_tokens']
        self.session_id = st.session_state.session_id
        self.llm = ChatGroq(model=self.model, temperature=self.temperature, max_tokens=self.max_tokens, streaming=True)

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

        Input: {input}

        Output:"""

        return ChatPromptTemplate.from_template(template)

    def get_qa_prompt(self) -> ChatPromptTemplate:
        template = """
            You are an assistant for question-answering tasks.
            Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know.
            Use three sentences maximum and keep the answer concise.
            Your human is called 'João' and you need to answer all the questions in {language}.

            Chat history: {chat_history}

            Context: {context}

            Input: {input}

            Output:"""

        return ChatPromptTemplate.from_template(template)

    def create_chain_qa(self) -> RunnableWithMessageHistory:
        try:
            question_answer_chain = create_stuff_documents_chain(self.llm, self.get_qa_prompt())
            base_chain = create_retrieval_chain(st.session_state.retriever, question_answer_chain)
        except Exception as e:
            raise e

        return RunnableWithMessageHistory(
                    base_chain,
                    lambda session_id: self.conn,
                    input_messages_key='input',
                    history_messages_key="chat_history",
                    output_messages_key='answer',
                )

    def process_reponse_qa(self, prompt:str) -> None:
        chain = self.create_chain_qa()

        if 'DeepSeek' in self.developer:
            with st.spinner("☁️ Thinking..."):
                response = chain.invoke( {
                    "input": prompt,
                    "language": self.language,
                } , config={"configurable": {"session_id": self.session_id } } )


                thinking_process, final_response = thinkins_processing(response, 'rag')

                if st.session_state.thinking_mode:
                    if thinking_process:
                        with st.expander("🤔 Veja o processo de pensamento"):
                            st.markdown(thinking_process)

            response_container = st.chat_message("assistant")
            response_text = response_container.empty()
            assistant_message = ''

            for content in final_response:
                assistant_message += (content + ' ')
                response_text.markdown(assistant_message + "█ ")
                time.sleep(0.02)

            response_text.markdown(assistant_message)

        else:
            response = chain.stream( {
                    "input": prompt,
                    "language": self.language,
                } , config={"configurable": {"session_id": self.session_id } } )

            response_container = st.chat_message("assistant")
            response_text = response_container.empty()
            assistant_message = ''

            for content in response:
                if 'answer' in content:
                    assistant_message += str(content['answer'])

                response_text.markdown(assistant_message + "█ ")
                time.sleep(0.02)

            response_text.markdown(assistant_message)


    def create_chain(self) -> RunnableWithMessageHistory:
        try:
            base_chain = self.get_prompt() | self.llm | StrOutputParser()
        except Exception as e:
            raise e
        return RunnableWithMessageHistory(
                    base_chain,
                    lambda session_id: self.conn,
                    input_messages_key='input',
                    history_messages_key="chat_history",
                )

    def process_reponse(self, prompt:str) -> None:
        chain = self.create_chain()

        if 'DeepSeek' in self.developer:
            with st.spinner("☁️ Thinking..."):
                response = chain.invoke( {
                            "input": prompt,
                            "language": self.language,
                            "context": None
                        } , config={"configurable": {"session_id": self.session_id } } )

                thinking_process, final_response = thinkins_processing(response)

                if st.session_state.thinking_mode:
                    if thinking_process:
                        with st.expander("🤔 Veja o processo de pensamento"):
                            st.markdown(thinking_process)

            response_container = st.chat_message("assistant")
            response_text = response_container.empty()
            assistant_message = ''

            for content in final_response:
                assistant_message += (content + ' ')
                response_text.markdown(assistant_message + "█ ")
                time.sleep(0.02)

            response_text.markdown(assistant_message)

        else:
            response = chain.stream( {
                        "input": prompt,
                        "language": self.language,
                        "context": None
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
            self.process_reponse_qa(prompt)
        else:
            self.process_reponse(prompt)

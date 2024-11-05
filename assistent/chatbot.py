from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
import streamlit as st
import time

class Chatbot:
    def __init__(self, conn, session_id:str):
        self.msgs = conn
        self.session_id = session_id

        options = st.session_state.session_options
        self.language = options['language']
        self.model = options['model']
        self.temperature = options['temperature']
        self.max_tokens = options['max_tokens']

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

        Question: {question}

        Output:"""

        return ChatPromptTemplate.from_template(template)

    def get_chain(self):
        try:
            model = ChatGroq(model=self.model, temperature=self.temperature, max_tokens=self.max_tokens)
            chain = self.get_prompt() | model | StrOutputParser()

        except Exception as e:
            raise e

        return  RunnableWithMessageHistory(
                chain,
                lambda session_id: self.msgs,
                input_messages_key='question',
                history_messages_key="chat_history")

    def bot_response(self, prompt:str):
        chain = self.get_chain()

        response = chain.stream( {
                    "question": [HumanMessage(content=prompt)],
                    "language": self.language
                },
                config={"configurable": {"session_id": self.session_id } }
        )

        response_container = st.chat_message("assistant")
        response_text = response_container.empty()
        full_response = ''

        for response in response:
            full_response += response
            response_text.markdown(full_response + "█ ")
            time.sleep(0.02)

        response_text.markdown(full_response)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader,CSVLoader
from chatdb_test import ChatDbMessages
from chatbot_test import Chatbot
from utils_test import *
import re

class Document:
    # Function to clean the text
    def __clean_text__(self, text):
        cleaned_text = text.strip()  # Remove leading/trailing whitespace
        cleaned_text = re.sub(r"\s+", " ", cleaned_text)  # Replace extra spaces with a single space
        cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)  # Remove non-alphanumeric characters
        return cleaned_text

    @property
    def load(self):
        try:

            if st.session_state.file_type == 'pdf':
                loader = PyPDFLoader(st.session_state.uploaded_file)
            else:
                loader = CSVLoader(st.session_state.uploaded_file)

            documents =  loader.load()
            for doc in documents:
                cleaned = self.__clean_text__(doc.page_content)
                doc.page_content = cleaned

            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
            vectorstores = FAISS.from_documents(documents, embeddings)

        except Exception as e:
            raise e

        return vectorstores.as_retriever()


class App:
    def __init__(self, session_id:str, conn:ChatDbMessages):
        self.session_id = session_id
        self.conn = conn

    def create_session_button(self, session_id, options, label):
        # Verifica se a sessão é ativa para desabilitar o botão correspondente
        disabled = (st.session_state.get("session_id") == session_id)
        st.button(
            label=label,
            key=f"btn-{session_id}",
            on_click=update_session,
            args=(session_id, options,),
            disabled=disabled,
            use_container_width=True
        )

    def display_previous_sessions(self):
        try:
            sessions = self.conn.get_previus_sessions()  # Obtem IDs das sessões
            sessions_ord = set_timestamp_session(sessions)  # Ordena por timestamp

            for session_data in sessions_ord:
                session_id = session_data['session_id']
                result = self.conn.get_message_history(session_id=session_id)
                options = self.conn.get_previus_sessions_options(session_id=session_id)

                if result:
                    label = mask_text(result[0].content)
                    self.create_session_button(session_id, options, label)

        except Exception as e:
            raise e

    def sidebar_options(self) -> str:

        settings = get_default_settings(self.conn.messages)

        with st.sidebar:
            with st.popover('Configurações', icon='⚙️', use_container_width=True):
                language_option = st.selectbox("Idioma", options=settings["language_options"], key=f'lang-{self.session_id}', disabled=settings["disabled"])
                selected_model = st.selectbox("Modelo", options=list(settings["model_options"].keys()), key=f'model-{self.session_id}', disabled=settings["disabled"])
                temperature = st.slider('Temperatura', 0.0, 2.0, settings["temperature_default"], key=f'temp-{self.session_id}', disabled=settings["disabled"])
                max_tokens = st.slider('Max Tokens', 0, settings["model_options"][selected_model]["tokens"], settings["max_token_default"], key=f'tokens-{self.session_id}', disabled=settings["disabled"])
                uploaded_file = st.file_uploader('Adicionar Arquivo', key=f"file-{self.session_id}", disabled=settings["disabled"], type=['csv','pdf'])

            st.button('Nova Conversa', icon="➕", on_click=start_new_session, use_container_width=True)
            st.button("Deletar Conversa", icon="❌", on_click=self.conn.clear, use_container_width=True)

            st.session_state.session_options = {
                'language': language_option,
                'model': selected_model,
                'max_tokens': max_tokens,
                'temperature': temperature
            }

            st.markdown('###')
            st.subheader('Recentes', divider='gray')
            self.display_previous_sessions()

            if uploaded_file:

                file_path = f"/tmp/{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                if st.session_state.uploaded_file is None or st.session_state.file_type is None:
                    st.session_state.uploaded_file = file_path
                    st.session_state.file_type = uploaded_file.type.split('/')[1]

                if st.session_state.retriever is None :
                    st.session_state.retriever = Document().load

def main():
    try:
        st.set_page_config(page_title='AI Chatbot', page_icon='💬')
        st.markdown('<h1><img src="https://img.icons8.com/fluency/50/chatbot--v1.png" alt="Kronos - AI Assistant" style="vertical-align: middle;padding: 0 0 5px 0 ;"> Kronos - AI Assistant</h1>', unsafe_allow_html=True)
        st.header("", divider='rainbow', anchor=False)

        session_id = init_sessions()
        conn = ChatDbMessages()

        app = App(session_id, conn)
        app.sidebar_options()

        bot = Chatbot(conn, session_id)

        for msg in conn.messages:
            st.chat_message(msg.type).write(msg.content)

        if prompt := st.chat_input():
            st.chat_message('human').write(prompt)
            bot.bot_response(prompt)

    except Exception as e:
        raise e

if __name__=="__main__":
    main()

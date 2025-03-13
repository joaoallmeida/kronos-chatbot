from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders.parsers import RapidOCRBlobParser
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_qdrant.vectorstores import Qdrant
from chatdb_test import ChatDbMessages
from chatbot_test import Chatbot
from utils_test import *
import re

class Document:

    def load(self, file):
        try:

            file_path = f"/tmp/{file.name}"
            file_type = file.type.split('/')[1]

            with st.spinner(f'Processando Arquivo: {file.name}...'):
                with open(file_path, "wb") as f:
                    f.write(file.getbuffer())

                loader = PyPDFLoader(
                    file_path,
                    mode='page',
                    extract_images=True,
                    images_inner_format="text",
                    images_parser=RapidOCRBlobParser()
                )
                documents =  loader.load()

                # Add source metadata
                for doc in documents:
                    doc.metadata.update({
                        "source_type": file_type,
                        "file_name": file.name,
                        "timestamp": datetime.now().isoformat()
                    })

                text_splitter = RecursiveCharacterTextSplitter( chunk_size=2048, chunk_overlap=128 )
                docs = text_splitter.split_documents(documents)

                embeddings = FastEmbedEmbeddings(model_name="BAAI/bge-base-en-v1.5")
                vector_stores = Qdrant.from_documents(docs, embeddings, location=":memory:", collection_name="document_embeddings")

                st.success(f"Arquivo processado", icon='✅')

        except Exception as e:
            raise e

        return vector_stores.as_retriever(search_type="mmr", search_kwargs={"k": 5})


class App:
    def __init__(self):
        self.session_id = st.session_state.session_id
        self.conn = st.session_state.db_connection
        self.options()

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

    def options(self) -> str:

        uploaded_file = False
        settings = get_default_settings(self.conn.messages)

        with st.sidebar:

            st.button('Nova Conversa', icon="➕", on_click=start_new_session, use_container_width=True)
            if st.button("Deletar Conversa", icon="❌", on_click=self.conn.clear, use_container_width=True):
                st.rerun()

            with st.popover('Configurações', icon='⚙️', use_container_width=True):
                language_option = st.selectbox("Idioma", options=settings["language_options"], key=f'lang-{self.session_id}', disabled=settings["disabled"])
                selected_model = st.selectbox("Modelo", options=sorted(list(settings["model_options"].keys())), key=f'model-{self.session_id}', disabled=settings["disabled"])
                temperature = st.slider('Temperatura', 0.0, 2.0, settings["temperature_default"], key=f'temp-{self.session_id}', disabled=settings["disabled"])
                max_tokens = st.slider('Max Tokens', 0, settings["model_options"][selected_model]["tokens"], settings["max_token_default"], key=f'tokens-{self.session_id}', disabled=settings["disabled"])
                st.session_state.rag_enabled = st.toggle("🔎 RAG", value=st.session_state.rag_enabled, disabled=settings["disabled"])

                if st.session_state.rag_enabled:
                    st.markdown("##### 📁 Carregar Arquivo")
                    uploaded_file = st.file_uploader('Adicionar PDF', key=f"file-{self.session_id}", type=['pdf'])


            st.session_state.session_options = {
                'language': language_option,
                'model': selected_model,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'developer': settings["model_options"][selected_model]['developer']
            }

            st.markdown('###')
            st.subheader('Recentes', divider='gray')
            self.display_previous_sessions()

        if uploaded_file:
            if st.session_state.uploaded_file is None and st.session_state.retriever is None:
                doc = Document()
                st.session_state.retriever = doc.load(uploaded_file)

def main():
    try:
        st.set_page_config(page_title='AI Chatbot', page_icon='💬')
        st.markdown('<h1><img src="https://img.icons8.com/fluency/50/chatbot--v1.png" alt="Kronos - AI Assistant" style="vertical-align: middle;padding: 0 0 5px 0 ;"> Kronos - AI Assistant</h1>', unsafe_allow_html=True)
        st.header("", divider='rainbow', anchor=False)

        init_sessions()
        st.session_state.db_connection = ChatDbMessages()

        app = App()
        bot = Chatbot()

        for msg in st.session_state.db_connection.messages:

            think_pattern = r'<think>(.*?)</think>'
            think_match = re.search(think_pattern, msg.content, re.DOTALL)

            if think_match:
                thinking_process = think_match.group(1).strip()
                final_response = re.sub(think_pattern, '', msg.content, flags=re.DOTALL).strip()
            else:
                thinking_process = None
                final_response = msg.content

            if thinking_process:
                with st.expander("🤔 Veja o processo de pensamento"):
                    st.markdown(thinking_process)

            st.chat_message(msg.type).markdown(final_response)

        if prompt := st.chat_input():
            st.chat_message('human').write(prompt)
            bot.bot_response(prompt)


    except Exception as e:
        raise e

if __name__=="__main__":
    main()

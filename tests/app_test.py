from langchain_text_splitters.character import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from PyPDF2 import PdfReader
from chatdb_test import ChatDbMessages
from chatbot_test import Chatbot
from utils_test import *

def create_session_button(session_id, options, label):
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

def display_previous_sessions(_conn):
    try:
        sessions = _conn.get_previus_sessions()  # Obtem IDs das sessões
        sessions_ord = set_timestamp_session(sessions)  # Ordena por timestamp

        for session_data in sessions_ord:
            session_id = session_data['session_id']
            result = _conn.get_message_history(session_id=session_id)
            options = _conn.get_previus_sessions_options(session_id=session_id)

            if result:
                label = mask_text(result[0].content)
                create_session_button(session_id, options, label)

    except Exception as e:
        raise e

def load_documents(file_path):
    try:
        pdf_reader = PdfReader(file_path)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        embeddings = HuggingFaceEmbeddings()
        text_splitter = RecursiveCharacterTextSplitter( chunk_size=1000, chunk_overlap=200 )
        docs = text_splitter.split_text(text)
        vectorstores = FAISS.from_texts(docs, embeddings)

    except Exception as e:
        raise e

    return vectorstores.as_retriever()

def sidebar_options(_conn, session_id) -> str:

    settings = get_default_settings(_conn.messages)

    with st.sidebar:
        st.button('Nova Conversa', icon="➕", on_click=start_new_session, use_container_width=True)
        st.button("Deletar Conversa", icon="❌", on_click=_conn.clear, use_container_width=True)

        with st.popover('Configurações', icon='⚙️', use_container_width=True):
            language_option = st.selectbox("Idioma", options=settings["language_options"], key=f'lang-{session_id}', disabled=settings["disabled"])
            selected_model = st.selectbox("Modelo", options=list(settings["model_options"].keys()), key=f'model-{session_id}', disabled=settings["disabled"])
            temperature = st.slider('Temperatura', 0.0, 2.0, settings["temperature_default"], key=f'temp-{session_id}', disabled=settings["disabled"])
            max_tokens = st.slider('Max Tokens', 0, settings["model_options"][selected_model]["tokens"], settings["max_token_default"], key=f'tokens-{session_id}', disabled=settings["disabled"])
            uploaded_file = st.file_uploader('Adicionar Arquivo', key=f"file-{session_id}", disabled=settings["disabled"])

        st.session_state.session_options = {
            'language': language_option,
            'model': selected_model,
            'max_tokens': max_tokens,
            'temperature': temperature
        }

        st.markdown('###')
        st.subheader('Recentes', divider='gray')
        display_previous_sessions(_conn)

        if uploaded_file:

            if "uploaded_file" not in st.session_state:
                st.session_state.uploaded_file = uploaded_file

            if "retriever" not in st.session_state:
                st.session_state.retriever = load_documents(st.session_state.uploaded_file)

def main():
    try:
        st.set_page_config(page_title='Kronos Bot', page_icon='💬')
        st.markdown("<h1 style='text-align:center;'><img width='60' height='60' src='https://img.icons8.com/isometric/60/bot.png'/> Kronos Assistent</h1>", unsafe_allow_html=True)
        st.subheader("", divider='rainbow', anchor=False)

        session_id = init_sessions()

        conn = ChatDbMessages()
        sidebar_options(conn, session_id)
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

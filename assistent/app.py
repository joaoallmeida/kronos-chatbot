from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from chatdb import ChatDbMessages
from chatbot import Chatbot
from utils import *
import re

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

# Function to clean the text
def clean_text(text):
  cleaned_text = text.strip()  # Remove leading/trailing whitespace
  cleaned_text = re.sub(r"\s+", " ", cleaned_text)  # Replace extra spaces with a single space
  cleaned_text = re.sub(r"[^\w\s]", "", cleaned_text)  # Remove non-alphanumeric characters
  return cleaned_text

@st.cache_data(show_spinner=False)
def load_documents(file_path):
    try:
        loader = PyPDFLoader(file_path)
        documents =  loader.load()

        for doc in documents:
            cleaned = clean_text(doc.page_content)
            doc.page_content = cleaned

        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vectorstores = FAISS.from_documents(documents, embeddings)
    except Exception as e:
        raise e

    return vectorstores.as_retriever()

def sidebar_options(_conn, session_id) -> str:

    settings = get_default_settings(_conn.messages)

    with st.sidebar:
        with st.popover('Configurações', icon='⚙️', use_container_width=True):
            language_option = st.selectbox("Idioma", options=settings["language_options"], key=f'lang-{session_id}', disabled=settings["disabled"])
            selected_model = st.selectbox("Modelo", options=list(settings["model_options"].keys()), key=f'model-{session_id}', disabled=settings["disabled"])
            temperature = st.slider('Temperatura', 0.0, 2.0, settings["temperature_default"], key=f'temp-{session_id}', disabled=settings["disabled"])
            max_tokens = st.slider('Max Tokens', 0, settings["model_options"][selected_model]["tokens"], settings["max_token_default"], key=f'tokens-{session_id}', disabled=settings["disabled"])
            uploaded_file = st.file_uploader('Adicionar Arquivo', key=f"file-{session_id}", disabled=settings["disabled"])

        st.button('Nova Conversa', icon="➕", on_click=start_new_session, use_container_width=True)
        st.button("Deletar Conversa", icon="❌", on_click=_conn.clear, use_container_width=True)

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

            file_path = f"/tmp/{uploaded_file.name}"
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            if st.session_state.uploaded_file is None :
                st.session_state.uploaded_file = file_path

            if st.session_state.retriever is None :
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
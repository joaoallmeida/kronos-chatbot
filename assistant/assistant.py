from chatdb import ChatDbMessages
from chatbot import Chatbot
from doc_loaders import Document
from utils import *
import re

class Assistant:
    def __init__(self):
        self.session_id = st.session_state.session_id
        self.conn = st.session_state.db_connection
        self.__sidebar_options__()

    def __create_session_button__(self, session_id, options, label):
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

    def __display_previous_sessions__(self):
        try:
            sessions = self.conn.get_previus_sessions()  # Obtem IDs das sessões
            sessions_ord = set_timestamp_session(sessions)  # Ordena por timestamp

            for session_data in sessions_ord:
                session_id = session_data['session_id']
                result = self.conn.get_message_history(session_id=session_id)
                options = self.conn.get_previus_sessions_options(session_id=session_id)

                if result:
                    label = mask_text(result[0].content)
                    self.__create_session_button__(session_id, options, label)

        except Exception as e:
            raise e

    def __sidebar_options__(self) -> str:

        settings = get_default_settings(self.conn.messages)

        with st.sidebar:

            st.button('New Chat', icon="➕", on_click=start_new_session, use_container_width=True)
            if st.button("Delete Chat", icon="❌", on_click=self.conn.clear, use_container_width=True):
                st.rerun()

            with st.popover('Settings', icon='⚙️', use_container_width=True):
                language_option = st.selectbox("Language", options=settings["language_options"], key=f'lang-{self.session_id}', disabled=settings["disabled"])
                selected_model = st.selectbox("Model", options=sorted(list(settings["model_options"].keys())), key=f'model-{self.session_id}', disabled=settings["disabled"])
                temperature = st.slider('Temperature', 0.0, 2.0, settings["temperature_default"], key=f'temp-{self.session_id}', disabled=settings["disabled"])
                max_tokens = st.slider('Max Tokens', 0, settings["model_options"][selected_model]["tokens"], settings["max_token_default"], key=f'tokens-{self.session_id}', disabled=settings["disabled"])

            st.subheader('', divider='gray')
            st.session_state.rag_enabled = st.toggle("🔎 RAG", value=st.session_state.rag_enabled, disabled=settings['disabled'])

            if st.session_state.rag_enabled:
                st.session_state.uploaded_file = st.file_uploader('📁 Add File', type=['pdf'])
                st.session_state.threshold = st.slider('Threshold', 0.0 , 1.0, 0.7, key=f'thres-{self.session_id}', disabled=settings['disabled'])

            st.session_state.session_options = {
                'language': language_option,
                'model': selected_model,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'developer': settings["model_options"][selected_model]['developer'],
                'disabled': settings["disabled"],
            }

            st.markdown('###')
            st.subheader('Previous Chats', divider='gray')
            self.__display_previous_sessions__()

        if st.session_state.uploaded_file is not None and st.session_state.retriever is None:
            doc = Document()
            st.session_state.retriever = doc.pdf_load()

def main():
    try:
        st.set_page_config(page_title='AI Chatbot', page_icon='💬')
        st.markdown('<h1 style="text-align:center"><img src="https://img.icons8.com/fluency/50/chatbot--v1.png" alt="Kronos - AI Assistant" style="vertical-align: middle;padding: 0 0 5px 0 ;"> Kronos - AI Assistant</h1>', unsafe_allow_html=True)
        st.header("", divider='rainbow', anchor=False)

        init = init_sessions()
        st.session_state.db_connection = ChatDbMessages()
        att = Assistant()
        bot = Chatbot()

        if 'DeepSeek' in st.session_state.session_options['developer']:
            st.session_state.thinking_mode = st.toggle('💡DeepThink', value=st.session_state.thinking_mode)

        for msg in st.session_state.db_connection.messages:

            think_pattern = r'<think>(.*?)</think>'
            think_match = re.search(think_pattern, msg.content, re.DOTALL)

            if think_match:
                thinking_process = think_match.group(1).strip()
                final_response = re.sub(think_pattern, '', msg.content, flags=re.DOTALL).strip()
            else:
                thinking_process = None
                final_response = msg.content

            if st.session_state.thinking_mode:
                if thinking_process:
                    with st.expander("🤔 See the thinking process"):
                        st.markdown(thinking_process)

            st.chat_message(msg.type).markdown(final_response)

        if prompt := st.chat_input():
            st.chat_message('human').write(prompt)
            bot.bot_response(prompt)

    except Exception as e:
        raise e

if __name__=="__main__":
    main()

from chatdb import ChatDbMessages
from chatbot import Chatbot
from sessions import *

def mask_text(text: str) -> str:
    return text[:30] + "..." if len(text) > 30 else text

# Atualiza timestamp e define a sessão atual
def update_timestamp(session_id):
    st.session_state.timestamps[session_id] = datetime.now()
    st.session_state.session_id = session_id

# Verifica se a sessão é ativa para desabilitar o botão correspondente
def create_session_button(session_id, label):
    disabled = (st.session_state.get("session_id") == session_id)
    st.button(
        label=label,
        key=f"btn-{session_id}",
        on_click=update_timestamp,
        args=(session_id,),
        disabled=disabled,
        use_container_width=True
    )

def display_previous_sessions(_conn):
    try:
        sessions = _conn.get_sessions_id()  # Obtem IDs das sessões
        sessions = set_timestamp_session(sessions)  # Ordena por timestamp

        for session_data in sessions:
            session_id = session_data['session_id']
            result = _conn.get_message_history(session_id=session_id)

            if result:
                label = mask_text(result[0].content)
                create_session_button(session_id, label)

    except Exception as e:
        raise e

def sidebar_options(_conn) -> str:
    with st.sidebar:

        st.button('Nova Conversa', icon="➕", on_click=start_new_session, use_container_width=True)
        st.button("Limpar Conversa", icon="❌", on_click=_conn.clear, use_container_width=True)
        st.markdown('###')
        st.subheader('Recentes', divider='gray')

        with st.container(height=400, border=False):
            display_previous_sessions(_conn)

        st.markdown('#')
        st.markdown('#')
        st.subheader('', divider='gray')
        with st.popover('Configurações', icon='⚙️', use_container_width=True):
            
            language_options = {
                '🇧🇷 Português': 'Português',
                '🇺🇸 English': 'English'
            }

            model_options = {
                "llama3-8b-8192": {"name": "llama3-8b-8192", "tokens": 8192, "developer": "Meta"},
                "llama3-70b-8192": {"name": "llama3-70b-8192", "tokens": 8192, "developer": "Meta"},
                "mixtral-8x7b-32768": {"name": "mixtral-8x7b-32768", "tokens": 32768, "developer": "Meta"},
                "gemma-7b-it": {"name": "gemma-7b-it", "tokens": 8192, "developer": "Google"},
            }

            selected_display = st.selectbox("Idioma", options=list(language_options.keys()))
            language_option = language_options[selected_display]

            selected_model = st.selectbox("Modelo", options=list(model_options.keys()))
            temperature = st.slider('Temperatura',0.0,2.0,0.5)
            max_tokens = st.slider('Max Tokens', 0, model_options[selected_model]["tokens"], 1024)

            options = {
                'language': language_option,
                'model': selected_model,
                'max_tokens': max_tokens,
                'temperature': temperature
            }

    return options

def main():
    try:
        st.set_page_config(page_title='Kronos Bot', page_icon='💬')
        st.markdown("<h1 style='text-align:center; color: white'><img width='60' height='60' src='https://img.icons8.com/isometric/60/bot.png'/> Kronos Assistent </h1>", unsafe_allow_html=True)
        st.subheader("", divider='rainbow', anchor=False)

        session_id = init_sessions()

        conn = ChatDbMessages()
        options = sidebar_options(conn)
        bot = Chatbot(conn, session_id, options)

        for msg in conn.messages:
            st.chat_message(msg.type).write(msg.content)

        if prompt := st.chat_input():
            st.chat_message('human').write(prompt)
            bot.bot_response(prompt)

    except Exception as e:
        raise e


if __name__=="__main__":
    main()

from datetime import datetime
from groq import Groq
import streamlit as st
import uuid
import os

def init_sessions():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'session_options' not in st.session_state:
        st.session_state.session_options = {}
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "uploaded_file_type" not in st.session_state:
        st.session_state.uploaded_file_type = None
    if 'rag_enabled' not in st.session_state:
        st.session_state.rag_enabled = False
    if 'db_connection' not in st.session_state:
        st.session_state.db_connection = None

def start_new_session():
    for key in st.session_state.keys():
        del st.session_state[key]

def update_session(session_id, options):
    st.session_state.timestamps[session_id] = datetime.now()
    st.session_state.session_id = session_id
    st.session_state.session_options = options

def set_timestamp_session(sessions:list):
    if 'timestamps' not in st.session_state:
        st.session_state.timestamps = {session['session_id']: session['timestamp'] for session in sessions}

    return sorted(sessions, key=lambda s: st.session_state['timestamps'].get(s['session_id'], datetime.now()), reverse=True)

def mask_text(text: str) -> str:
    return ( text[:30].replace('\n',' ') + "..." ) if len(text) > 30 else text

@st.cache_data
def get_models() -> dict:
    client = Groq( api_key=os.environ.get("GROQ_API_KEY") )
    models = client.models.list()
    models_dict = models.to_dict()
    return { a['id']: {"name": a['id'], "tokens": a['context_window'], "developer": a['owned_by']}  for a in models_dict['data'] if a['active'] is True }

def get_default_settings(is_connected):
    MODEL_OPTIONS = get_models()

    if is_connected:
        return {
            "disabled": True,
            "language_options": [st.session_state.session_options['language']],
            "temperature_default": float(st.session_state.session_options['temperature']),
            "max_token_default": int(st.session_state.session_options['max_tokens']),
            "model_options": {
                st.session_state.session_options['model']: {
                    "name": st.session_state.session_options['model'],
                    "tokens": MODEL_OPTIONS[st.session_state.session_options['model']]['tokens'],
                    "developer": MODEL_OPTIONS[st.session_state.session_options['model']]['developer']
                }
            }
        }
    else:
        return {
            "disabled": False,
            "language_options": ['Português', 'English'],
            "temperature_default": 1.0,
            "max_token_default": 1024,
            "model_options": MODEL_OPTIONS
        }

def thinkins_processing(response, ctype:str=None) -> any:
    import re

    think_pattern = r'<think>(.*?)</think>'

    if ctype == 'rag':
        response = response['answer']

    think_match = re.findall(think_pattern, response, re.DOTALL)

    if think_match:
        thinking_process = [a.strip() for a in think_match][0]
        final_response = re.sub(think_pattern, '', response, flags=re.DOTALL).split(' ')
    else:
        thinking_process = None
        final_response = response.split(' ')

    return thinking_process, final_response


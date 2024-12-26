from datetime import datetime
import streamlit as st
import uuid

def init_sessions():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'session_options' not in st.session_state:
        st.session_state.session_options = {}
    if "retriever" not in st.session_state:
        st.session_state.retriever = None
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    return st.session_state.session_id

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
    return text[:30] + "..." if len(text) > 30 else text

def get_default_settings(is_connected):
    MODEL_OPTIONS = {
        "llama3-70b-8192": {"name": "llama3-70b-8192", "tokens": 8192, "developer": "Meta"},
        "llama3-8b-8192": {"name": "llama3-8b-8192", "tokens": 8192, "developer": "Meta"},
        "llama-3.2-3b-preview": {"name": "llama-3.2-3b-preview", "tokens": 8192, "developer": "Meta"},
        "mixtral-8x7b-32768": {"name": "mixtral-8x7b-32768", "tokens": 32768, "developer": "Meta"},
        "gemma-7b-it": {"name": "gemma-7b-it", "tokens": 8192, "developer": "Google"},
    }

    if is_connected:
        return {
            "disabled": True,
            "language_options": [st.session_state.session_options['language']],
            "temperature_default": float(st.session_state.session_options['temperature']),
            "max_token_default": int(st.session_state.session_options['max_tokens']),
            "model_options": {
                st.session_state.session_options['model']: {
                    "name": st.session_state.session_options['model'],
                    "tokens": MODEL_OPTIONS[st.session_state.session_options['model']]['tokens']
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


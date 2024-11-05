from datetime import datetime
import streamlit as st
import uuid

def init_sessions():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    if 'session_options' not in st.session_state:
        st.session_state.session_options = {}
    return st.session_state.session_id

def start_new_session():
    for key in st.session_state.keys():
        del st.session_state[key]

def set_timestamp_session(sessions:list):
    if 'timestamps' not in st.session_state:
        st.session_state.timestamps = {session['session_id']: session['timestamp'] for session in sessions}

    return sorted(sessions, key=lambda s: st.session_state['timestamps'].get(s['session_id'], datetime.now()), reverse=True)

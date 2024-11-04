from datetime import datetime
import streamlit as st
import uuid

def init_sessions():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

def start_new_session():
    st.session_state.session_id = str(uuid.uuid4())

def set_current_session(session_id:str):
    st.session_state.session_id = session_id

def set_timestamp_session(sessions:list):
    if 'timestamps' not in st.session_state:
        st.session_state.timestamps = {session['session_id']: session['timestamp'] for session in sessions}

    return sorted(sessions, key=lambda s: st.session_state['timestamps'].get(s['session_id'], datetime.now()), reverse=True)

from datetime import datetime
from typing import List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, messages_from_dict, message_to_dict
from pymongo import DESCENDING, MongoClient
import json
import streamlit as st


class ChatDbMessages(BaseChatMessageHistory):
    def __init__(self):
        self.client = MongoClient(host='mongodb', port=27017)
        self.session_id = st.session_state.session_id

        database = self.client['chat_history']
        self.collection = database['message_store']

    @property
    def messages(self) -> List[BaseMessage]:
        try:
            session = self.collection.find({'session_id': self.session_id})
            if session:
                results = [json.loads(data['history']) for data in session]
            else:
                results = []

        except Exception as e:
            raise e

        return messages_from_dict(results)

    def add_message(self, message:BaseMessage) -> None :
        try:
            self.collection.insert_one({
                'session_id': self.session_id,
                'history': json.dumps(message_to_dict(message)),
                'session_options': json.dumps(st.session_state.session_options),
                'timestamp': datetime.now()
            })

        except Exception as e:
            raise e

    def clear(self) -> None:
        self.collection.delete_many({'session_id': self.session_id})

    def get_previus_sessions(self):
        unique_sessions = {}

        for data in self.collection.find().sort('timestamp', DESCENDING):
            session_id = data['session_id']
            timestamp = data['timestamp']

            if session_id not in unique_sessions:
                unique_sessions[session_id] = timestamp

        # Retornar o session_id e timestamp únicos
        return [{'session_id': session_id, 'timestamp': timestamp} for session_id, session in unique_sessions.items()]

    def get_previus_sessions_options(self, session_id:str) -> dict:
        return [json.loads(data['session_options']) for data in self.collection.find({"session_id":session_id}).limit(1)][0]

    def get_message_history(self, session_id:str=None) -> List[BaseMessage]:
        if session_id:
            result = [json.loads(data['history']) for data in self.collection.find({'session_id': session_id}).limit(1)]
        else:
            result = [json.loads(data['history']) for data in self.collection.find()]

        return messages_from_dict(result)

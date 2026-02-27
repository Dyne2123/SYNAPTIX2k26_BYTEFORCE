# gemini_chat_db.py
import os
from google.genai import Client
from database import MongoDB

class GeminiChatDB:
    """
    Gemini Chat with persistent storage in MongoDB per user.
    """
    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        os.environ["GENAI_API_KEY"] = api_key
        self.client = Client()
        self.model = model
        self.mongo = MongoDB()  # MongoDB instance

    def _get_or_create_user(self, user_phone, user_name="Unknown"):
        """Ensure user exists in DB"""
        user = self.mongo.collection.find_one({"phone_number": user_phone})
        if not user:
            self.mongo.add_user({"name": user_name, "phone": user_phone})
            user = self.mongo.collection.find_one({"phone_number": user_phone})
        return user

    def send_message(self, user_phone: str, message: str, user_name="Unknown") -> str:
        """Send a message to Gemini with persistent history in MongoDB"""
        user = self._get_or_create_user(user_phone, user_name)

        # Create chat session
        chat_session = self.client.chats.create(model=self.model)

        # Load previous messages for context
        for msg in user.get("bot_history", []):
            chat_session.send_message(f"{msg['role']}: {msg['content']}")

        # Send the new user message
        response = chat_session.send_message(message)

        # Update MongoDB history
        new_history_user = {"role": "user", "content": message}
        new_history_bot = {"role": "assistant", "content": response.text}

        self.mongo.collection.update_one(
            {"phone_number": user_phone},
            {"$push": {"bot_history": {"$each": [new_history_user, new_history_bot]}}}
        )

        return response.text

    def get_history(self, user_phone: str):
        user = self.mongo.collection.find_one({"phone_number": user_phone})
        return user.get("bot_history", []) if user else []
# database.py
from pymongo import MongoClient

class MongoDB:
    def __init__(self):
        self.MONGO_URI = "mongodb://localhost:27017/"
        self.DB_NAME = "WhatsAppBot"

        try:
            self.client = MongoClient(self.MONGO_URI)
            self.db = self.client[self.DB_NAME]
            self.client.admin.command("ping")
            print("✅ MongoDB Connected Successfully")
        except Exception as e:
            print("❌ MongoDB Connection Error:", e)

        self.collection = self.db["UserData"]

    def add_user(self, data):
        """Insert user if not exists"""
        x = self.collection.find_one({"phone_number": data["phone"]})
        if not x:
            template = {
                "name": data["name"],
                "phone_number": data["phone"],
                "bot_history": [],
                "bot_summary": ""
            }
            self.collection.insert_one(template)
            print(f"[DEBUG] New user added: {data['phone']}")
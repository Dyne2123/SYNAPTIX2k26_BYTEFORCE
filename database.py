#database.py
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

    def add_user(self,username,phonenumber):
        """Insert user if not exists"""
        x = self.collection.find_one({"phone_number": phonenumber})
        if not x:
            template = {
                "name": username,
                "phone_number": phonenumber,
                "bot_history": [],
                "bot_summary": ""
            }
            
            self.collection.insert_one(template)
            self.add_bot_history(phonenumber,{"system":"only reply to last user message consider remaining as context. Your name is UtilityBot. Introduce yourself at first conversation"})
            print(f"[DEBUG] New user added: {phonenumber}")
        
    def add_bot_history(self,phone_number,message):
        data = {"user":message}
        result = self.collection.update_one(
                    {"phone_number": phone_number},   # filter by phone number
                    {"$push": {"bot_history": message}})  # append new entry
        print("history added")

    def get_bot_history(self,number):
        doc = self.collection.find_one(
        {"phone_number": number},     # filter
        {"_id": 0, "bot_history": 1}  # projection
    )
        if doc:
            return doc.get("bot_history", [])
        return []



        

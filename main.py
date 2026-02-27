# app.py
from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv
from LLM import GeminiChatDB
import requests

# Load environment variables
load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Flask and Gemini Chat
app = Flask(__name__)
gem_chat = GeminiChatDB(GEMINI_API_KEY)

# Webhook Verification
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return challenge, 200
    return "Verification failed", 403

# Receive messages from WhatsApp
@app.route("/webhook", methods=["POST"])
def receive_message():
    try:
        data = request.get_json()
        if not data:
            return "No JSON", 400
        # Extract user message
        user_data = extract_whatsapp_message(data)
        if not user_data:
            return "No valid message", 200

        print(f"[DEBUG] Message from {user_data['phone_number']}: {user_data['message']}")

        # Send message to Gemini AI and get reply
        reply_text = gem_chat.send_message(
            user_phone=user_data["phone_number"],
            message=user_data["message"],
            user_name=user_data.get("name", "Unknown")
        )

        # Send reply back to WhatsApp
        send_whatsapp_message(user_data["phone_number"], reply_text)

        return "Message processed", 200

    except Exception as e:
        print("Webhook Error:", e)
        return "Internal Server Error", 500

# Extract message payload
def extract_whatsapp_message(payload: dict):
    try:
        if payload.get("object") != "whatsapp_business_account":
            return None
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        contacts = value.get("contacts", [])
        messages = value.get("messages", [])
        if not contacts or not messages:
            return None
        contact = contacts[0]
        message = messages[0]
        user_name = contact.get("profile", {}).get("name", "Unknown")
        phone_number = contact.get("wa_id")
        text_message = message.get("text", {}).get("body") if message.get("type") == "text" else f"[{message.get('type')} message]"
        return {"name": user_name, "phone_number": phone_number, "message": text_message}
    except Exception as e:
        print("Extraction error:", e)
        return None

# Send message via WhatsApp Cloud API
def send_whatsapp_message(recipient_number: str, message_text: str):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": recipient_number, "type": "text", "text": {"body": message_text}}
    response = requests.post(url, json=payload, headers=headers)
    print(f"[DEBUG] WhatsApp API Response: {response.json()}")
    return response.json()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
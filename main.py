
from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv
from database import MongoDB
from LLM import LLM

# ----------------------------
# Load Environment Variables
# ----------------------------
load_dotenv()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# ----------------------------
# Initialize Flask App
# ----------------------------
app = Flask(__name__)

# ----------------------------
# Webhook Verification (GET)
# ----------------------------
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return challenge, 200

    return "Verification failed", 403


# ----------------------------
# Receive Messages (POST)
# ----------------------------
@app.route("/webhook", methods=["POST"])
def receive_message():
    try:
        if not request.is_json:
            print("Invalid request: Not JSON")
            return "Invalid request", 400

        data = request.get_json()
        print("Incoming Webhook:", data)

        user_data = extract_whatsapp_message(data)

        if not user_data:
            print("No valid message found in payload")
            return "Event received", 200

        print("Name:", user_data["name"])
        print("Phone:", user_data["phone_number"])
        print("Message:", user_data["message"])

        # Reply Message
        # reply_text = f"Hello {user_data['name']}"
        # send_whatsapp_message(user_data["phone_number"], reply_text)

        return "Message processed", 200

    except Exception as e:
        print("Webhook Error:", str(e))
        return "Internal Server Error", 500


# ----------------------------
# Extract Message Data
# ----------------------------
def extract_whatsapp_message(payload: dict):
    try:
        if payload.get("object") != "whatsapp_business_account":
            return None

        entry = payload.get("entry", [])
        if not entry:
            return None

        changes = entry[0].get("changes", [])
        if not changes:
            return None

        value = changes[0].get("value", {})

        contacts = value.get("contacts", [])
        messages = value.get("messages", [])

        if not contacts or not messages:
            return None

        user_name = contacts[0].get("profile", {}).get("name")
        phone_number = contacts[0].get("wa_id")

        message_type = messages[0].get("type")
        

       
        if message_type == "text":
            text_message = messages[0].get("text", {}).get("body")
        else:
            text_message = f"[Unsupported message type: {message_type}]"

        MongoDB().add_user(user_name,phone_number)
        if not text_message.startswith('/'):
            chat_bot(phone_number,text_message)

        return {
            "name": user_name,
            "phone_number": phone_number,
            "message": text_message
        }

    except Exception as e:
        print("Extraction error:", e)
        return None


# ----------------------------
# Send WhatsApp Message
# ----------------------------
def send_whatsapp_message(recipient_number: str, message_text: str):
    try:
        url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"

        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": recipient_number,
            "type": "text",
            "text": {
                "body": message_text
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        print("WhatsApp API Response:", response.json())

        return response.json()

    except Exception as e:
        print("Send message error:", e)
        return None
def chat_bot(number,message):
    user_msg = {"user":message}
    MongoDB().add_bot_history(number,user_msg)
    print(number,message)
    response = LLM(message,number)
    send_whatsapp_message(number,response)



# ----------------------------
# Run Application
# ----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

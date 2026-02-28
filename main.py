
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
JSEARCH = os.getenv("JSEARCH")
METAL = os.getenv("METALPRICE")
CRYPTO = os.getenv("CRYPTOAPI")


app = Flask(__name__)


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verified successfully")
        return challenge, 200

    return "Verification failed", 403



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

        
        return "Message processed", 200

    except Exception as e:
        print("Webhook Error:", str(e))
        return "Internal Server Error", 500


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
        global number
        number = phone_number
        message_type = messages[0].get("type")
        

       
        if message_type == "text":
            text_message = messages[0].get("text", {}).get("body")
            MongoDB().add_user(user_name,phone_number)
            if not text_message.startswith('/'):
                chat_bot(phone_number,text_message)
            else:
                parse_command(text_message,phone_number)

        elif message_type == "image":
            media_id = messages[0].get("image", {}).get("id")
            mime_type = messages[0].get("image", {}).get("mime_type")

            print("Image received!")
            print("Media ID:", media_id)

            if media_id:
                file_path = download_whatsapp_media(media_id, mime_type)
                message = f"[Image received and saved as {file_path}]"
            else:
                message = "[Image received but no media ID found]"
            

        

        return {
            "name": user_name,
            "phone_number": phone_number,
            "message": text_message
        }

    except Exception as e:
        print("Extraction error:", e)
        return None
    
def download_whatsapp_media(media_id, mime_type):
    pass


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

def parse_command(command,number):
    from utility import search_jobs
    print(command)
    parsed = command.split()

    print("parsed  ", parsed[1])
    if parsed[1].strip() == "job":
        print("inside if")
        send_whatsapp_message(number,"fetching job postings........!")
        query = " ".join(parsed[2::])
        print("query ", query)
        search_jobs(parsed[2],number)

    if parsed[1].strip() == "help":
        text = "======= Avaliable commands ========\n1. / job  {query} :to search for jobs\n 2. / gold :to get current live gold price \n 3. / password :to generate strong random password \n 4. / crypto10 :get the price of top 10 crypto currencies \n 5. / getstockprice {company name} :get the stock price of the company \n 6. / wiki {context} :To get summary about search term \n 7. / quote {keyword/random} :get random or specific quote \n 8. / getbooks {book domain} :Get the book of the specified domain \n 9. / deals {product name} :to get best deals to buy product"
        send_whatsapp_message(number,text)

    if parsed[1].strip() == "gold":
        from utility import get_gold_price
        text = get_gold_price()
        send_whatsapp_message(number,text)

    if parsed[1].strip() == "password":
        from utility import generate_password
        text = generate_password()
        send_whatsapp_message(number,text)
    
    if parsed[1].strip() == "crypto10":
        from utility import get_top_10
        text = get_top_10()
        send_whatsapp_message(number,text)

    if parsed[1].strip() == "getstockprice":
        from utility import get_stock_price
        company = parsed[2].strip()
        text = get_stock_price(company)
        send_whatsapp_message(number,text)


    if parsed[1].strip() == "wiki":
        from utility import wiki
        context = " ".join(parsed[2::])
        text = wiki(context)
        send_whatsapp_message(number,text)
    
    if parsed[1].strip() == "quote":
        from utility import get_quote
        text = get_quote(parsed[2])
        send_whatsapp_message(number,text)

    if parsed[1].strip() == "getbooks":
        send_whatsapp_message(number,"fetching books.........!")
        from utility import recommend_books
        domain = " ".join(parsed[2::]).strip()
        text = "\n\n".join(recommend_books(domain))
        send_whatsapp_message(number,text)

    if parsed[1].strip() == "deals":
        from utility import get_lowest_price_summary
        context = " ".join(parsed[2::])
        send_whatsapp_message(number,"fetching best deals.........")
        text = get_lowest_price_summary(context)
        send_whatsapp_message(number,text)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

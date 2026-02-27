from database import MongoDB

from google import genai


client = genai.Client(api_key="AIzaSyA0DmDfXlEJWr7FmuBP8si9NeQoDMp4zAE")

def LLM(message, phonenumber):
    
    db = MongoDB()


    history = db.get_bot_history(phonenumber)  

    fixed_history = []
    for msg in history:
        if "user" in msg:
            fixed_history.append({"role": "user", "content": msg["user"]})
        elif "assistant" in msg:
            fixed_history.append({"role": "assistant", "content": msg["assistant"]})
        elif "system" in msg:
            fixed_history.append({"role": "system","content":msg["system"]})

    fixed_history.append({"role": "user", "content": message})

   
    contents_list = [f"{msg['role']}: {msg['content']}" for msg in fixed_history]

    print("Normalized history:", fixed_history)
    print("Contents sent to Gemini:", contents_list)


    response = callLLM(contents_list)

    bot_reply = response.text
    print("Gemini reply:", bot_reply)
    MongoDB().add_bot_history(phonenumber,{"assistant":bot_reply})

    return bot_reply


def callLLM(content_list):
    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=content_list
    )
    return response 
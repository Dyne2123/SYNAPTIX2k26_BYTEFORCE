from database import MongoDB

from google import genai



# def LLM(message,phonenumber):
#     client = genai.Client(api_key="AIzaSyCp454P0OxDKSguWg_TlcqCEyyJTK7MIfk")
#     history = MongoDB().get_bot_history(phonenumber)
#     fixed_history = [
#         {"role": "user", "content": msg["user"]} for msg in history
#     ]

#     print("history",history)
#     contents_list = [f"{msg['role']}: {msg['content']}" for msg in fixed_history]
#     print(contents_list)
#     response = client.models.generate_content(
#         model="gemini-3-flash-preview",
#         contents=contents_list
#     )
#     print(response.text)
#     bot_response = {"assistant":response.text}
#     user_msg = message
    
#     MongoDB().add_bot_history(phonenumber,bot_response)

#     return response.text

def LLM(message, phonenumber):
    client = genai.Client(api_key="AIzaSyDioNBx4Lc_pYFRCUOhkjyaz9p6XM3CT2A")
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

    response = client.models.generate_content(
        model="gemini-2.5-flash-lite",
        contents=contents_list
    )

    bot_reply = response.text
    print("Gemini reply:", bot_reply)
    MongoDB().add_bot_history(phonenumber,{"assistant":bot_reply})

    return bot_reply


import requests
import os
from dotenv import load_dotenv
# from telegram import Update as update
# import asyncio

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
base_url = f"https://api.telegram.org/bot{bot_token}"

# globals
seen_chats = set()
user_states = {}


# greeting message (image with caption)
def send_greeting_message(chat_id, message_id, sender):
    image_url = "https://cdn.prod.website-files.com/65ce038ac58a7f988fb59ccd/6862f809b4d779c5cc7013bd_660dde5fd75afffac6083973_Insurance%2520Basics%2520Everything%2520you%2520need%2520to%2520know-min.webp"  
    caption = f"👋 Hello! {sender}, Welcome to Onyx Assurance Limited. \nPlease enter your *full name* and let me assist you. \nEg: Kyle Larry"
    
    requests.post(base_url + "/sendPhoto", data={
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "reply_to_message_id": message_id
    })
    
    
# sending options of the main menu
def send_main_menu_options(chat_id):
    keyboard = {
        "inline_keyboard": [
            [{"text": "Learn", "callback_data": "learn"}],
            [{"text": "Ask a Question", "callback_data": "ask"}, {"text": "Contact", "callback_data": "contact"}],
            [{"text": "Check", "callback_data": "contact"}],
        ]
    }


# message handling
def handle_text_message(data):
    message = data["message"]
    chat_id = message["chat"]["id"]
    chat_type = message["chat"]["type"]
    message_id = message["message_id"]
    sender = message["from"]["username"]
    text = message.get("text", "")

    if not isinstance(text, str):
        return

    # Group chat logic
    if chat_type in ["group", "supergroup"]:
        return

    # checking input text 
    if text.lower()  == "hello" or text.lower() == "hi":
        # check if chat user already said hello or hi 
        # if it turns true, take the person back to the main menu
        if chat_id in seen_chats:
            print(f"chat is already seen: {seen_chats}")
        else:
            seen_chats.add(chat_id)
            print(seen_chats)
        
        if chat_id not in user_states:
            send_greeting_message(chat_id, message_id, sender)
            user_states[chat_id] = {"step": "ask_name"}            
        
    else:            
        if user_states and user_states[chat_id]["step"] == "ask_name":
            # print("working")
            user_states[chat_id]["name"] = text.strip()
            user_states[chat_id]["step"] = "awaiting_choice"
            
            # reply after taking name
            requests.post(base_url + "/sendMessage", data={
                "chat_id": chat_id,
                "text": f"Thanks, {text.strip()}!"
            })
            # send_option_buttons(chat_id)
            
        else:
            # reply on wrote first input
            reply = "Invalid input. Please type Hello or Hi to start a conversation with me."
            requests.post(base_url + "/sendMessage", data={
                "chat_id": chat_id,
                "text": reply
            })
            # print(reply)    
    

# reading telegram private messages to bot
def read_message(offset):
    response = requests.get(base_url + "/getUpdates", params={"offset": offset})
    data = response.json()
    updates = data.get("result", [])

    for update in updates:
        if "message" in update:
            handle_text_message(update)
                
        elif "callback_query" in update:
            # handle_callback_query(update)
            print("callback")
            
        else:
            chat_id = update["message"]["chat"]["id"]
            reply = "Invalid input. Please type Hello or Hi to start a conversation with me."
            requests.post(base_url + "/sendMessage", data={
                "chat_id": chat_id,
                "text": reply
            })

    if updates:
        return updates[-1]["update_id"] + 1
    return offset
    


# running read in loop
offset = 0
while True:
    offset = read_message(offset)
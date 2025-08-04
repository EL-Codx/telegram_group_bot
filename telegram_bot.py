import requests
from dotenv import load_dotenv
import os
import pandas as pd


load_dotenv()

qna_url = "https://gist.githubusercontent.com/EL-Codx/d7157c09c964a78e03e51aec4fddea78/raw/74897f16ee2c6f84f822c4ad0b0ba9ddec1bca3c/insurance_data.csv"

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
base_url = f"https://api.telegram.org/bot{bot_token}"


# replies
dataframe = pd.read_csv(qna_url, sep="\t")

def auto_reply(message):
    answer = dataframe.loc[dataframe["question"].str.lower() == message.lower()]
    
    if not answer.empty:
        answer = answer.iloc[0]["answer"]
        return answer
    else:
        return "Sorry, I could not understand you. I am still learning to get better"


# get message from chat
def read_message(offset):
    parameters = {
    "offset": offset,
    }
    
    response = requests.get(base_url + "/getUpdates", data = parameters)
    data = response.json()
    pulls = data["result"]  # holding results pulled from json
    # print(pulls)
    
    # looping through each 
    for each in pulls:
        send_message(each)
    
    # taking the update_id for offset
    if pulls:
        return pulls[-1]["update_id"] + 1


# send message to chat
def send_message(data):
    message = data["message"]["text"]
    message_id = data["message"]["message_id"]
    
    # print(message)
    # print(message_id)
    
    answer = auto_reply(message)
    
    parameters = {
        "chat_id": "-4989461040",
        "text": answer,
        "reply_to_message_id": message_id
    }
    
    response = requests.get(base_url + "/sendMessage", data = parameters)
    # # print(response.text)
    
    


# calls
offset = 0
while True:
    offset = read_message(offset)
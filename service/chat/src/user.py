# Server imports
import json
import time
import requests
from flask import Flask, jsonify, make_response, request
#Flask app
app = Flask(__name__)

# ------------------------------ ENV variables ------------------------------

#.env imports
from dotenv import load_dotenv
from pathlib import Path
import os

#Getting env variables
dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

#Assign env variables

PORT_CHAT = os.getenv('PORT_CHAT')
HOST = os.getenv('HOST')

# ------------------------------ MODELS ------------------------------

from models import Message, Chat

# ------------------------------ ENDPOINTS ------------------------------


#Variables
PORT = PORT_CHAT

with open('{}/databases/chat.json'.format("."), "r") as jsf:
   chat_dict = json.load(jsf)["chat"]
   print(chat_dict)
   chat:list[Chat] = Chat.schema().load(chat_dict, many=True) 
   print(chat)

@app.route("/", methods=['GET'])
def home():
   return make_response(jsonify({'message':'chat service api root'}))

@app.route("/chats", methods=['GET'])
def get_chat():
   return make_response(Chat.schema().dumps(chat, many=True),200)

@app.route("/messages/<chatid>",methods=['GET'])
def get_chat_messages(chatid):
   for c in chat :
      if c.uuid == chatid :
         return make_response(c.to_json(),200)

   return make_response(jsonify({'error': 'chat not found'}),400)

@app.route("/messages/<chatid>",methods=['POST'])
def send_message(chatid):
   for c in chat :
      if c.uuid == chatid :
         return make_response(c.to_json(),200)

   return make_response(jsonify({'error': 'chat not found'}),400)

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

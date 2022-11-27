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
   chat = json.load(jsf)["chat"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/chat", methods=['GET'])
def get_chat():
   return make_response(jsonify(chat),200)

@app.route("/chat/<userid>",methods=['GET'])
def get_user_byid(userid):
   for user in chat :
      if str(userid) == str(user["id"]):
         return make_response(jsonify(user),200)
   return make_response(jsonify({'error':'id not found'}))

@app.route("/chat/<userid>",methods=['POST'])
def create_user(userid):
   req = request.get_json()

   for user in chat:
      if str(user["id"]) == str(userid):
         return make_response(jsonify({"error":"user ID already exists"}),409)

   res = {
      'id':req["id"],
      'name':req["name"],
      'last_active':int(time.time()),
   }

   chat.append(res)
   res = make_response(jsonify({"message":"user added"}),200)
   return res

@app.route("/booking/<userid>")
def get_chat_booking(userid):
   try :
      res = requests.get(f'{BOOKING_URL}/bookings/{userid}')
   except :
      return make_response(jsonify({'error':'error fetching booking microservice'}),400)
   if not(res.ok) : return make_response(jsonify({'error':'error user don\'t have bookings'}),400)
   response = json.loads(res.text)

   return make_response(jsonify(response["dates"]),200)

@app.route("/allmoviesbooked/<userid>")
def get_all_movies_booked(userid):
   try :
      res = requests.get(f'{BASE_URL}/booking/{userid}')
   except :
      return make_response(jsonify({'error':'error fetching user microservice'}))

   dates = json.loads(res.text)

   movie_list = []
   for date in dates :
      for movie in date["movies"] :
         try :
            res = json.loads(requests.get(f'{MOVIE_URL}/movies/{movie}').text)
            movie_list.append(res)
         except :
            return make_response(jsonify({'error':'error fetching movie microservice'}))
   return make_response(jsonify(movie_list))
         

   return None


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

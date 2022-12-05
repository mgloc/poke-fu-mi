# Server imports
import json
import time
import requests
from uuid import uuid4
from flask import Flask, jsonify, make_response, request
#Flask app
app = Flask(__name__)

# ------------------------------ ENV variables ------------------------------

#.env imports
from dotenv import load_dotenv
from pathlib import Path
import os

#Getting env variables
dotenv_path = Path('../../.env')
load_dotenv(dotenv_path=dotenv_path)

#Assign env variables

PORT_STATS = os.getenv('PORT_STATS')
HOST = os.getenv('HOST')

# ------------------------------ MODELS ------------------------------

from models import Stats,GameStats,StatAndUser

# ------------------------------ VARIABLES ------------------------------

PORT = PORT_STATS

with open('{}/db/stats.json'.format("."), "r") as jsf:
   stat_dict = json.load(jsf)["stats"]
   stats:list[Stats] = Stats.schema().load(stat_dict, many=True) 


def generateId():
   return str(uuid4().int)

# ------------------------------ GET & SET FUNCTIONS ------------------------------

def getStatsByUsername(username)->Stats:
   for stat in stats :
      if stat.username == username:
         return stat
   return None

# ------------------------------ ERRORS FUNCTIONS ------------------------------
def notFound(name):
   return make_response(jsonify({'error': f'{name} not found'}),400)


# ------------------------------ ENDPOINTS ------------------------------
@app.route("/", methods=['GET'])
def home():
   return make_response(jsonify({'message':'stats service api root'}))

@app.route("/stats", methods=['GET'])
def get_stats():
   return make_response(Stats.schema().dumps(stats, many=True),200)

@app.route("/stats/<username>",methods=['GET'])
def get_stats_by_username(username):
   stat = getStatsByUsername(username)
   if stat : return make_response(stat.to_json(),200)
   return notFound("stats for user")

@app.route("/stats/<username>/win",methods=['POST'])
def countWin(username):
   stat = getStatsByUsername(username)
   if not(stat) : return notFound("stats")
   stat.gamestats.win += 1
   return make_response(jsonify({'success': 'number of win incremented by one',"current wins":stat.gamestats.win}),200)

@app.route("/stats/win",methods=['POST'])
def countLose(username):
   body = request.json
   try :
      credentials:StatAndUser = StatAndUser.from_dict(body)
   except :
      sample_request = StatAndUser("matteo","pokefumi").to_dict()
      return make_response(jsonify({
         'error': "incorrect request",
         "sample-request-body":sample_request,
         "your-request-body": body
         }),400)

   
   stat = getStatsByUsername(credentials.username)
   if not(stat) : return notFound("stats")
   if not(len([gamestat for gamestat in stat.gamestats if gamestat.game_id == credentials.game_id]) > 0) :
      stat.gamestats.append(GameStats(game_id=credentials.game_id,win=0,lose=1))
   #TODO : increment lose  of the game_id
   return make_response(jsonify({'success': 'number of lose incremented by one',"current lose":stat.gamestats.lose}),200)


@app.route("/stats",methods=['POST'])
def create_stat():
   
   body = request.json
   try :
      credentials:StatAndUser = StatAndUser.from_dict(body)
   except :
      sample_request = StatAndUser("matteo","pokefumi").to_dict()
      return make_response(jsonify({
         'error': "incorrect request",
         "sample-request-body":sample_request,
         "your-request-body": body
         }),400)


   stat = getStatsByUsername(credentials.username)
   if stat : return make_response(jsonify({'error': 'stats already exists'}),400)

   stat = Stats(username=credentials.username,gamestats=GameStats(game_id=credentials.game_id,win=0,lose=0))
   return make_response(jsonify({'success': 'stats created'}),200)


if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)

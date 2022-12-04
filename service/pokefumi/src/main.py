# Server imports
import json
import time
import requests
from uuid import uuid4
import random
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
PORT_shop = os.getenv('PORT_SHOP')
HOST = os.getenv('HOST')

# ------------------------------ MODELS ------------------------------

from models import Round,Match,PokemonStats,Pokemon,DualPlayers,Move

# ------------------------------ VARIABLES ------------------------------

PORT = PORT_shop

with open('{}/db/matches.json'.format("."), "r") as jsf:
   matches_dict = json.load(jsf)["matches"]
   matches:list[Match] = Match.schema().load(matches_dict, many=True) 
   
   past_matches_dict = json.load(jsf)["past_matches"]
   past_matches:list[Match] = Match.schema().load(past_matches_dict, many=True) 


with open('{}/db/pokemon.json'.format("."), "r") as jsf:
   pokemons_dict = json.load(jsf)["pokemons"]
   pokemons:list[Pokemon] = Pokemon.schema().load(pokemons_dict, many=True) 


def generateId():
   return str(uuid4().int)

# ------------------------------ GET & SET FUNCTIONS ------------------------------

def getMatchById(matchid):
   for match in matches :
      if match.match_id == matchid :
         return match
   return None

def getPokemonById(pokemonid):
   for pokemon in pokemons :
      if pokemon.match_id == pokemonid :
         return pokemon
   return None

def determineBestPokemon(pokemon1,pokemon2):
   """Determine the best pokemon between pokemon1 and pokemon2"""
   return random.randint(0,2)
# ------------------------------ ERRORS FUNCTIONS ------------------------------
def notFound(name):
   return make_response(jsonify({'error': f'{name} not found'}),400)

def checkNot3Matches():
   """Check if the player has less than 3 matches"""
   return True

# ------------------------------ ENDPOINTS ------------------------------
@app.route("/", methods=['GET'])
def home():
   return make_response(jsonify({'message':'shop service api root'}))

@app.route("/matches", methods=['GET'])
def get_match():
   return make_response(Match.schema().dumps(matches, many=True),200)

@app.route("/matches/<matchid>",methods=['GET'])
def get_match_by_id(match_id):
   match = getMatchById(match_id)
   if match : return make_response(match.to_json(),200)
   return notFound("match")

@app.route("/matches",methods=['POST'])
def create_match():
   """
   need :
   player1
   player2

   check :
   pour chaque joueurs ceux-ci n'ont pas plus de 3 matchs simultanés
   """
   if not checkNot3Matches() : return make_response(jsonify({'error': 'a player already has 3 matches occuring'}),400)

   body = request.json
   try :
      players = DualPlayers.from_dict(body)
   except :
      sample_request = DualPlayers("player1","player2").to_dict()
      return make_response(jsonify({
         'error': "incorrect request",
         "sample-request-body":sample_request,
         "your-request-body": body
         }),400)

   new_match = Match(
      match_id=uuid4(),
      status="CREATED",
      round_history=[],
      players=players,
      current_round=Round(
         player1_item_used=None,
         player2_item_used=None,
         winner=None
      ),
      winner=None
   )

   matches.append(new_match)

   return make_response(jsonify({'success': 'match created',"match":new_match.to_dict()}),200)

@app.route("/matches/<matchid>/play",methods=['GET'])
def who_need_to_play(match_id):
   match = getMatchById(match_id)
   if not(match) : return notFound("match")

   liste = []
   current_round = match.current_round
   if not(current_round.player1_item_used) : liste.append(match.players.player1)
   if not(current_round.player2_item_used) : liste.append(match.players.player2)

   return make_response(jsonify({'who_need_to_play': liste}),200)

@app.route("/matches/<matchid>/play",methods=['POST'])
def play_pokemon(match_id):
   """
   need :
   item_id
   player_id
   
   check :
   if the match is valid | ok
   if the player is valid | ok
   
   if the player has already played | ok
   if the item is in player's inventory
   """
   #check if the match is valid
   match = getMatchById(match_id)
   if not(match) : return notFound("match")

   #check if the player is valid
   body = request.json
   try :
      player_move:Move = Move.from_dict(body)
   except :
      sample_request = Move("player1","pikachu1234","pikachu").to_dict()
      return make_response(jsonify({
         'error': "incorrect request",
         "sample-request-body":sample_request,
         "your-request-body": body
         }),400)
   players:DualPlayers = match.players
   if not(players.contains(player_move.player_id)) : return notFound("player")
   player_key = players.get_key(player_move.player_id)

   #check if the player has already played
   current_round = match.current_round
   if getattr(current_round,player_key+"_item_used") : return make_response(jsonify({'error': 'the player has already played'}),400)
   else :
      setattr(current_round,player_key+"_item_used",player_move.in_game_item_id)
      if (current_round.player1_item_used and current_round.player2_item_used) :

         #determine the winner
         pokemon1 = getPokemonById(current_round.player1_item_used)
         pokemon2 = getPokemonById(current_round.player2_item_used)
         winner = determineBestPokemon(pokemon1,pokemon2)
         match.winner = winner

         match.round_history.append(current_round)
         match.current_round = Round(
            player1_item_used=None,
            player2_item_used=None,
            winner=None
         )

         # if all the rounds are finished
         if len(match.round_history) == 3 :
            match.status = "FINISHED"
            past_matches.append(match)
            matches.remove(match)





if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)
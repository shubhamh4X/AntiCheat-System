from flask import Flask, jsonify, request
from pymongo import MongoClient
import redis
import datetime

app = Flask(__name__)

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["anti_cheat_system"]
cheat_reports = db["cheat_reports"]
player_reputation = db["player_reputation"]
global_bans = db["global_bans"]

# Redis Connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

@app.route('/report-cheat', methods=['POST'])
def report_cheat():
    data = request.json
    player_id = data.get("player_id")
    cheat_type = data.get("cheat_type")

    cheat_reports.insert_one({"player_id": player_id, "cheat_type": cheat_type})
    redis_client.set(f"cheat_{player_id}", cheat_type, ex=300)  # Cache for 5 mins

    return jsonify({"message": f"Cheat report stored for {player_id}"}), 201

@app.route('/update-reputation', methods=['POST'])
def update_reputation():
    data = request.json
    player_id = data.get("player_id")
    change = data.get("change")

    player = player_reputation.find_one({"player_id": player_id})
    new_reputation = (player["reputation"] if player else 100) + change

    player_reputation.update_one({"player_id": player_id}, {"$set": {"reputation": new_reputation}}, upsert=True)
    return jsonify({"message": f"Reputation updated for {player_id}"}), 200

@app.route('/global-bans', methods=['GET'])
def get_global_bans():
    bans = list(global_bans.find({}, {"_id": 0}))
    return jsonify({"global_bans": bans})

@app.route('/ban-player', methods=['POST'])
def ban_player():
    data = request.json
    player_id = data.get("player_id")
    reason = data.get("reason")

    global_bans.insert_one({"player_id": player_id, "reason": reason, "timestamp": datetime.datetime.utcnow()})
    return jsonify({"message": f"Player {player_id} globally banned"}), 201

if __name__ == '__main__':
    app.run(debug=True, port=5000)

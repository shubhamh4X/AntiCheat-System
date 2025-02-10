from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["anti_cheat_system"]
db.create_collection("cheat_reports")
db.create_collection("player_reputation")
db.create_collection("global_bans")

print("MongoDB database and collections created successfully!")

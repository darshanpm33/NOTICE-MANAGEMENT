from pymongo import MongoClient

print("Checking MongoDB Connection...\n")

try:
    # 👉 Replace with your MongoDB URL
    client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)

    # This command forces connection check
    client.server_info()

    print("MongoDB Connected Successfully!")

    # Optional: list databases
    print("Databases:", client.list_database_names())

except Exception as e:
    print("MongoDB Connection Failed!")
    print("Error:", e)

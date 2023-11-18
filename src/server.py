from fastapi import FastAPI, HTTPException
from pymongo import MongoClient

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["dyte"]  # Replace with your actual database name
collection = db["dyte"]

@app.post("/")
async def handle_logs(data: dict):
    try:
        print("Received JSON data:")
        print(data)

        # Insert the data into MongoDB
        collection.insert_one(data)

        return {"message": "JSON data received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing JSON data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)

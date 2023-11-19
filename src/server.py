from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser

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
        
        # Add timestamp field as a datetime object
        data["tObj"] = parser.parse(data["timestamp"])

        data['pRID'] = data['metadata']['parentResourceId']
        # Insert the data into MongoDB
        collection.insert_one(data)

        return {"message": "JSON data received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing JSON data: {str(e)}")

@app.get("/filtered_logs/")
async def filtered_logs(
    level: str = Query(None, title="Log Level"),
    resourceId: str = Query(None, title="Resource ID"),
    start_timestamp: datetime = Query(None, title="Start Timestamp"),
    end_timestamp: datetime = Query(None, title="End Timestamp"),
    traceId: str = Query(None, title="Trace ID"),
    spanId: str = Query(None, title="Span ID"),
    commit: str = Query(None, title="Commit"),
    pRID: str = Query(None, title="Parent Resource ID"),
):
    filters = {
        key: value
        for key, value in locals().items()
        if key not in ["self", "filters"] and value is not None
    }
    
    # Update timestamp filters to use $gte and $lte for the range
    if start_timestamp:
        filters["tObj"] = {"$gte": start_timestamp, "$lte": end_timestamp}
        del filters['start_timestamp']
        del filters['end_timestamp']
    print(filters)
    c = collection.find(filters, {'_id': False, 'pRID': False, 'tObj': False})
    op = list()
    for _ in c: op.append(_)
    return op

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)

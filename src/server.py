from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from datetime import datetime
from dateutil import parser
from kafka import KafkaProducer, KafkaConsumer
import json
from threading import Thread
from bson import ObjectId
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS for all origins (you might want to restrict this in a production environment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with the appropriate list of allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["dyte"]  # Replace with your actual database name
collection = db["dyte"]

class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

# Kafka configuration
kafka_bootstrap_servers = 'localhost:9092'
kafka_topic = 'dyte-logs'

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v, cls=MongoEncoder).encode('utf-8')
)

def kafka_producer_worker(data):
    producer.send(kafka_topic, value=data)

# Kafka Consumer
consumer = KafkaConsumer(
    kafka_topic,
    bootstrap_servers=kafka_bootstrap_servers,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def kafka_consumer_worker():
    for message in consumer:
        # Process the Kafka messages as needed
        print(f"Received message: {message.value}")
        data = message.value
        # Add timestamp field as a datetime object
        data["tObj"] = parser.parse(data["timestamp"])
        
        data['pRID'] = data['metadata']['parentResourceId']
        # Insert the data into MongoDB
        collection.insert_one(data)
        print("Stored in DB")

# Start Kafka Consumer in a separate thread
consumer_thread = Thread(target=kafka_consumer_worker)
consumer_thread.start()

@app.post("/")
async def handle_logs(data: dict):
    try:
        print("Received JSON data:")
        print(data)
        
        # Produce the data to Kafka in a separate thread
        kafka_producer_thread = Thread(target=kafka_producer_worker, args=(data,))
        kafka_producer_thread.start()
        
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

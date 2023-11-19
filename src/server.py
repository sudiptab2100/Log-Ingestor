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

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client["dyte"]
collection = db["logs"]
collection.create_index([('message', 'text')])

# Custom JSON encoder for handling ObjectId
class MongoEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

# Kafka configuration
kafka_bootstrap_servers = 'localhost:9092'
kafka_topic = 'dyte-logs'

# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=kafka_bootstrap_servers,
    value_serializer=lambda v: json.dumps(v, cls=MongoEncoder).encode('utf-8')
)

# Kafka Consumer
consumer = KafkaConsumer(
    kafka_topic,
    bootstrap_servers=kafka_bootstrap_servers,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def kafka_producer_worker(data):
    producer.send(kafka_topic, value=data)

def kafka_consumer_worker():
    for message in consumer:
        try:
            # Process the Kafka messages as needed
            print(f"Received message: {message.value}")
            data = message.value
            data["tObj"] = parser.parse(data["timestamp"])  # Add timestamp field as a datetime object
            data['pRID'] = data['metadata']['parentResourceId']  # Copying metadata.parentResourceId in pRID for easy filtering
            collection.insert_one(data)  # Insert the data into MongoDB
            print("Stored in DB")

        except Exception as e:
            print(f"Error processing Kafka message: {str(e)}")

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
    search_text: str = Query(None, title="Search Text"),
):
    # Build filters based on query parameters
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

    # Add text search
    if search_text:
        filters["$text"] = {"$search": search_text}
        del filters['search_text']

    print(filters)
    
    # Fetch data from MongoDB based on filters
    result = list(collection.find(filters, {'_id': False, 'pRID': False, 'tObj': False}))
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)

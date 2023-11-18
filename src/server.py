from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/")
async def handle_logs(data: dict):
    try:
        print("Received JSON data:")
        print(data)

        return {"message": "JSON data received successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing JSON data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=3000)

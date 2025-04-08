from fastapi import FastAPI
import uvicorn
import os

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Bot is running!"}

def run_webserver():
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("webserver:app", host="0.0.0.0", port=port, reload=False)

import uvicorn
from fastapi import FastAPI
from routers import todoist, water_logger

#initialize
app = FastAPI(title="Life Sync", version="1.0")

#routers
app.include_router(todoist.router)
app.include_router(water_logger.router)


@app.get("/")
def read_root():
    return {"message: Welcome to Life Sync!"}

@app.get("/healthz")
def health_check():
    return {}

#tools
#dummy tool
@app.get("/status")
def get_status():
    """
    Returns the current status of the user
    """
    return{
        "battery": "100%",
        "mood": "Productive",
        "alerts": ["Drink water"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from app.api.routes import router

app = FastAPI(
    title="Cloud Operations Agent",
    description="Agentic AI for OpenStack Cloud Operations",
    version="1.0.0"
)

# Mount static files
app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")

app.include_router(router)

@app.get("/")
async def root():
    return {"message": "Welcome to Cloud Operations Agent"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

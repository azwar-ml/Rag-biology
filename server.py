import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logger import get_logger
from api.routes import router as api_router

logger = get_logger(__name__)

app = FastAPI(
    title="NCAI Class 11 Biology RAG API",
    description="API for querying the Class 11 Biology RAG system.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect the modular routes
app.include_router(api_router)

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI Server Started Successfully.")

@app.get("/")
def read_root():
    return {"message": "Welcome to the API. Visit /docs for Swagger UI."}

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
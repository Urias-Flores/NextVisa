import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST before any other imports
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Now import other modules
from datetime import datetime
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from controllers.configuration_controller import router as configuration_router
from controllers.applicant_controller import router as applicant_router
from controllers.re_schedule_controller import router as re_schedule_router

app = FastAPI(
    title="QuickVisa API",
    description="API for managing visa applications and applicants",
    version="0.0.1",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "QuickVisa API is running"}

@app.get("/status")
def get_status():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Quick Visa API",
        "version": "0.0.1",
        "database": "supabase - postgres"
    }

# Register routers
app.include_router(configuration_router, prefix="/api/configuration", tags=["configuration"])
app.include_router(applicant_router, prefix="/api/applicants", tags=["applicants"])
app.include_router(re_schedule_router, prefix="/api/re-schedules", tags=["re-schedules"])
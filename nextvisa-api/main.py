from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
import logging
import sys
from utils.logger_formater import UvicornStyleFormatter

# Load environment variables FIRST before any other imports
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Configure logging to match uvicorn style
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(UvicornStyleFormatter())

logging.basicConfig(
    level=logging.INFO,
    handlers=[handler]
)

# Now import other modules
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.configuration_controller import router as configuration_router
from controllers.applicant_controller import router as applicant_router
from controllers.re_schedule_controller import router as re_schedule_router
from controllers.re_schedule_log_controller import router as re_schedule_log_router
from lib.scheduler import scheduler

logger = logging.getLogger(__name__)

# Background lifecycle
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Scheduler")
    try:
        scheduler.start()
    except Exception as e:
        logger.error(f"Error starting Scheduler: {e}", exc_info=True)
    
    yield
    
    logger.info("Stopping Scheduler")
    try:
        scheduler.stop()
    except Exception as e:
        logger.error(f"Error stopping Scheduler: {e}", exc_info=True)

app = FastAPI(
    title="NextVisa API",
    description="API for managing visa applications and applicants",
    version="0.0.1",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=
    [
        "http://localhost:5173",
        "https://nextvisa.uf-technology.com"
    ], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "NextVisa API is running"}

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
app.include_router(re_schedule_log_router)
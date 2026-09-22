import traceback
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.api.routes import router
from app.database.db import Base, engine, SessionLocal
from app.database.models import Task
from app.database.seed import seed_database

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="English-First Adaptive Child-Friendly Language Support MVP Backend",
    version="2.2"
)

# CORS middleware — must be added BEFORE the global exception handler
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"]
)

# Global exception handler — ensures CORS headers are always present,
# even when an unhandled exception causes a 500. Without this the
# browser sees a missing Access-Control-Allow-Origin and reports CORS.
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    origin = request.headers.get("origin", "")
    allowed = settings.cors_origins_list
    logger.error("Unhandled exception on %s %s:\n%s", request.method, request.url, traceback.format_exc())
    headers = {}
    if origin in allowed:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal server error: {str(exc)}"},
        headers=headers
    )

# Register routes
app.include_router(router)

@app.on_event("startup")
def startup_event():
    # Ensure tables exist (including new TaskResult table)
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if database is empty
    db = SessionLocal()
    try:
        task_count = db.query(Task).count()
        if task_count == 0:
            print("Database empty on startup. Running automated seed...")
            seed_database()
        else:
            # Backfill TaskResult records for any existing completed sessions
            from app.services.session_service import session_service
            backfilled = session_service.backfill_task_results(db)
            if backfilled > 0:
                print(f"Startup backfill: Created {backfilled} TaskResult records from existing sessions.")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

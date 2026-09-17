from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router
from app.database.db import Base, engine, SessionLocal
from app.database.models import Task
from app.database.seed import seed_database

app = FastAPI(
    title=settings.app_name,
    description="English-First Adaptive Child-Friendly Language Support MVP Backend",
    version="2.2"
)

# CORS middleware with restricted origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)

# Register routes
app.include_router(router)

@app.on_event("startup")
def startup_event():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    # Auto-seed if database is empty
    db = SessionLocal()
    try:
        task_count = db.query(Task).count()
        if task_count == 0:
            print("Database empty on startup. Running automated seed...")
            seed_database()
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

from fastapi import FastAPI
from app.api.routes.students import router as students_router
from app.db.base import Base
from app.db.database import engine

app = FastAPI(title="Opportunity Map API")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

app.include_router(students_router)

#cd ~/Projects/opportunity-map/opportunity-map-backend
#.venv/bin/python -m uvicorn app.main:app --reload

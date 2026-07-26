from fastapi import FastAPI
#from app.api.routes.students import router as students_router
from app.api.routes.dev_auth import router as dev_auth_router
from app.api.routes.profile import router as profile_router
from app.api.routes.opportunities import router as opportunities_router
from app.db.base import Base
from app.db.database import engine
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Opportunity Map API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

@app.get("/health")
def health_check():
    return {"status": "ok"}

#app.include_router(students_router)
app.include_router(dev_auth_router)
app.include_router(profile_router)

app.include_router(opportunities_router)

#cd ~/Projects/opportunity-map/opportunity-map-backend
# local dev entrypoint: .venv/bin/python -m uvicorn app.main:app --reload

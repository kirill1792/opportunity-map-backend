from fastapi import FastAPI

app = FastAPI(title="Opportunity Map API")


@app.get("/health")
def health_check():
    return {"status": "ok"}


#cd ~/Projects/opportunity-map/opportunity-map-backend
#.venv/bin/python -m uvicorn app.main:app --reload

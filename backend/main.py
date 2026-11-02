from fastapi import FastAPI
from database import engine, Base
from routers.auth import router as auth_router
from routers.habits import router as habits_router
from routers.dashboard import router as dashboard_router

app = FastAPI(
    title="Habit Tracker API",
    version="1.0.0"
)

Base.metadata.create_all(
    bind=engine
)

app.include_router(auth_router)
app.include_router(habits_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {
        "message": "Habit Tracker API is working!"
    }

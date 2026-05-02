from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import students
from database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

app.include_router(students.router)
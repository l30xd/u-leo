from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes import students
from routes.auth import router as auth_router
from database import engine, Base
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/etc/secrets/env"):
    ENV_PATH = "/etc/secrets/env"
elif os.path.exists("/etc/secrets/resend"):
    ENV_PATH = "/etc/secrets/resend"
elif os.path.exists("/etc/secrets/.env"):
    ENV_PATH = "/etc/secrets/.env"
else:
    ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

print(f"[INIT] Cargando desde: {ENV_PATH}")
print(f"[INIT] EMAIL_PASSWORD: {'*' * len(os.getenv('EMAIL_PASSWORD') or '')}")
print(f"[INIT] EMAIL_FROM: {os.getenv('EMAIL_FROM')}")

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(students.router)

app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "frontend"), html=True), name="frontend")

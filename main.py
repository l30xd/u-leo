from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from routes import students
from routes.auth import router as auth_router
from database import engine, Base
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists("/etc/secrets/resend"):
    ENV_PATH = "/etc/secrets/resend"
elif os.path.exists("/etc/secrets/env"):
    ENV_PATH = "/etc/secrets/env"
elif os.path.exists("/etc/secrets/.env"):
    ENV_PATH = "/etc/secrets/.env"
else:
    ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de FastAPI-Mail
mail_conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASSWORD"),
    MAIL_FROM=os.getenv("EMAIL_FROM"),
    MAIL_PORT=587,
    MAIL_SERVER="smtp.resend.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

@app.on_event("startup")
async def startup_event():
    app.state.fm = FastMail(mail_conf)

app.include_router(auth_router)
app.include_router(students.router)

app.mount("/", StaticFiles(directory=os.path.join(BASE_DIR, "frontend")), name="frontend")

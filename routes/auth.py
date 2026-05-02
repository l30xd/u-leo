import os
import random
import smtplib
from datetime import datetime, timedelta
from email.message import EmailMessage
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Header, Depends, status
from pydantic import BaseModel, EmailStr
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

router = APIRouter(prefix="/auth")

OTP_STORE: dict[str, dict] = {}
TOKEN_STORE: dict[str, dict] = {}

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    code: str

class AuthToken(BaseModel):
    token: str


def get_mail_configuration() -> dict:
    api_key = os.environ.get("SENDGRID_API_KEY")
    from_email = os.environ.get("SENDGRID_FROM_EMAIL", "noreply@tuapp.com")
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Falta configuración de SendGrid. "
                "Define SENDGRID_API_KEY en las variables de entorno."
            ),
        )

    return {
        "api_key": api_key,
        "from_email": from_email,
    }


def send_otp_email(email: str, code: str) -> None:
    config = get_mail_configuration()
    sg = SendGridAPIClient(config["api_key"])

    from_email = Email(config["from_email"])
    to_email = To(email)
    subject = "Código OTP para acceder al CRUD"
    content = Content("text/plain", f"Tu código OTP es: {code}\n\nIntroduce este código en la aplicación para poder acceder al CRUD.")

    mail = Mail(from_email, to_email, subject, content)

    try:
        response = sg.send(mail)
        if response.status_code not in [200, 201, 202]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo enviar el correo OTP.",
            )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo enviar el correo OTP. Verifica la configuración de SendGrid.",
        ) from exc


@router.post("/request-otp")
def request_otp(payload: OTPRequest):
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    OTP_STORE[payload.email] = {
        "code": code,
        "expires_at": expires_at,
    }
    send_otp_email(payload.email, code)
    return {"message": "Código OTP enviado al correo."}


@router.post("/verify-otp", response_model=AuthToken)
def verify_otp(payload: OTPVerify):
    otp_data = OTP_STORE.get(payload.email)
    if not otp_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP no solicitado o expirado.")

    if datetime.utcnow() > otp_data["expires_at"]:
        OTP_STORE.pop(payload.email, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código OTP expiró.")

    if otp_data["code"] != payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código OTP incorrecto.")

    token = str(uuid4())
    TOKEN_STORE[token] = {
        "email": payload.email,
        "expires_at": datetime.utcnow() + timedelta(hours=1),
    }
    OTP_STORE.pop(payload.email, None)
    return {"token": token}


def verify_token(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token no proporcionado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ", 1)[1]
    token_data = TOKEN_STORE.get(token)
    if not token_data or datetime.utcnow() > token_data["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data["email"]

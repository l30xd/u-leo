import os
import random
from datetime import datetime, timedelta
from uuid import uuid4
import requests

from fastapi import APIRouter, HTTPException, Header, Depends, status, Request
from pydantic import BaseModel, EmailStr

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


async def send_otp_email(request: Request, email: str, code: str) -> None:
    api_key = os.getenv("EMAIL_PASSWORD")
    from_email = os.getenv("EMAIL_FROM")
    
    print(f"[RESEND CONFIG] API Key: {'*' * 10}{api_key[-10:] if api_key else 'NOT SET'}")
    print(f"[RESEND CONFIG] From Email: {from_email}")
    
    if not api_key or not from_email:
        raise HTTPException(status_code=500, detail="Falta configuración de correo (EMAIL_PASSWORD y EMAIL_FROM)")
    
    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "from": from_email,
        "to": [email],
        "subject": "Código OTP para acceder al CRUD",
        "text": f"Tu código OTP es: {code}\n\nIntroduce este código en la aplicación para acceder al CRUD."
    }
    
    try:
        print(f"[RESEND] Enviando email a {email}...")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        print(f"[RESEND] Status: {response.status_code}")
        print(f"[RESEND] Response: {response.text}")
        response.raise_for_status()
        print("[RESEND] Email enviado exitosamente")
    except requests.RequestException as e:
        print("[RESEND API ERROR]", str(e))
        raise HTTPException(status_code=500, detail=f"Error Resend: {str(e)}")


@router.post("/request-otp")
async def request_otp(payload: OTPRequest, request: Request):
    email = payload.email.strip().lower()
    print(f"[REQUEST OTP] Email: {email}")
    code = f"{random.randint(100000, 999999)}"
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    OTP_STORE[email] = {
        "code": code,
        "expires_at": expires_at,
    }
    print(f"[REQUEST OTP] Code generated: {code}")
    await send_otp_email(request, email, code)
    print("[REQUEST OTP] Email sent successfully")
    return {"message": "Código OTP enviado al correo."}


@router.post("/verify-otp", response_model=AuthToken)
def verify_otp(payload: OTPVerify):
    email = payload.email.strip().lower()
    otp_data = OTP_STORE.get(email)
    if not otp_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP no solicitado o expirado.")

    if datetime.utcnow() > otp_data["expires_at"]:
        OTP_STORE.pop(email, None)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El código OTP expiró.")

    if otp_data["code"] != payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código OTP incorrecto.")

    token = str(uuid4())
    TOKEN_STORE[token] = {
        "email": email,
        "expires_at": datetime.utcnow() + timedelta(hours=24),  # Increased to 24 hours
    }
    OTP_STORE.pop(email, None)
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

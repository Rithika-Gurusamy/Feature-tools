import random
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

otp_store = {}

SMTP_SERVER = "://gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your-email@gmail.com"
SENDER_PASSWORD = "your-email-app-password"

class EmailRequest(BaseModel):
    email: EmailStr

class VerifyRequest(BaseModel):
    email: EmailStr
    otp: str

def send_email(to_email: str, otp: str):
    msg = MIMEText(f"Your one-time password is: {otp}")
    msg["Subject"] = "Your OTP Code"
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())

@app.post("/send-otp")
def request_otp(data: EmailRequest):
    otp = str(random.randint(100000, 999999))
    otp_store[data.email] = otp
    try:
        send_email(data.email, otp)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to send email")
    return {"message": "OTP sent successfully"}

@app.post("/verify-otp")
def verify_otp(data: VerifyRequest):
    stored_otp = otp_store.get(data.email)
    if not stored_otp or stored_otp != data.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    del otp_store[data.email]
    return {"message": "OTP verified successfully"}

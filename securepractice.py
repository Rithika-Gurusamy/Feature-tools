import secrets
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

MOCK_DATABASE = {
    "student@university.edu": {
        "email": "student@university.edu",
        "otp_code": None
    }
}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@app.post("/api/v1/auth/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest):
    target_email = payload.email.lower()
    user_record = MOCK_DATABASE.get(target_email)
    
    if user_record:
        secure_otp = "".join(secrets.choice("0123456789") for _ in range(6))
        user_record["otp_code"] = secure_otp
    else:
        pass

    return {
        "status": "success",
        "message": "If the account exists, a recovery code has been sent to your registered email."
    }

import secrets
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

MOCK_DATABASE = {
    "student@university.edu": {
        "email": "student@university.edu",
        "otp_code": None
    }
}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@app.post("/api/v1/auth/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(payload: ForgotPasswordRequest):
    target_email = payload.email.lower()
    user_record = MOCK_DATABASE.get(target_email)
    
    if user_record:
        secure_otp = "".join(secrets.choice("0123456789") for _ in range(6))
        user_record["otp_code"] = secure_otp
    else:
        _ = "".join(secrets.choice("0123456789") for _ in range(6))

    return {
        "status": "success",
        "message": "If the account exists, a recovery code has been sent to your registered email."
    }
import secrets
from fastapi import FastAPI, status, Request
from pydantic import BaseModel, EmailStr
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

MOCK_DATABASE = {
    "student@university.edu": {
        "email": "student@university.edu",
        "otp_code": None
    }
}

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

@app.post("/api/v1/auth/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/15 minutes")
async def forgot_password(request: Request, payload: ForgotPasswordRequest):
    target_email = payload.email.lower()
    user_record = MOCK_DATABASE.get(target_email)
    
    if user_record:
        secure_otp = "".join(secrets.choice("0123456789") for _ in range(6))
        user_record["otp_code"] = secure_otp
    else:
        _ = "".join(secrets.choice("0123456789") for _ in range(6))

    return {
        "status": "success",
        "message": "If the account exists, a recovery code has been sent to your registered email."
    }

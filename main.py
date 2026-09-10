import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI, status, HTTPException, Header
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Email and password are required"},
    )

@app.on_event("startup")
async def startup_event():
    print("Server running and connected to Supabase")

class UserCredential(BaseModel):
    email: str
    password: str

@app.post(
    "/auth/signup",
    status_code=status.HTTP_201_CREATED,
    summary="Sign up for an account"
)
def user_signup(user_credential: UserCredential):
    if user_credential.email.strip() == "" or user_credential.password.strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_up({
            "email": user_credential.email,
            "password": user_credential.password,
        })
        return {"message": "Signup successful", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    summary="User login"
)
def user_login(user_credential: UserCredential):
    if user_credential.email.strip() == "" or user_credential.password.strip() == "":
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Email and password are required"}
        )

    try:
        response = supabase.auth.sign_in_with_password({
            "email": user_credential.email,
            "password": user_credential.password,
        })
        return {
            "message": "Login successful", 
            "access_token": response.session.access_token, 
            "refresh_token": response.session.refresh_token
            }
    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid login credentials"}
        )

@app.get(
    "/public/info",
    status_code=status.HTTP_200_OK,
    summary="Public lobby, anyone can enter"
)
def public_lobby():
    return { "message": "Welcome stranger! This info is public." }

@app.get(
    "/protected/profile",
    status_code=status.HTTP_200_OK,
    summary="Private lobby, needs permission to enter."
)
def private_lobby(authorization: str = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "Access token required"}
        )
    
    token = authorization.split(" ")[1]

    return {"message": "Token received", "token": token}
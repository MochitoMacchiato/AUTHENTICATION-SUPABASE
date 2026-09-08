import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

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
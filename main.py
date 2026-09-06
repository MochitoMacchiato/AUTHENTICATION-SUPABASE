import os
from dotenv import load_dotenv
from supabase import create_client, Client
from fastapi import FastAPI

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Server running and connected to Supabase")
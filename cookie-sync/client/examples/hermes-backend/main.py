# examples/hermes-backend/main.py
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json
import os
from pathlib import Path

app = FastAPI(title="Hermes Browser Sync API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("HERMES_API_KEY", "your-secret-api-key")
STORAGE_STATE_PATH = os.getenv("STORAGE_STATE_PATH", "storage_state.json")

class Cookie(BaseModel):
    name: str
    value: str
    domain: str
    path: str = "/"
    secure: bool = False
    httpOnly: bool = False
    sameSite: str = "None"
    expirationDate: Optional[float] = None
    session: bool = True
    storeId: str = "0"
    hostOnly: bool = False

class CookieSyncPayload(BaseModel):
    domain: str
    cookies: List[Cookie]
    timestamp: str

class ConnectionTest(BaseModel):
    type: str = "connection_test"
    timestamp: str

def verify_api_key(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.replace("Bearer ", "")
    if token != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return token

@app.post("/api/browser-sync")
async def browser_sync(
    payload: CookieSyncPayload,
    api_key: str = Depends(verify_api_key)
):
    """
    Receive cookies from Hermes Browser Sync Extension and save as storage_state.json
    """
    try:
        # Convert to Playwright storage state format
        storage_state = {
            "cookies": [
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "domain": cookie.domain,
                    "path": cookie.path,
                    "secure": cookie.secure,
                    "httpOnly": cookie.httpOnly,
                    "sameSite": cookie.sameSite,
                    "expires": cookie.expirationDate if cookie.expirationDate else -1,
                    "url": f"https://{cookie.domain.lstrip('.')}{cookie.path}"
                }
                for cookie in payload.cookies
            ],
            "origins": []
        }
        
        # Load existing state if available
        if os.path.exists(STORAGE_STATE_PATH):
            with open(STORAGE_STATE_PATH, "r") as f:
                existing_state = json.load(f)
            
            # Merge cookies (update existing, add new)
            existing_cookies = existing_state.get("cookies", [])
            cookie_map = {
                (c["name"], c["domain"]): c 
                for c in existing_cookies
            }
            
            for cookie in storage_state["cookies"]:
                key = (cookie["name"], cookie["domain"])
                cookie_map[key] = cookie
            
            storage_state["cookies"] = list(cookie_map.values())
        
        # Save to file
        with open(STORAGE_STATE_PATH, "w") as f:
            json.dump(storage_state, f, indent=2)
        
        return {
            "success": True,
            "message": f"Synced {len(payload.cookies)} cookies for {payload.domain}",
            "timestamp": payload.timestamp
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-connection")
async def connection_test(
    payload: ConnectionTest,
    api_key: str = Depends(verify_api_key)
):
    """
    Test connection endpoint
    """
    return {
        "success": True,
        "message": "Connection successful",
        "timestamp": payload.timestamp
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

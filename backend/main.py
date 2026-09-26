from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import io
import csv
import secrets
from typing import List, Dict, Any
from okta_service import OktaService
from config import APP_USERNAME, APP_PASSWORD
import os
import traceback

app = FastAPI()

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP Basic Auth gate - every endpoint that can read/write Okta data requires
# this. Without it, anyone who can reach this port could create Okta users or
# add users to any group (including admin groups) with no credentials at all.
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    valid_username = secrets.compare_digest(credentials.username, APP_USERNAME)
    valid_password = secrets.compare_digest(credentials.password, APP_PASSWORD)
    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

print("[Main] Initializing FastAPI application...")
try:
    okta_service = OktaService()
    print("[Main] OK: OktaService initialized successfully")
except Exception as e:
    print(f"[Main] FAILED: Failed to initialize OktaService: {str(e)}")
    print(f"[Main] Traceback: {traceback.format_exc()}")
    raise

def parse_csv(contents: bytes) -> tuple[list[dict], list[str]]:
    """Parse CSV file and return rows and headers"""
    try:
        text = contents.decode('utf-8')
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        headers = reader.fieldnames or []
        return rows, headers
    except Exception as e:
        raise ValueError(f"Error parsing CSV: {str(e)}")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/groups")
def get_groups(user: str = Depends(verify_credentials)):
    """Fetch all groups from Okta"""
    try:
        groups = okta_service.get_groups()
        return {"success": True, "groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import/users")
async def import_users(
    file: UploadFile = File(...),
    user: str = Depends(verify_credentials),
):
    """Import new users to Okta"""
    print(f"[Audit] {user} started a new-user import ({file.filename})")
    try:
        contents = await file.read()
        rows, headers = parse_csv(contents)

        results = {
            "created": [],
            "duplicates": [],
            "errors": [],
            "total": len(rows)
        }

        required_fields = ["login", "firstName", "lastName", "email"]
        for field in required_fields:
            if field not in headers:
                raise HTTPException(status_code=400, detail=f"Missing required column: {field}")

        for idx, row in enumerate(rows):
            try:
                email = row.get("email", "").strip()
                if not email:
                    results["errors"].append({
                        "row": idx + 2,
                        "email": "empty",
                        "message": "Email field is empty"
                    })
                    continue

                # Check if user exists
                exists, user_id = okta_service.user_exists(email)
                if exists:
                    results["duplicates"].append({
                        "row": idx + 2,
                        "email": email,
                        "message": "User already exists"
                    })
                    continue

                # Clean row data - remove None for None strings
                user_data = {
                    k: (v.strip() if isinstance(v, str) and v else None)
                    for k, v in row.items()
                }
                success, user_id, message = okta_service.create_user(user_data)

                if success:
                    results["created"].append({
                        "email": email,
                        "user_id": user_id,
                        "message": message
                    })
                else:
                    results["errors"].append({
                        "row": idx + 2,
                        "email": email,
                        "message": message
                    })
            except Exception as e:
                results["errors"].append({
                    "row": idx + 2,
                    "email": row.get("email", "unknown"),
                    "message": str(e)
                })

        return {"success": True, "results": results}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/import/groups")
async def import_group_assignment(
    file: UploadFile = File(...),
    group_name: str = Form(...),
    user: str = Depends(verify_credentials),
):
    """Add existing users to group"""
    print(f"[Audit] {user} started a group import into '{group_name}' ({file.filename})")
    try:
        # Get group ID
        group_id = okta_service.get_group_by_name(group_name)
        if not group_id:
            raise HTTPException(status_code=400, detail=f"Group '{group_name}' not found")

        contents = await file.read()
        rows, headers = parse_csv(contents)

        if "userIdOrLogin" not in headers:
            raise HTTPException(status_code=400, detail="Missing required column: userIdOrLogin")

        results = {
            "added": [],
            "not_found": [],
            "already_member": [],
            "errors": [],
            "total": len(rows)
        }

        for idx, row in enumerate(rows):
            try:
                email = row.get("userIdOrLogin", "").strip()
                if not email:
                    results["errors"].append({
                        "row": idx + 2,
                        "email": "empty",
                        "message": "userIdOrLogin field is empty"
                    })
                    continue

                # Find user by email/login
                exists, user_id = okta_service.user_exists(email)
                if not exists:
                    results["not_found"].append({
                        "row": idx + 2,
                        "email": email,
                        "message": "User not found"
                    })
                    continue

                # Add user to group
                success, message = okta_service.add_user_to_group(user_id, group_id)

                if "already" in message.lower():
                    results["already_member"].append({
                        "email": email,
                        "message": message
                    })
                elif success:
                    results["added"].append({
                        "email": email,
                        "user_id": user_id,
                        "message": message
                    })
                else:
                    results["errors"].append({
                        "row": idx + 2,
                        "email": email,
                        "message": message
                    })
            except Exception as e:
                results["errors"].append({
                    "row": idx + 2,
                    "email": row.get("userIdOrLogin", "unknown"),
                    "message": str(e)
                })

        return {"success": True, "results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

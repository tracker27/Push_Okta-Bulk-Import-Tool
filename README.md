# Okta Bulk User Import Tool

A web-based tool for bulk importing users and managing group assignments in Okta.

## Features

- **New User Onboarding**: Create new users in Okta from a CSV file
- **Group Assignment**: Add existing users to groups in bulk
- **Real-time Results**: View detailed import results with success/error counts
- **Drag & Drop Upload**: Easy CSV file upload with validation
- **Interactive UI**: Clean, user-friendly interface built with React

## Prerequisites

- Python 3.9+
- Okta Organization, with either:
  - An OAuth Service App (client credentials / `private_key_jwt`) - **recommended, proven working**, or
  - A personal API token (fallback)

> **Note on Docker:** `docker-compose.yml` and the `Dockerfile`s are included but have **not been verified** in this environment. The setup below (plain Python) is the tested, working path and is recommended until the Docker path is validated. See [DOCKER_SETUP.md](DOCKER_SETUP.md) for the untested container instructions.

## Setup

### 1. Clone/Download the Project

```bash
cd bulk-import-tool
```

### 2. Environment Variables

Copy the example env file **into the backend folder** (the backend loads `.env` from its own working directory):

```bash
cp .env.example backend/.env
```

Edit `backend/.env` and add your Okta credentials (see comments in `.env.example` for OAuth app setup):

```
OKTA_DOMAIN=https://your-domain.okta.com
OKTA_CLIENT_ID=your_service_app_client_id
OKTA_PRIVATE_KEY={"kty": "RSA", ...}
```

### 3. Quick Start (Recommended)

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh stop.sh
./start.sh
```

This creates the backend virtual environment (first run only), starts the backend on port 8000 and the frontend on port 3000 in the background, and opens the browser.

To stop: run `stop.bat` (Windows) or `./stop.sh` (Mac/Linux).
To restart after a code change: run `restart.bat`, or `restart_and_logs.bat` to also tail the backend logs live.

### 4. Manual Setup (Alternative)

#### Backend

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Backend runs on http://localhost:8000. **Important:** run this from inside `backend/` so it picks up `backend/.env`, and note that `python main.py` does **not** auto-reload on code changes - restart the process manually after editing backend code.

#### Frontend (in a new terminal, from the project root)

The frontend is a single static file (`index.html` at the project root, plain HTML/CSS/JS - no build step needed):

```bash
python -m http.server 3000
```

Frontend runs on http://localhost:3000

> The `frontend/` folder contains an earlier React-based scaffold that is **not currently used/served**. The working UI is the root-level `index.html`.

## Usage

### New User Onboarding

1. Click "New User Onboarding"
2. Prepare a CSV file with columns:
   - **login** (required)
   - **firstName** (required)
   - **lastName** (required)
   - **email** (required)
   - Other optional fields: title, phone, department, etc.
3. Upload the CSV
4. View results showing created users, duplicates, and errors

### Add Users to Group

1. Click "Add to Group"
2. Select the target group from the dropdown
3. Prepare a CSV file with column:
   - **userIdOrLogin** (user email)
4. Upload the CSV
5. View results showing added users, not found, and errors

## CSV Templates

### New User Template
```csv
login,firstName,lastName,email,title,department
jdoe@company.com,John,Doe,jdoe@company.com,Engineer,Engineering
asmith@company.com,Alice,Smith,asmith@company.com,Manager,Engineering
```

### Group Assignment Template
```csv
userIdOrLogin
jdoe@company.com
asmith@company.com
```

## API Endpoints

### GET /api/health
Health check endpoint

### GET /api/groups
Fetch all groups from Okta

### POST /api/import/users
Create new users in Okta
- Form data: `file` (CSV)

### POST /api/import/groups
Add existing users to a group
- Form data: `file` (CSV), `group_name` (string)

## Project Structure

```
bulk-import-tool/
├── index.html                # The actual frontend (static HTML/CSS/JS, served as-is)
├── start.bat / start.sh      # Start backend + frontend (recommended)
├── stop.bat / stop.sh        # Stop backend + frontend
├── restart.bat               # Stop + start (after a code change)
├── restart_and_logs.bat      # Restart and tail backend logs live
├── backend/
│   ├── main.py               # FastAPI app (run directly via venv, no auto-reload)
│   ├── okta_service.py       # Okta API integration (OAuth + user/group logic)
│   ├── config.py             # Configuration
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Okta credentials (create from .env.example, gitignored)
├── frontend/                 # Legacy React scaffold - NOT currently used/served
├── docker-compose.yml        # Docker setup (untested in this environment)
├── DOCKER_SETUP.md           # Docker instructions (untested - see note in Prerequisites)
└── README.md                 # This file
```

## Error Handling

The tool provides detailed error reporting:

- **New User Flow**: Reports duplicates (user exists) and creation errors
- **Group Assignment**: Reports users not found and group membership errors
- All errors are shown in a detailed results table with row numbers and messages

## Security Considerations

- API token is read from environment variables (not hardcoded)
- CORS is configured for localhost only
- CSV files are validated before processing
- No sensitive data is logged or stored

## Troubleshooting

### Backend Connection Error
- Ensure the backend is running: check `backend\backend_error.txt` for startup errors (this is where OAuth/auth failures show up)
- Check if port 8000 is in use: `netstat -an | findstr 8000` (Windows) or `lsof -i :8000` (Mac/Linux)
- Verify `backend/.env` exists and has correct Okta credentials
- **Remember:** `python main.py` does not auto-reload - after editing backend code, run `restart.bat` / `./stop.sh && ./start.sh`, or the fix will not take effect

### Frontend Not Loading
- Ensure something is serving `index.html` on port 3000 (`python -m http.server 3000` from the project root)
- Check if port 3000 is already in use by another process
- Check browser console for errors (F12)

### Okta API Errors
- Verify credentials are valid in `backend/.env`
- Check Okta domain format: `https://your-domain.okta.com`
- If using the OAuth service app: the token request must include `scope` matching exactly what's granted under the app's "Okta API Scopes" tab (`okta.users.manage okta.users.read okta.groups.manage okta.groups.read`) - omitting scope causes a `consent_required` error even if scopes show as "Granted" in the console
- If using a personal API token instead: ensure it hasn't expired/been revoked (`401` from `/api/groups` or `/api/import/users` is the symptom)

## Future Improvements

- [ ] Batch API calls for better performance
- [ ] User attribute mapping/transformation
- [ ] Scheduled imports
- [ ] Import history/audit log
- [ ] Advanced filtering and search in results
- [ ] Export results to Excel
- [ ] Multi-group assignment in one import

## License

MIT

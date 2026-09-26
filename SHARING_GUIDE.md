# 🚀 Share Okta Bulk Import Tool with Your Team

## For Team Members: Getting Started (5 minutes)

> Note: this tool runs as a plain Python backend + a static HTML frontend - **Docker is not required** (the Docker files in this repo are unverified, see [DOCKER_SETUP.md](DOCKER_SETUP.md)).

### 1. Prerequisites
Install **Python 3.9+**: https://www.python.org/downloads/

### 2. Get the Code
Ask your team lead for the repository link, then:
```bash
git clone <repository-url>
cd bulk-import-tool
```

### 3. Get Credentials
Request the Okta credentials from your team lead (either an OAuth service app's client ID + private key, or a personal API token).

Place them in a `.env` file **inside the `backend/` folder** (the backend loads its own working directory's `.env`):
```
bulk-import-tool/
├── backend/
│   └── .env              <-- HERE
├── index.html
└── ...
```

### 4. Start the Tool

**On Windows:**
```bash
start.bat
```

**On Mac/Linux:**
```bash
chmod +x start.sh stop.sh
./start.sh
```

This sets up the backend's Python virtual environment on first run, then starts the backend (port 8000) and frontend (port 3000) in the background.

### 5. Use the Tool
Open your browser: **http://localhost:3000**

To stop: `stop.bat` (Windows) or `./stop.sh` (Mac/Linux).
To restart after pulling new code: `restart.bat`, or `restart_and_logs.bat` to also watch the backend logs live.

Done! 🎉

---

## For Team Leads: Sharing the Tool

### Step 1: Prepare the Repository

```bash
# Push to GitHub, GitLab, or your Git server
git add .
git commit -m "Update Okta Bulk Import Tool"
git push

# Make sure .env is in .gitignore (it should be)
cat .gitignore | grep ".env"
```

### Step 2: Create a Secure Credentials File

**Option A: Share via 1Password/LastPass (Recommended)**
1. Create a vault item with the `backend/.env` file contents
2. Share with team members who need access

**Option B: Email Securely**
Send the `.env` file contents encrypted or via your company's secure file sharing

**Option C: Use Environment Variables**
Share a script that sets environment variables (example format - use your own values, never real credentials in docs):
```bash
export OKTA_DOMAIN="https://your-org.okta.com"
export OKTA_CLIENT_ID="your_service_app_client_id"
export OKTA_PRIVATE_KEY="..."
```

### Step 3: Share Instructions

Send your team this message:

---

### 📢 Team Announcement

Hey team! 👋

We've created an **Okta Bulk Import Tool** to make user management easier. Here's how to use it:

**Requirements:**
- Python 3.9+ (install if you don't have it)

**Quick Start:**
1. Clone the repo: `git clone <your-url>`
2. Get `backend/.env` file from [PERSON/LOCATION]
3. Run `./start.sh` (Mac/Linux) or `start.bat` (Windows)
4. Open http://localhost:3000

**Features:**
- ✅ Create new Okta users in bulk from CSV
- ✅ Add existing users to groups in bulk from CSV
- ✅ Real-time results and error reporting

**Need Help?**
- Check `README.md` for detailed setup instructions
- Check logs: `backend\backend_log.txt` and `backend\backend_error.txt`
- Ask [PERSON] for questions

Let's go! 🚀

---

### Step 4: Ongoing Maintenance

**Update Credentials**
If you need to rotate API credentials:
1. Generate new Okta service account credentials
2. Update `backend/.env`
3. Share with team again (via secure method)
4. Team members restart: `restart.bat` (Windows) or `./stop.sh && ./start.sh` (Mac/Linux)

**Code Updates**
When you update the tool:
```bash
git pull
```
Then restart (`restart.bat` or `./stop.sh && ./start.sh`) - **plain `python main.py` does not auto-reload**, so a restart is required for backend code changes to take effect.

---

## Deployment Options

### Option 1: Local Python (Current - Easy for Small Teams)
- ✅ Simple setup, no Docker needed
- ✅ No server needed
- ❌ Everyone runs their own copy
- ❌ Not accessible remotely

### Option 2: Shared Server (Internal Network)
- ✅ One central instance
- ✅ Everyone accesses same tool
- ❌ Requires server setup

**Setup:**
```bash
# On internal server
ssh user@internal-server.com
git clone <repo>
cd bulk-import-tool
chmod +x start.sh stop.sh
./start.sh
```

Access at: `http://internal-server.com:3000`

### Option 3: Docker / Cloud Deployment (Unverified)
`docker-compose.yml` and `Dockerfile`s exist in this repo for a containerized/cloud path (Heroku, AWS, Azure, etc.), but they have **not been tested** - see the warning at the top of [DOCKER_SETUP.md](DOCKER_SETUP.md). Validate the Docker build locally before relying on it for deployment.

---

## Security Best Practices

### ✅ DO
- Keep `.env` file **secret**
- Share credentials via **secure channels** (1Password, LastPass, etc.)
- Use **environment variables** in production
- Rotate credentials **regularly**
- Audit **who has access**

### ❌ DON'T
- Commit `.env` to Git
- Share credentials via email/Slack without encryption
- Hardcode credentials in code
- Leave credentials on shared machines
- Share production credentials with test team

---

## Troubleshooting for Your Team

### "Python not found"
→ Install Python 3.9+ from https://www.python.org/downloads/ (check "Add to PATH" during install)

### "Port 3000 already in use"
Something else is using port 3000. Stop it, or run the frontend on another port manually:
```bash
python -m http.server 3001
```
Then open `http://localhost:3001` instead.

### "Can't connect to backend"
Check `backend\backend_error.txt` and `backend\backend_log.txt` for the actual error (these are written by `start.bat`/`start.sh`).

### ".env file not found"
Make sure it's at **`backend/.env`** (not the project root) and ask your team lead for a copy.

---

## Questions?

For detailed information, see:
- `README.md` - Full setup, usage, and troubleshooting documentation
- `DOCKER_SETUP.md` - Docker documentation (unverified, optional path)

Happy importing! 🎉

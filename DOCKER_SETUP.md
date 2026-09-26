# Okta Bulk Import Tool - Docker Setup

> ⚠️ **Unverified path.** This project was developed and tested without Docker actually installed - the backend runs as a plain Python process (`python main.py` via a venv) and the frontend is a static `index.html` served with `python -m http.server`. The instructions below have **not been confirmed to work**. For the proven setup, see the main [README.md](README.md) and run `start.bat` / `./start.sh`. Use this guide only if you want to build out and test the Docker path yourself.

This guide explains how to run the Okta Bulk Import Tool using Docker and share it with your team.

## Prerequisites

- **Docker**: [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Docker Compose**: Included with Docker Desktop
- **Okta Credentials**: Your service account credentials from `.env`

## Quick Start

### 1. Clone/Download the Repository
```bash
git clone <your-repo-url>
cd bulk-import-tool
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory with your Okta credentials:

```bash
OKTA_DOMAIN=https://your-domain.okta.com
OKTA_CLIENT_ID=your_service_app_client_id
OKTA_PRIVATE_KEY={"kty": "RSA", "use": "sig", ... }
APP_USERNAME=your_chosen_username
APP_PASSWORD=your_chosen_password
```

**OR** copy your existing `.env` file to the root:
```bash
cp backend/.env .env
```

### 3. Build and Run with Docker Compose

```bash
docker-compose up --build
```

This command:
- ✅ Builds the backend Docker image
- ✅ Builds the frontend Docker image
- ✅ Starts both services on a shared network
- ✅ Backend runs on `http://localhost:8000`
- ✅ Frontend runs on `http://localhost:3000`

### 4. Access the Tool

Open your browser and navigate to:
```
http://localhost:3000
```

### 5. Stop the Services

```bash
docker-compose down
```

## Sharing with Coworkers

### Option A: Share Docker Repository (Easiest)

1. **Push to Git**: Commit the Dockerfile and docker-compose.yml to your repo
2. **Share Instructions**: Send coworkers this guide
3. **Coworkers Run**:
   ```bash
   git clone <your-repo-url>
   cd bulk-import-tool
   cp backend/.env .env  # If they have their own .env
   docker-compose up --build
   ```

### Option B: Deploy to Cloud (Recommended for Team Access)

#### Deploy to Heroku (Free tier available)

1. **Install Heroku CLI**:
   ```bash
   brew install heroku/brew/heroku  # macOS
   # or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Create Heroku App**:
   ```bash
   heroku login
   heroku create your-app-name
   ```

3. **Set Environment Variables**:
   ```bash
   heroku config:set OKTA_DOMAIN=https://your-domain.okta.com
   heroku config:set OKTA_CLIENT_ID=your_service_app_client_id
   heroku config:set OKTA_PRIVATE_KEY='{"kty": "RSA", ...}'
   heroku config:set APP_USERNAME=your_chosen_username
   heroku config:set APP_PASSWORD=your_chosen_password
   ```

4. **Create Heroku.yml** (in project root):
   ```yaml
   build:
     docker:
       backend: backend/Dockerfile
       frontend: frontend/Dockerfile
   run:
     web: backend
   ```

5. **Deploy**:
   ```bash
   git push heroku main
   ```

#### Or Deploy to AWS/Google Cloud/Azure

Follow their Docker deployment guides:
- **AWS**: ECS or App Runner
- **Google Cloud**: Cloud Run
- **Azure**: Container Instances

### Option C: Deploy to Internal Server

If you have an internal server/VM:

```bash
# SSH to server
ssh user@your-server.com

# Clone repo
git clone <your-repo-url>
cd bulk-import-tool

# Create .env with credentials
echo "OKTA_DOMAIN=..." >> .env

# Run with Docker
docker-compose up -d
```

Access via: `http://your-server.com:3000`

## Docker Commands Reference

### Start Services
```bash
docker-compose up                    # Foreground
docker-compose up -d                 # Background (detached)
docker-compose up --build            # Rebuild images
```

### Stop Services
```bash
docker-compose stop                  # Graceful stop
docker-compose down                  # Stop and remove containers
docker-compose down -v               # Also remove volumes
```

### View Logs
```bash
docker-compose logs                  # All services
docker-compose logs backend          # Backend only
docker-compose logs frontend         # Frontend only
docker-compose logs -f               # Follow logs (live)
```

### Rebuild After Code Changes
```bash
docker-compose up --build
```

## Troubleshooting

### Port Already in Use
If ports 3000 or 8000 are already in use:

Edit `docker-compose.yml`:
```yaml
backend:
  ports:
    - "8001:8000"  # Use 8001 instead

frontend:
  ports:
    - "3001:3000"  # Use 3001 instead
```

Then access at `http://localhost:3001`

### Service Won't Start
Check logs:
```bash
docker-compose logs backend   # Check backend errors
docker-compose logs frontend  # Check frontend errors
```

### Environment Variables Not Loading
Make sure `.env` file is in the root directory and `docker-compose.yml` has `env_file: - .env`

### Frontend Can't Connect to Backend
- Ensure both containers are on the same network (they are in docker-compose.yml)
- Check backend is running: `docker-compose logs backend`
- Verify CORS is enabled in `backend/main.py`

## Security Notes

⚠️ **Never commit `.env` file to Git**

Add to `.gitignore`:
```
.env
.env.local
.env.*.local
```

Use environment variable secrets in production:
- **Docker Secrets** (Docker Swarm)
- **Environment variables** (Kubernetes)
- **Secrets Manager** (AWS/Azure/GCP)

## File Structure

```
bulk-import-tool/
├── backend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── requirements.txt
│   ├── main.py
│   ├── okta_service.py
│   ├── config.py
│   └── .env (KEEP SECRET - don't commit!)
├── frontend/
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── package.json
│   ├── public/
│   └── src/
├── docker-compose.yml
├── DOCKER_SETUP.md (this file)
└── .gitignore
```

## Next Steps

1. **Share with Team**: Send them this guide and your Git repo
2. **They Run**: `docker-compose up --build`
3. **Done!** 🎉

For questions or issues, check the logs:
```bash
docker-compose logs
```

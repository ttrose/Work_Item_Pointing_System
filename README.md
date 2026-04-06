# Fusion Planning Poker - Full Vue Setup

This version uses a real frontend/backend split:

- **Frontend:** Vue 3 + Vite
- **Backend:** Flask + Flask-SocketIO
- **Realtime:** Socket.IO
- **Docker:** frontend + backend containers
- **Ubuntu support:** included below

## Project structure

```text
planning_poker_full_vue/
  backend/
  frontend/
  scripts/
  docker-compose.yml
  README.md
```

## Ubuntu quick start

These steps assume **Ubuntu 22.04+**.

### 1. Install system packages

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl ca-certificates gnupg
```

### 2. Install Node.js 20

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Verify:

```bash
node -v
npm -v
python3 --version
```

### 3. Start the app on Ubuntu

Open one terminal for the backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

Open a second terminal for the frontend:

```bash
cd frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

### 4. Stop the app on Ubuntu

If you started backend and frontend in separate terminals, stop each one with:

```bash
Ctrl + C
```

Notes:

- Press `Ctrl + C` once in the frontend terminal running `npm run dev`.
- Press `Ctrl + C` once in the backend terminal running `python3 app.py`.
- If one process does not exit, press `Ctrl + C` again.

## Ubuntu one-command helper scripts

From the project root:

### Install dependencies and set up the backend venv
```bash
bash scripts/setup_ubuntu.sh
```

### Run backend
```bash
bash scripts/run_backend.sh
```

### Run frontend
```bash
bash scripts/run_frontend.sh
```

## Docker on Ubuntu

Install Docker and Compose plugin if needed:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

Log out and back in after adding yourself to the docker group.

Then from the project root:

```bash
docker compose up --build
```

If you change any environment variables in `docker-compose.yml`, rebuild and restart:

```bash
docker compose down
docker compose up --build
```

Frontend:
```text
http://localhost:5173
```

Backend:
```text
http://localhost:5000
```

## Notes for Ubuntu

- Use `python3`, not `python`, to avoid path issues.
- The frontend Vite server is already configured with `--host 0.0.0.0`, so it works in Ubuntu, Docker, and most VM/WSL setups.
- The backend Flask app already binds to `0.0.0.0`, so it is reachable from the frontend and from Docker.
- This project still stores room/session state in memory only. Restarting the backend clears active rooms.

## Helpful commands

### Frontend
```bash
cd frontend
npm install
npm run dev
npm run build
npm run preview
```

## Frontend environment setup

Step three for public deployment is making the frontend read the backend API and Socket.IO URLs from Vite environment variables instead of hardcoded localhost values.

The frontend now supports:

- `VITE_API_BASE`
- `VITE_SOCKET_URL`

### Local example

Create a file at `frontend/.env.local` with:

```bash
VITE_API_BASE=http://localhost:5000
VITE_SOCKET_URL=http://localhost:5000
```

Then run:

```bash
cd frontend
npm install
npm run dev
```

### Production example

When you deploy the frontend, set environment variables like:

```text
VITE_API_BASE=https://your-backend-site.com
VITE_SOCKET_URL=https://your-backend-site.com
```

### Docker example

You can also pass the same variables into Docker Compose:

```yaml
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_BASE: "http://localhost:5000"
      VITE_SOCKET_URL: "http://localhost:5000"
```

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

## Backend environment setup

Step two for public deployment is making the backend read its secret key, allowed frontend origin, and port from environment variables instead of hardcoded values.

The backend now supports:

- `SECRET_KEY`
- `CORS_ORIGIN`
- `PORT`
- `FLASK_DEBUG`

### Local example

Run the backend with:

```bash
cd backend
source .venv/bin/activate
export SECRET_KEY="replace-this-with-a-long-random-value"
export CORS_ORIGIN="http://localhost:5173"
export PORT="5000"
export FLASK_DEBUG="true"
python3 app.py
```

### Production example

When you deploy the backend, set environment variables like:

```text
SECRET_KEY=use-a-long-random-secret
CORS_ORIGIN=https://your-frontend-site.com
PORT=5000
FLASK_DEBUG=false
```

If you need to allow more than one frontend origin, separate them with commas:

```text
CORS_ORIGIN=https://your-frontend-site.com,https://www.your-frontend-site.com
```

### Docker example

You can also pass the same variables into Docker Compose:

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      SECRET_KEY: "replace-this-with-a-long-random-value"
      CORS_ORIGIN: "http://localhost:5173"
      PORT: "5000"
      FLASK_DEBUG: "false"
```

### Docker
```bash
docker compose up --build
docker compose down
```

To stop Docker services without removing containers:

```bash
docker compose stop
```

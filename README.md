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

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
```

### Docker
```bash
docker compose up --build
docker compose down
```

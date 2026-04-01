# Fusion Planning Poker - Full Vue Setup

This version uses a real frontend/backend split:

- **Frontend:** Vue 3 + Vite
- **Backend:** Flask + Flask-SocketIO
- **Realtime:** Socket.IO
- **Docker:** frontend + backend containers

## Project structure

```text
planning_poker_full_vue/
  backend/
  frontend/
  docker-compose.yml
  README.md
```

---

## 1. Requirements

Install these first:

### Node / npm
Use **Node 20+**.

Check:
```bash
node -v
npm -v
```

### Python
Use **Python 3.11+**.

Check:
```bash
python --version
```

---

## 2. Frontend setup

Open a terminal in `frontend/`.

Install dependencies:
```bash
cd frontend
npm install
```

### Packages used
These are already listed in `package.json`, so `npm install` is enough.

If you want the manual equivalent, these are the important ones:
```bash
npm install vue socket.io-client
npm install -D vite @vitejs/plugin-vue
```

---

## 3. Backend setup

Open another terminal in `backend/`.

Create a virtual environment:

### Windows PowerShell
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Windows CMD
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### macOS / Linux
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Python packages used
Already included in `requirements.txt`:
```bash
pip install Flask Flask-SocketIO Flask-Cors simple-websocket
```

---

## 4. Run locally for development

You need **two terminals**.

### Terminal 1: backend
```bash
cd backend
python app.py
```

Backend runs on:
```text
http://localhost:5000
```

### Terminal 2: frontend
```bash
cd frontend
npm run dev
```

Frontend runs on:
```text
http://localhost:5173
```

Open the frontend URL in your browser.

---

## 5. Production-style local build

Build the Vue frontend:

```bash
cd frontend
npm run build
```

Preview it:
```bash
npm run preview
```

---

## 6. Docker setup

From the project root:

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

---

## 7. Current behavior

- one shared session
- users can join as:
  - **Player**
  - **Observer**
- players choose:
  - **DEV**
  - **QA**
- observers do **not** need a team
- permission-aware reveal/reset buttons
- settings tabs
- DEV / QA split results
- moderator handoff
- history
- consensus badges
- summary stats

---

## 8. Notes

- Settings are still in-memory only
- No database yet
- First observer becomes moderator
- Changing settings clears the current round

---

## 9. Helpful commands

### Frontend
```bash
npm install
npm run dev
npm run build
npm run preview
```

### Backend
```bash
pip install -r requirements.txt
python app.py
```

### Docker
```bash
docker compose up --build
docker compose down
```

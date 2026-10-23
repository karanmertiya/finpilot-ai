# FinPilot AI — Production Deployment & Operations Guide

## 1. Local Development (Zero Docker Required)

### Backend Setup
```bash
cd backend
python -m venv venv

# Windows PowerShell:
.\venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
python ../scripts/seed_data.py
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

---

## 2. Docker & Docker Compose Deployment (PostgreSQL + pgvector)

```bash
# From project root:
docker compose up --build -d

# Verify services:
docker compose ps
docker compose logs -f backend
```

Services:
- **Frontend**: `http://localhost:3000`
- **Backend API**: `http://localhost:8000/docs`
- **PostgreSQL pgvector**: `localhost:5432`

---

## 3. Free/Low-Cost Cloud Deployment (Portfolio Ready)

### A. Database (Supabase / Neon - Free Tier)
1. Create a free PostgreSQL database on [Supabase](https://supabase.com) or [Neon](https://neon.tech).
2. Enable the `vector` extension:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy the connection string (e.g. `postgresql://user:pass@ep-xyz.neon.tech/finpilot_db?sslmode=require`).

### B. Backend (Render / Fly.io)
1. Deploy as a Web Service on [Render](https://render.com) pointing to the root directory with Dockerfile `backend/Dockerfile`.
2. Configure Environment Variables:
   - `DATABASE_URL`: Your Supabase/Neon connection string
   - `SECRET_KEY`: Random 32+ character string
   - `CORS_ORIGINS`: `["https://your-frontend.vercel.app"]`
   - `LLM_PROVIDER`: `gemini` (or `mock` for zero-cost offline engine)
   - `GEMINI_API_KEY`: Your Google Gemini API key
3. Run the database seed script once via Render Shell:
   ```bash
   python scripts/seed_data.py
   ```

### C. Frontend (Vercel)
1. Import repository on [Vercel](https://vercel.com) and set Root Directory to `frontend`.
2. Set Environment Variable:
   - `NEXT_PUBLIC_API_URL`: `https://your-backend.onrender.com/api/v1`
3. Click **Deploy**. Vercel automatically builds and optimizes the Next.js frontend with global edge CDN.

---

## 4. Database Backup & Disaster Recovery Strategy
1. **Daily Logical Dump**:
   ```bash
   pg_dump -U finpilot -d finpilot_db -F c -b -v -f finpilot_backup_$(date +%F).dump
   ```
2. **Point-In-Time Restore**:
   ```bash
   pg_restore -U finpilot -d finpilot_db -v finpilot_backup_2026-10-23.dump
   ```

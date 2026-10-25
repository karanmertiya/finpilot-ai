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

## 4. Azure Deployment with Student Pack Credits & Custom Domain (`karanmertiya.me`)

The GitHub Student Developer Pack provides **$100 in Azure Credits + 12 months of free services**. You can use these to run FinPilot AI under your personal domain brand (`https://finpilot.karanmertiya.me`).

### Architecture with Custom Subdomains
```
User / Interviewer
       │
       ▼
https://finpilot.karanmertiya.me ─────> [ Frontend: Azure Static Web Apps / Vercel ]
       │
       ▼
https://api.finpilot.karanmertiya.me ─> [ Backend: Azure App Service / Container Apps ]
       │
       ▼
Azure Database for PostgreSQL (Flexible Server B1ms + pgvector)
```

---

### Option A: Modern Azure Cloud Architecture (PaaS & Serverless)

#### 1. Database: Azure Database for PostgreSQL Flexible Server
1. In [Azure Portal](https://portal.azure.com), search for **Azure Database for PostgreSQL flexible servers** -> **Create**.
2. Settings:
   - **Compute + Storage**: Burstable `Standard_B1ms` (1 vCore, 2 GiB RAM, 32 GiB storage) — covered by student credits (~$12/month).
   - **PostgreSQL Version**: 16.
   - **Networking**: Allow public access from Azure services (check *"Allow public access from any Azure service within Azure to this server"*).
3. Enable `pgvector`:
   - Under **Server Parameters**, search for `azure.extensions` -> add `VECTOR`.
   - Save and connect to the database via psql or DBeaver:
     ```sql
     CREATE EXTENSION IF NOT EXISTS vector;
     ```
4. Copy the connection string:
   `postgresql://finadmin:Password123!@finpilot-db.postgres.database.azure.com:5432/finpilot?sslmode=require`

#### 2. Backend: Azure App Service (Linux B1) or Container Apps
1. Create an **App Service** (Linux):
   - **Runtime stack**: Python 3.12 (or Docker container using `backend/Dockerfile`).
   - **Pricing Plan**: `B1 Basic` (covered by $100 student credits).
2. Set **Configuration / Environment Variables**:
   ```ini
   DATABASE_URL=postgresql://finadmin:Password123!@finpilot-db.postgres.database.azure.com:5432/finpilot?sslmode=require
   JWT_SECRET=super_secure_random_key_64_chars_long
   CORS_ORIGINS=["https://finpilot.karanmertiya.me"]
   LLM_PROVIDER=gemini
   GEMINI_API_KEY=your_gemini_api_key
   ```
3. Custom Domain on Backend:
   - Go to **Custom domains** in Azure App Service.
   - Add `api.finpilot.karanmertiya.me`.
   - Azure generates a free managed App Service SSL certificate.

#### 3. Frontend: Azure Static Web Apps (Free Tier) or Vercel
1. Create an **Azure Static Web App**:
   - Link your GitHub repo: `karanmertiya/finpilot-ai`.
   - App location: `/frontend`
   - Build preset: `Next.js`
2. In **Custom domains**:
   - Add `finpilot.karanmertiya.me`.
   - Azure provisions a free auto-renewing SSL certificate.
3. In **Environment variables**:
   - `NEXT_PUBLIC_API_URL=https://api.finpilot.karanmertiya.me/api/v1`

---

### Option B: The All-in-One Azure Ubuntu VM (Single Docker Compose)

The GitHub Student Pack includes **750 hours/month of Azure B1s Linux VM for 12 months for FREE**. This allows running the entire stack (Postgres + pgvector, FastAPI, Next.js, and Caddy/Nginx) on one machine at zero additional cost.

1. **Launch Azure VM**:
   - OS: Ubuntu 24.04 LTS
   - Size: `Standard_B1s` (or `Standard_B2s` using your $100 credits for faster builds)
   - Open ports: `80` (HTTP), `443` (HTTPS), `22` (SSH).
2. **SSH into the VM & Install Docker**:
   ```bash
   ssh azureuser@<YOUR_VM_PUBLIC_IP>
   curl -fsSL https://get.docker.com | sh
   sudo usermod -aG docker $USER
   ```
3. **Clone & Launch FinPilot AI**:
   ```bash
   git clone https://github.com/karanmertiya/finpilot-ai.git
   cd finpilot-ai
   docker compose up --build -d
   ```
4. **Automated SSL with Caddy Reverse Proxy**:
   Create a `Caddyfile` on the VM:
   ```caddy
   finpilot.karanmertiya.me {
       reverse_proxy localhost:3000
   }

   api.finpilot.karanmertiya.me {
       reverse_proxy localhost:8000
   }
   ```
   Run Caddy (`caddy run`), and it automatically provisions and manages free Let's Encrypt SSL certificates for both domains.

---

### DNS Configuration for `karanmertiya.me`

In your DNS provider (Cloudflare, Namecheap, GoDaddy, Hostinger, etc.), add the following DNS records:

| Record Type | Host / Name | Value / Points To | Purpose |
| :--- | :--- | :--- | :--- |
| **CNAME** | `finpilot` | `your-app.azurestaticapps.net` *(or `cname.vercel-dns.com`)* | Frontend Web App |
| **CNAME** | `api.finpilot` | `your-backend.azurewebsites.net` | Backend API & Swagger |
| **A** (If using VM) | `finpilot` | `<YOUR_AZURE_VM_PUBLIC_IP>` | Direct VM IP |
| **A** (If using VM) | `api.finpilot` | `<YOUR_AZURE_VM_PUBLIC_IP>` | Direct VM IP |

---

## 5. Database Backup & Disaster Recovery Strategy
1. **Daily Logical Dump**:
   ```bash
   pg_dump -U finpilot -d finpilot_db -F c -b -v -f finpilot_backup_$(date +%F).dump
   ```
2. **Point-In-Time Restore**:
   ```bash
   pg_restore -U finpilot -d finpilot_db -v finpilot_backup_2026-10-23.dump
   ```


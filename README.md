# LDS Hymnal Catalog & AI Theological Comparison Engine

A multi-container web application designed to catalog, compare, and analyze lyrical and theological shifts across:
1. **Traditional Christian Precursor Hymns** (historical public domain texts by Watts, Wesley, Newton, etc.)
2. **1985 LDS Hymnal**
3. **New *Hymns—for Home and Church*** digital releases

Optimized for containerized deployment on **QNAP NAS** via **Docker Compose** and **Portainer**.

---

## 🛠️ Architecture Stack

- **Database**: PostgreSQL 16 (`db/init.sql`) storing 3-tier hymn lineage and AI change logs.
- **Backend / Data Ingestion & AI Engine**: Python 3.11 FastAPI service using `google-genai` SDK (`gemini-2.5-flash`), BeautifulSoup4, and Pydantic structured output.
- **Frontend Dashboard**: Next.js 14 (App Router) + Tailwind CSS + Lucide React icons, featuring a 3-way side-by-side comparison view and diff visualizer.
- **Orchestration**: Docker Compose with persistent database volume mounts.

---

## 🚀 QNAP NAS & Portainer Deployment Guide

> [!IMPORTANT]
> **Why did Portainer throw `path "/data/compose/.../backend" not found`?**
> Portainer's **Web Editor** tab runs `docker-compose` in an isolated temp folder (`/data/compose/X/`) without your local source files (`backend/`, `frontend/`). 
> To deploy via Portainer, use **Option A (Git Repository)** or **Option B (SSH CLI)** below.

---

### Option A: Portainer Git Repository (Recommended for Portainer UI)
1. Push this repository to GitHub (or your Git server).
2. Open **Portainer** -> **Stacks** -> **Add Stack**.
3. Select **Repository** (instead of Web Editor).
4. Enter your Git Repository URL and specify `docker-compose.yml`.
5. Under **Environment variables**, set:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `POSTGRES_DB`: `hymnal_db`
   - `POSTGRES_USER`: `postgres`
   - `POSTGRES_PASSWORD`: `<your-secure-password>`
6. Click **Deploy the stack**. Portainer will automatically pull the repo, build the `backend` and `frontend` images, and start the stack!

---

### Option B: Direct CLI / Container Station on QNAP NAS (Via SSH)
If your code files are stored on a NAS folder (e.g. `/share/CACHEDEV1_DATA/Container/lds-hymnal-compair`):

1. SSH into your QNAP NAS:
   ```bash
   ssh admin@<your-nas-ip>
   ```
2. Navigate to your project folder:
   ```bash
   cd /share/CACHEDEV1_DATA/Container/lds-hymnal-compair
   ```
3. Create `.env` file from template:
   ```bash
   cp .env.example .env
   # Edit .env and enter your GEMINI_API_KEY
   ```
4. Build and start containers:
   ```bash
   docker-compose up -d --build
   ```
5. Once built, the stack will appear and can be managed in Portainer or QNAP Container Station!


Access services:
- **Frontend Dashboard**: `http://<your-nas-ip>:3000`
- **Backend API Docs**: `http://<your-nas-ip>:8000/docs`

---

## 🤖 AI Comparison Engine Output Schema

The comparison engine invokes Gemini LLM with strict system instructions and forces a Pydantic JSON structure:

```json
{
  "omitted_verses": [
    "Verse 3 (1985 variation was omitted in favor of restoring Watts original Verse 3)"
  ],
  "altered_phrases": [
    {
      "original": "Let men their songs employ",
      "new": "Let all their songs employ"
    }
  ],
  "change_categories": [
    "Inclusive language update",
    "Restoration of original Watts verse"
  ],
  "summary": "The change replaces gendered phrasing ('men') with inclusive phrasing ('all') and restores Isaac Watts' original 3rd verse regarding grace overcoming the curse.",
  "classification": {
    "major_theme": "Taken from Christianity",
    "minor_theme": "Easter/Christmas"
  }
}
```

---

## 📁 Repository Structure

```
.
├── db/
│   └── init.sql                 # PostgreSQL 3-way schema and seed data
├── backend/
│   ├── ai_engine.py             # Gemini LLM comparison engine & strict Pydantic JSON schema
│   ├── scraper.py               # Church music library polling & ingestion
│   ├── app.py                   # FastAPI REST server & line-by-line lineage API
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                 # Next.js App Router pages
│   │   ├── components/          # 3-Way Diff viewer & cards
│   │   └── lib/api.ts           # API Client
│   ├── package.json
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml           # Multi-container orchestration
└── .env.example
```

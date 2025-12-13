# FinEdge RAG Deployment Guide

Deploy the backend on **Render** and frontend on **Vercel**.

---

## 📋 Prerequisites

1. GitHub account with this repo pushed
2. [Render](https://render.com) account (free tier works)
3. [Vercel](https://vercel.com) account (free tier works)
4. Google API Key for Gemini

---

## 🖥️ Part 1: Deploy Backend on Render

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Add deployment config"
git push origin main
```

### Step 2: Create Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `finedge-api` (or your choice) |
| **Region** | Oregon (US West) |
| **Branch** | `main` |
| **Root Directory** | *(leave empty)* |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | Free |

### Step 3: Add Environment Variables

In Render dashboard → Your service → **Environment**:

| Key | Value |
|-----|-------|
| `GOOGLE_API_KEY` | Your Google AI API key |
| `PYTHON_VERSION` | `3.11.0` |

### Step 4: Deploy

1. Click **"Create Web Service"**
2. Wait for build to complete (5-10 minutes first time)
3. Note your URL: `https://finedge-api.onrender.com`

### Step 5: Verify Backend

Visit: `https://your-render-url.onrender.com/health`

You should see:
```json
{"status": "healthy", "version": "2.0.0", ...}
```

---

## 🌐 Part 2: Deploy Frontend on Vercel

### Step 1: Update Production URL

Edit `frontend/.env.production`:
```env
VITE_API_URL=https://your-render-url.onrender.com
```

Commit and push this change.

### Step 2: Deploy to Vercel

**Option A: Vercel CLI**
```bash
cd frontend
npm install -g vercel
vercel
```

**Option B: Vercel Dashboard**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:

| Setting | Value |
|---------|-------|
| **Framework Preset** | Vite |
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

### Step 3: Add Environment Variable

In Vercel → Project Settings → **Environment Variables**:

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://your-render-url.onrender.com` |

### Step 4: Deploy

1. Click **"Deploy"**
2. Wait for build (1-2 minutes)
3. Your frontend is live at: `https://your-project.vercel.app`

---

## ⚠️ Important Notes

### Render Free Tier Limitations
- **Spins down after 15 min inactivity** - First request may take 30-60 seconds
- **Limited to 750 hours/month** across all services
- For production, upgrade to paid tier ($7/month)

### File Storage
- Render free tier uses **ephemeral storage** - uploaded files are lost on restart
- For production, integrate cloud storage (AWS S3, Cloudinary, etc.)

### CORS
The backend is configured to accept requests from any origin (`*`). For production, update `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-url.vercel.app"],
    ...
)
```

---

## 🧪 Testing Deployment

1. Open your Vercel URL
2. Upload a PDF document
3. Wait for analytics to generate
4. Test the RAG chat feature

---

## 🔧 Troubleshooting

### Backend won't start
- Check Render logs for errors
- Verify `GOOGLE_API_KEY` is set correctly
- Check `/health` endpoint

### Frontend can't connect to backend
- Verify `VITE_API_URL` is correct (no trailing slash)
- Check browser console for CORS errors
- Ensure backend is running (check /health)

### PDF viewer not working
- PDFs are served from backend - ensure backend URL is correct
- Check browser console for blocked requests

---

## 📁 Files Created for Deployment

| File | Purpose |
|------|---------|
| `render.yaml` | Render configuration |
| `Procfile` | Render start command |
| `frontend/vercel.json` | Vercel configuration |
| `frontend/.env.production` | Production API URL |
| `.env.example` | Environment template |

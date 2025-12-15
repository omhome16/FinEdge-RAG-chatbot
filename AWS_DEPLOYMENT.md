# FinEdge AWS Deployment Guide

Complete step-by-step guide to deploy FinEdge on AWS (Free Tier eligible).

---

## Prerequisites

Before starting, ensure you have:
- [ ] An AWS Account ([Create one here](https://aws.amazon.com/))
- [ ] Your `GOOGLE_API_KEY` (from Google AI Studio)
- [ ] Code pushed to GitHub
- [ ] AWS CLI installed (optional but recommended)

---

## Part 1: AWS Account Setup (5 minutes)

### Step 1.1: Create AWS Account
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Enter email, password, and account name
4. Add payment method (won't be charged if staying in free tier)
5. Verify phone number
6. Select "Basic Support" (free)

### Step 1.2: Set Up Billing Alerts (IMPORTANT!)
1. Go to **Billing Console** → **Budgets**
2. Click **Create budget**
3. Choose "Zero spend budget"
4. Set alert email → Click **Create**

> ⚠️ This protects you from unexpected charges!

---

## Part 2: Deploy Backend to Elastic Beanstalk (15 minutes)

### Step 2.1: Open Elastic Beanstalk Console
1. Go to [AWS Console](https://console.aws.amazon.com)
2. Search for "Elastic Beanstalk" → Click on it
3. Click **Create application**

### Step 2.2: Configure Application
Fill in the following:

| Field | Value |
|-------|-------|
| Application name | `finedge-api` |
| Platform | Docker |
| Platform branch | Docker running on 64bit Amazon Linux 2023 |
| Application code | Upload your code |

### Step 2.3: Prepare and Upload Code
1. **On your local machine**, create a ZIP file containing:
   ```
   FinEdge-RAG-FineTuning/
   ├── Dockerfile
   ├── requirements.txt
   ├── backend/
   │   └── main.py
   └── src/
       ├── analytics_engine.py
       ├── analytics_storage.py
       ├── document_processor.py
       ├── ingestion.py
       ├── rag_pipeline.py
       └── utils.py
   ```
   
2. **Create ZIP** (excluding frontend, venv, .git):
   ```bash
   # Windows PowerShell
   Compress-Archive -Path Dockerfile,requirements.txt,backend,src -DestinationPath finedge-backend.zip
   ```

3. Upload `finedge-backend.zip` in the console

### Step 2.4: Configure Service Access
1. Select **Create and use new service role**
2. EC2 key pair: Create new or select existing
3. EC2 instance profile: Create new

### Step 2.5: Instance Settings
1. Click **Edit** on "Instances"
2. Set instance type: `t2.micro` (FREE TIER!)
3. Root volume: 8 GB (default, free tier)

### Step 2.6: Set Environment Variables
1. In left panel, click **Updates, monitoring, and logging**
2. Scroll to **Environment properties**
3. Add:
   | Name | Value |
   |------|-------|
   | `GOOGLE_API_KEY` | Your Google AI API key |
   | `PORT` | `8000` |

### Step 2.7: Create Environment
1. Review all settings
2. Click **Submit**
3. Wait 5-10 minutes for deployment
4. Note down your URL: `http://finedge-api-env.xxxxxx.us-east-1.elasticbeanstalk.com`

### Step 2.8: Verify Backend
Open browser and go to:
```
https://YOUR-EB-URL/health
```
You should see: `{"status": "healthy", "version": "2.0.0", ...}`

---

## Part 3: Deploy Frontend to AWS Amplify (10 minutes)

### Step 3.1: Open Amplify Console
1. Search for "AWS Amplify" in AWS Console
2. Click **Create new app**
3. Choose **Host web app**

### Step 3.2: Connect Repository
1. Select **GitHub**
2. Authorize AWS Amplify to access your GitHub
3. Select your repository: `FinEdge-RAG-FineTuning`
4. Select branch: `main` (or your default branch)

### Step 3.3: Configure Build Settings
1. Check "Connecting a monorepo? Pick a folder"
2. Enter: `frontend`
3. Build settings will auto-detect from `amplify.yml`
4. Click **Next**

### Step 3.4: Set Environment Variable
1. Expand **Advanced settings**
2. Add environment variable:
   | Key | Value |
   |-----|-------|
   | `VITE_API_URL` | `https://YOUR-EB-URL.elasticbeanstalk.com` |

   > Replace with your actual Elastic Beanstalk URL from Part 2!

### Step 3.5: Deploy
1. Review settings
2. Click **Save and deploy**
3. Wait 3-5 minutes for build and deployment
4. Note your Amplify URL: `https://main.xxxxx.amplifyapp.com`

---

## Part 4: Final Configuration

### Step 4.1: Update CORS (if needed)
If you get CORS errors, update `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://main.xxxxx.amplifyapp.com",  # Your Amplify URL
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Step 4.2: Test Full Application
1. Open your Amplify URL
2. Upload a test PDF document
3. Wait for processing
4. Try asking questions in chat
5. Verify analytics dashboard works

---

## Troubleshooting

### Backend won't start
- Check Elastic Beanstalk logs: **Logs** → **Request Logs** → **Full logs**
- Common issue: Missing `GOOGLE_API_KEY` environment variable

### Frontend shows API error
- Verify `VITE_API_URL` is set correctly in Amplify
- Check CORS settings in backend

### Deployment fails
- Check build logs in Amplify console
- Ensure `amplify.yml` is in root directory

---

## Cost Summary (Free Tier)

| Service | Limit | Your Usage |
|---------|-------|------------|
| EC2 t2.micro | 750 hrs/month | ~720 hrs |
| Elastic Beanstalk | Free | - |
| Amplify Build | 1000 mins | ~10 mins |
| Amplify Hosting | 15 GB | ~500 MB |

**Total: $0/month** (for 12 months)

---

## Resume Bullet Point

Add this to your resume:

> **FinEdge - Financial Document Intelligence Platform**
> - Deployed full-stack RAG application on AWS (Elastic Beanstalk, Amplify, CloudFront)
> - Built with FastAPI, React, LangChain, and Google Gemini AI
> - Features document parsing, OCR, dynamic analytics, and conversational AI with citations
> - Demo: [Your Amplify URL]

---

## Quick Reference

| Resource | URL |
|----------|-----|
| Backend API | `https://YOUR-EB-URL.elasticbeanstalk.com` |
| Frontend App | `https://main.xxxxx.amplifyapp.com` |
| Health Check | `https://YOUR-EB-URL.elasticbeanstalk.com/health` |
| AWS Console | [console.aws.amazon.com](https://console.aws.amazon.com) |

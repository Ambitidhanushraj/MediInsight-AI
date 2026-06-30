# MediInsight AI - Deployment Guide

## Overview
- **Frontend (React + Vite)** → Vercel
- **Backend (FastAPI + Python)** → Render
- **Free tier available** on both platforms

---

## Part 1: Deploy Frontend to Vercel

### Prerequisites
- Vercel account: https://vercel.com/signup
- GitHub account with your repo pushed

### Steps

1. **Connect GitHub to Vercel**
   - Go to https://vercel.com/dashboard
   - Click "Add New..." → "Project"
   - Import your GitHub repository

2. **Configure Project**
   - **Framework Preset**: Vite
   - **Root Directory**: `backend/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Add Environment Variables**
   - In Vercel Dashboard: Settings → Environment Variables
   - Add: `VITE_API_URL=https://mediinsight-api.onrender.com` (from Render backend)
   - This is set after backend deployment

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete
   - You'll get URL like: `https://mediinsight.vercel.app`

---

## Part 2: Deploy Backend to Render

### Prerequisites
- Render account: https://render.com
- GitHub account with your repo pushed
- API Keys ready:
  - `GEMINI_API_KEY` (from Google AI Studio)
  - `OPENROUTER_API_KEY` (from OpenRouter.ai)

### Steps

1. **Connect GitHub to Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Select your GitHub repository

2. **Configure Service**
   - **Name**: `mediinsight-api`
   - **Region**: Choose nearest to you
   - **Branch**: `main` (or your deploy branch)
   - **Runtime**: Docker
   - **Plan**: `Free` (or Starter if you need more resources)
   - **Auto-deploy**: On

3. **Set Environment Variables**
   - Click "Advanced" → "Add Environment Variable"
   - Add these:
     ```
     GEMINI_API_KEY=your_gemini_key
     OPENROUTER_API_KEY=your_openrouter_key
     CORS_ORIGINS=https://mediinsight.vercel.app
     ENVIRONMENT=production
     UPLOAD_DIR=/tmp/uploads
     ```

4. **Deploy**
   - Click "Create Web Service"
   - Watch build logs in "Logs" tab
   - Once deployed, you'll get URL like: `https://mediinsight-api.onrender.com`

5. **Update Vercel Frontend Environment**
   - Go back to Vercel settings
   - Update `VITE_API_URL` to your Render backend URL
   - Redeploy frontend

---

## Part 3: Update Frontend API URL

### Update React Code to Use Backend

In `backend/frontend/src/App.jsx` or your API client:

```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Use API_URL in your axios calls
axios.get(`${API_URL}/api/endpoint`)
```

---

## Testing Deployment

### Test Backend
```bash
# In browser or terminal
curl https://mediinsight-api.onrender.com/health
```

### Test Frontend
- Visit: https://mediinsight.vercel.app
- Check browser DevTools Console for any API errors
- Verify requests go to backend URL

### Check Logs
- **Vercel**: Dashboard → Deployments → Logs
- **Render**: Dashboard → mediinsight-api → Logs

---

## Troubleshooting

### Backend Issues
- **Build fails**: Check `render.yaml` and `Dockerfile` are in `/backend` root
- **Crashes after deploy**: Check environment variables are set
- **CORS errors**: Verify `CORS_ORIGINS` matches frontend URL exactly

### Frontend Issues
- **API calls fail**: Check `VITE_API_URL` environment variable
- **404/Not Found**: Ensure backend is running (check Render logs)
- **CORS blocked**: Backend may not have correct `CORS_ORIGINS`

---

## Important Notes

**Free Tier Limits:**
- Render free tier: 0.5 GB RAM, spins down after 15 min inactivity
- Vercel free tier: 100 GB bandwidth/month, 12 concurrent builds

**Production Setup:**
- Store API keys in environment variables (NEVER in code)
- Use `ENVIRONMENT=production` on Render
- Enable HTTPS (automatic on both platforms)
- Monitor logs regularly

---

## Files Created

✅ `backend/Dockerfile` - Docker container config
✅ `backend/render.yaml` - Render deployment config  
✅ `backend/frontend/vercel.json` - Vercel deployment config
✅ `backend/.env.example` - Updated with production notes

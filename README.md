# MediInsight AI

AI-powered medical report analysis platform with a FastAPI backend and React (Vite) frontend.

## Project Structure

- `backend/` - FastAPI APIs, OCR/parsing, report analysis, RAG services
- `backend/frontend/` - React + Vite web app
- `backend/render.yaml` - Render deployment config (backend)
- `backend/frontend/vercel.json` - Vercel deployment config (frontend)

## Features

- Upload medical reports (PDF/JPG/PNG)
- OCR and text extraction
- Health parameter extraction and analysis
- Risk classification and recommendations
- Report-aware and medical Q&A chat
- Report history and comparison

## Local Development

### 1) Backend

```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
# source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # create and edit values
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`

### 2) Frontend

```bash
cd backend/frontend
npm install
npm run dev
```

Frontend URL:

- `http://127.0.0.1:5173`

Set frontend API base URL in `.env` (inside `backend/frontend`):

```bash
VITE_API_URL=http://127.0.0.1:8000
```

## Environment Variables

### Backend (`backend/.env`)

Required:

- `GEMINI_API_KEY`
- `OPENROUTER_API_KEY`

Common:

- `CORS_ORIGINS` (comma-separated list)
- `CORS_ORIGIN_REGEX` (default supports `*.vercel.app`)
- `MAX_UPLOAD_SIZE`
- `UPLOAD_DIR`
- `ENVIRONMENT`

### Frontend (Vercel or `backend/frontend/.env`)

- `VITE_API_URL` = backend base URL (Render URL in production)

## Deployment

### Backend on Render

- Service type: Web Service (Docker)
- Root directory: `backend`
- Uses `backend/Dockerfile`
- Set env vars in Render dashboard
- Deploy latest commit

### Frontend on Vercel

- Framework: Vite
- Root directory: `backend/frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Set env var `VITE_API_URL` to Render backend URL

## Troubleshooting

### CORS blocked in browser

- Ensure Render `CORS_ORIGINS` includes your Vercel URL
- Redeploy backend after env changes
- Ensure frontend `VITE_API_URL` points to Render URL

### Upload fails in production

- Check browser Network tab for failed endpoint
- Confirm backend is live: `https://<render-url>/health`
- Check Render app logs for runtime errors

### Build fails on Render

- Open Render Build logs and review first `ERROR`
- Fix dependency versions in `backend/requirements.txt`

## License

Internal / private project.

# PocketAgent Backend

Proxy server that connects PocketAgent (mypoag.app) to Clash of Agents API.
Solves CORS issues so the mobile app can register fighters directly.

## Deploy on Railway (free, no terminal needed)

### Step 1 — Create a GitHub account
Go to github.com and sign up free if you don't have one.

### Step 2 — Create a new repository
1. Click the + button top right → New repository
2. Name it `poag-backend`
3. Set to Public
4. Click Create repository

### Step 3 — Upload these files
1. Click "uploading an existing file" link on the repo page
2. Drag all 4 files into the upload area:
   - server.py
   - requirements.txt
   - Procfile
   - README.md
3. Click "Commit changes"

### Step 4 — Deploy on Railway
1. Go to railway.app
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `poag-backend` repo
5. Railway auto-detects Python and deploys it

### Step 5 — Get your backend URL
Railway gives you a URL like:
`https://poag-backend-production.up.railway.app`

Copy that URL — you'll paste it into the PocketAgent app.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | / | Health check |
| POST | /clash/register | Register a new fighter |
| GET | /clash/me | Get fighter status |
| GET | /clash/leaderboard | Get leaderboard |
| POST | /clash/challenge | Send a challenge |
| POST | /clash/fight/:id/action | Make a fight move |
| POST | /clash/train | Train a stat |
| POST | /clash/chat | Post to lounge |

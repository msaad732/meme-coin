# MemeTrackerBot + Streamlit Dashboard

## Local setup

1. Create `.env` with your Discord bot token:

```
DISCORD_TOKEN=YOUR_TOKEN_HERE
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the Discord bot (writes messages to Postgres if `DATABASE_URL` is set, else to `data/messages.jsonl`):

```
python ingestion_worker.py
```

4. In a separate terminal, run the Streamlit dashboard (reads from Postgres if `DATABASE_URL` is set, else local JSONL):

```
streamlit run streamlit_app.py
```

The dashboard will show the most recent messages captured from the configured channel(s).

## Notes on hosting

- Run the Discord bot on a worker host (Railway/Render/Fly.io/VPS) so it stays online 24/7.
- You can host the Streamlit app on Streamlit Cloud or Railway. It only needs DB read access.
- Use a shared Postgres DB (Railway Postgres or Supabase). Set `DATABASE_URL` in both services.

### Railway (Discord bot backend)

**Step-by-step deployment:**

1) **Create Railway account & project:**
   - Go to [railway.app](https://railway.app) and sign in with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `memecoin` repository

2) **Add Postgres database (optional - if using Supabase, skip this):**
   - In your Railway project, click "+ New" → "Database" → "Add PostgreSQL"
   - Railway will create a Postgres instance and automatically set `DATABASE_URL` as an environment variable

3) **Configure the Discord bot service:**
   - Railway will auto-detect your Python app
   - Go to the service settings → "Variables" tab
   - Add these environment variables:
     - `DISCORD_TOKEN` = your Discord bot token (from Discord Developer Portal)
     - `DATABASE_URL` = your Supabase Postgres connection string (if using Supabase) OR Railway will auto-set this if you added Railway Postgres
   - In "Settings" → "Deploy", set the start command:
     - `python ingestion_worker.py`

4) **Deploy:**
   - Railway will automatically build and deploy
   - Check the "Deployments" tab for logs
   - You should see: `✅ Discord Bot Logged in as MemeTrackerBot#XXXX`

5) **Verify it's working:**
   - The bot will automatically create the `messages` table in your database
   - Send a test message in your Discord channel to verify capture

**Important notes:**
- Railway free tier gives you $5/month credit (usually enough for a lightweight bot)
- The bot stays online 24/7 as long as Railway service is running
- Use the same `DATABASE_URL` in Streamlit Cloud so both services share the same database

### Streamlit Cloud (dashboard)

1) Connect the same repo to Streamlit Cloud.
2) In app settings, set environment variable `DATABASE_URL` to the same Postgres URL.
3) Set the app entrypoint to `streamlit_app.py`.
4) Deploy. Opening the app will show the latest messages from Postgres.

### Render (bot + dashboard + Postgres)

Option A: One-click via `render.yaml`

1) Push this repo to GitHub.
2) In Render, "New +" → "Blueprint" → select the repo (it detects `render.yaml`).
3) Render will create:
   - A Postgres database `memetracker-db`.
   - A web service `memetracker-dashboard` running Streamlit.
   - A background worker `memetracker-bot` running the Discord bot.
4) In the `memetracker-bot` service, add environment variable `DISCORD_TOKEN` (from your bot).
5) Deploy. The bot writes to Postgres; the dashboard reads from it.

Option B: Manual services

1) Create a Postgres database in Render and copy its `DATABASE_URL`.
2) Create a Background Worker service for the bot:
   - Build: `pip install -r requirements.txt`
   - Start: `python ingestion_worker.py`
   - Env: `DISCORD_TOKEN`, `DATABASE_URL`
3) Create a Web Service for Streamlit:
   - Build: `pip install -r requirements.txt`
   - Start: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
   - Env: `DATABASE_URL`

### Vercel (API endpoints)

Vercel provides REST API endpoints that read from Supabase. The Discord bot cannot run on Vercel (needs persistent connections), but you can expose API endpoints.

**Important:** Vercel Python support may be limited. If Python functions don't work, consider using Next.js API routes instead.

**Setup:**
1) Connect your GitHub repo to Vercel.
2) In Vercel project settings → Environment Variables, add:
   - `DATABASE_URL` = your Supabase Postgres connection string (URL-encode special characters like `@`, `#`, etc.)
3) Deploy. Vercel will detect the `api/` folder.

**Available endpoint:**
- `https://your-app.vercel.app/api` - Returns the most recent message from Supabase

**Note:** The bot must still run on Render/Railway for 24/7 operation. Vercel is only for the API endpoint.


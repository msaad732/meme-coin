# Files to Upload to GitHub

## ✅ Files to Upload (via GitHub website)

When you upload manually to GitHub, add these files:

### Main Application Files:
1. **`ingestion_worker.py`** - Discord bot that captures messages
2. **`streamlit_app.py`** - Streamlit dashboard UI
3. **`requirements.txt`** - Python dependencies
4. **`README.md`** - Project documentation

### Deployment Configuration Files:
5. **`Procfile`** - Railway deployment config
6. **`render.yaml`** - Render deployment config
7. **`vercel.json`** - Vercel deployment config

### API Files:
8. **`api/index.py`** - Vercel API endpoint

### Configuration Files:
9. **`.gitignore`** - Git ignore rules (protects secrets)

---

## ❌ Files to NEVER Upload

These are already in `.gitignore` and should NOT be uploaded:

- **`.env`** - Contains your Discord token (SECRET!)
- **`data/`** folder - Local data files (if it exists)

---

## 📋 Quick Upload Checklist

When uploading via GitHub website:

- [ ] ingestion_worker.py
- [ ] streamlit_app.py
- [ ] requirements.txt
- [ ] README.md
- [ ] Procfile
- [ ] render.yaml
- [ ] vercel.json
- [ ] api/index.py (create `api` folder first, then upload `index.py` inside it)
- [ ] .gitignore

---

## 🔒 Important Security Notes

1. **Never upload `.env`** - It contains your Discord bot token
2. **Never commit secrets** - Keep `DISCORD_TOKEN` and `DATABASE_URL` only in:
   - Railway environment variables
   - Streamlit Cloud secrets
   - Vercel environment variables

---

## 📁 Folder Structure on GitHub Should Look Like:

```
memecoin/
├── api/
│   └── index.py
├── ingestion_worker.py
├── streamlit_app.py
├── requirements.txt
├── README.md
├── Procfile
├── render.yaml
├── vercel.json
└── .gitignore
```


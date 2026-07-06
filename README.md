# LivWise — AI Household & Community Living Advisor

**Gen AI Academy APAC Edition — Challenge: AI for Better Living and Smarter Communities**

LivWise compares your household's electricity and water usage against real
community benchmark data for your city, then uses Google's Gemini model to
turn that comparison into fast, personalized, actionable recommendations —
so you don't have to guess whether your bill is normal or where to cut back.

## Demo: [https://livwise-3tbqnum7fgosm96q2tuq9e.streamlit.app/] 



<img width="2550" height="1248" alt="image" src="https://github.com/user-attachments/assets/81a0b500-3ddb-482a-bf63-1af670ab46fb" />


## How it works
1. Enter your city, household size, and last month's electricity/water usage & bills.
2. LivWise instantly benchmarks you against similar households in your city.
3. Gemini generates a plain-English summary, 3 concrete savings actions, and one
   insight you could share with your community.

## Tech stack
- **Streamlit** — frontend
- **Pandas** — benchmark data intelligence
- **Plotly** — visual gauges
- **Google Gemini API** (`gemini-2.0-flash`) — AI-generated recommendations

## Deploy in ~5 minutes (Streamlit Community Cloud — free, public URL)

1. **Get a free Gemini API key**
   Go to https://aistudio.google.com/app/apikey → "Create API key" → copy it.

2. **Push this folder to GitHub**
   ```bash
   cd livwise
   git init
   git add .
   git commit -m "LivWise submission"
   gh repo create livwise --public --source=. --push
   ```
   (No `gh` CLI? Create a new repo on github.com, then:
   `git remote add origin <your-repo-url> && git branch -M main && git push -u origin main`)

3. **Deploy**
   - Go to https://share.streamlit.io → sign in with GitHub.
   - Click **"New app"** → select your `livwise` repo → main branch → `app.py` → **Deploy**.
   - Once deployed, go to **App settings → Secrets** and paste:
     ```
     GEMINI_API_KEY = "your-key-here"
     ```
   - Save. The app reboots automatically. You now have a public URL like
     `https://livwise-<something>.streamlit.app` — that's your **Deployment Link**.

4. Copy that public URL into the Hack2Skill submission form as your
   **Working Prototype Deployed Link**, and your GitHub repo URL as the
   **GitHub Repository Link**.

## Alternative: Google Cloud Run
If you'd rather deploy on Cloud Run (also accepted by the hackathon), add a
`Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0
```
Then:
```bash
gcloud run deploy livwise --source . --set-env-vars GEMINI_API_KEY=your-key --allow-unauthenticated
```

## Files
- `app.py` — main application
- `community_benchmark.csv` — sample community dataset (electricity/water benchmarks by city & household size)
- `requirements.txt` — dependencies
- `.streamlit/secrets.toml.example` — template for your API key (rename to `secrets.toml` for local testing; use the Streamlit Cloud Secrets UI for the live deployment)

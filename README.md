# AI-Powered Smart City Intelligence System

A learning-focused Flask application that analyzes traffic and Air Quality Index (AQI) datasets with NumPy and optionally uses Groq-powered generative AI to explain computed results. It includes an interactive Chart.js dashboard, CSV validation, anomaly indicators, experimental linear estimates, and PDF reports.

> **Data notice:** The included Saddar, Commercial Market, Murree Road, and Satellite Town readings are fictional educational sample values. They are not real-time measurements or official city data.

## Features
- Dashboard cards and Chart.js traffic/AQI charts populated from Flask APIs.
- NumPy mean, median, min, max, standard deviation, 75th percentile, rankings, boolean masks, vectorized growth scenario, and array metadata.
- Configurable threshold and z-score anomaly indicators. A flag is a prompt for review, not proof of an emergency.
- Experimental next-day linear trend estimates using `numpy.polyfit()`; seven days are not enough for reliable operational forecasting.
- CSV upload with schema, numeric, missing-value, non-negative and duplicate checks. Missing values are rejected, never silently changed to zero.
- Groq live AI analysis, recommendations, Q&A and chart/metric explanation, with clearly labelled demo fallbacks when credentials are absent.
- Downloadable PDF report.

## Project structure
```text
AI_Smart_City_Intelligence/
├── app.py
├── analytics.py
├── ai_helper.py
├── data_manager.py
├── report_generator.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── data/sample_city_data.csv
├── templates/{index.html,dashboard.html,report.html}
├── static/{css/style.css,js/app.js,images/}
└── generated_reports/
```

## Windows setup (VS Code / PowerShell)
1. Open this project folder in VS Code.
2. Open the integrated terminal and run:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and optionally add your Groq settings:
   ```env
   GROQ_API_KEY=your_real_key
   GROQ_MODEL=your_current_supported_model_id
   FLASK_SECRET_KEY=replace-with-a-long-random-secret
   ```
   Obtain the current supported model identifier from Groq's official model documentation. Do not paste your key into HTML, JavaScript, GitHub, or chat messages.
4. Start the server:
   ```powershell
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

### Test demo mode
Leave `GROQ_API_KEY` and `GROQ_MODEL` empty. The NumPy dashboard, charts, CSV tools and reports still work. AI responses are explicitly labelled demo content and are not live model output.

### Test live AI mode
Set both environment variables in `.env`, restart Flask, and check for the LIVE AI MODE label. If the key, model or network is unavailable, the UI reports a safe error; no credential is sent to the browser.

## CSV format
The required columns are `location,day,traffic,aqi`. Each location/day pair must be unique. Numeric values must be non-negative. All locations must have the same number of distinct days. Missing and non-numeric values are rejected rather than imputed. Uploads are held in application memory for the running process; restarting the server restores the original sample dataset.

## API endpoints
- `GET /api/dashboard`
- `GET /api/traffic`
- `GET /api/air-quality`
- `GET /api/analytics`
- `GET /api/predictions`
- `POST /api/upload-dataset` (multipart field: `file`)
- `POST /api/reset-dataset`
- `POST /api/settings` (JSON thresholds)
- `POST /api/ai/analyze`
- `POST /api/ai/ask` (JSON `question`)
- `POST /api/ai/recommendations`
- `POST /api/ai/explain` (JSON `subject`)
- `POST /api/ai/generate-report` (PDF response)

## Manual test checklist
- [ ] Run `python app.py` and load the dashboard.
- [ ] Confirm four sample locations and seven days appear.
- [ ] Compare the dashboard averages with the analytics calculations.
- [ ] Upload a valid CSV and confirm the charts update.
- [ ] Try a non-CSV file, missing column, blank value, non-numeric value and duplicate location/day; each should be rejected.
- [ ] Change thresholds and confirm anomaly counts update.
- [ ] Review predictions and their experimental warning.
- [ ] Test AI analysis, recommendations and chat in demo mode.
- [ ] Configure valid Groq credentials and test live AI features.
- [ ] Generate and open the PDF report.

## GitHub
Run these commands from the project directory:
```bash
git init
git add .
git status
git commit -m "Build AI Smart City Intelligence System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AI_Smart_City_Intelligence.git
git push -u origin main
```
Check `git status` before pushing and confirm `.env` is not staged. Never commit API keys.

## Deployment
A conventional Flask host such as Render can run this application with a start command such as `gunicorn app:app` (add `gunicorn` to requirements for that deployment). Configure `GROQ_API_KEY`, `GROQ_MODEL`, and `FLASK_SECRET_KEY` in the host's environment settings. The current in-memory uploaded dataset resets when the process restarts or a new instance handles the request. For durable multi-user uploads, use persistent object storage or a managed database and add authentication/authorization. Do not assume a local filesystem is persistent on serverless platforms. Review the selected host's current Python/runtime and persistent-disk requirements before deploying.

## Security and limitations
- `.env` is ignored by Git; secrets remain on the backend.
- CSV upload size is limited to 5 MB and the file is parsed as data, never executed.
- This starter app has no user authentication and is intended for local educational use; add authentication, CSRF protections, rate limiting and production WSGI configuration before public deployment.
- AI output is explanatory, not an official operational instruction. Verify source data and measurement units independently.
- The current dataset state is process-local memory. Do not use it as permanent storage.

## Screenshots
Add screenshots of the running dashboard here after launching the application.

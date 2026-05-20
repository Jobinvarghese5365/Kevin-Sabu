# Brand Research Desktop Pro

Local web app (FastAPI) + Gemini integration.

## 1) Setup

```bash
cd /Users/kevin.sabu/Desktop/BrandResearchDesktopPro
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Gemini key in `.env`:

```bash
GEMINI_API_KEY=...
```

## 2) Run web app on port 8080

```bash
source .venv/bin/activate
set -a; source .env; set +a
uvicorn backend.app:app --host 127.0.0.1 --port 8080 --reload
```

Open in browser: `http://127.0.0.1:8080`

## Notes

- `Parent Organisation` is normalized to lowercase and suffixed with `-_org`.
- Every output field includes `Copy` and `Google Search`.


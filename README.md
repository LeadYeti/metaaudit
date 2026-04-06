# Meta Ads Audit Tool

Free Meta Ads audit tool by Lead Yeti Pro. Users connect their Facebook account, select an ad account, and get an instant visual audit of their campaigns, audiences, creatives, and spend efficiency.

## Setup

### 1. Create a Meta App

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create a new app (type: "Business")
3. Add "Facebook Login" product
4. Add your redirect URI: `https://yourdomain.com/auth/callback`
5. Request these permissions via App Review: `ads_read`, `read_insights`, `business_management`

### 2. Configure Environment

```bash
cp .env.example .env
# Fill in your Meta App ID, App Secret, GHL webhook URLs, etc.
```

### 3. Install & Run

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Visit `http://localhost:8000`

### 4. Run Tests

```bash
python -m pytest tests/ -v
```

## Architecture

- **Backend:** FastAPI (Python) — handles OAuth, Meta API calls, analysis, GHL webhooks
- **Frontend:** Vanilla HTML/CSS/JS with Chart.js — dark theme dashboard
- **No database** — all data fetched and analyzed in real-time
- **Lead capture** — Facebook OAuth profile data sent to GHL CRM via webhook

## Audit Areas

1. **Account Health** — pixel, conversion tracking, spend cap, account status
2. **Campaign Structure** — count, budget distribution, objective mix
3. **Audience Targeting** — audience types, retargeting, overlap risk
4. **Ad Creative** — ad count per set, frequency fatigue, format mix
5. **Spend Efficiency** — CPM/CPC/CPA vs benchmarks, wasted spend, trends

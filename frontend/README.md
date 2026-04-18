
```markdown
# 🤖 Smart Marketing Assistant
### AI-Powered B2B Outreach Automation Platform



---

## 📌 Problem Statement

B2B sales teams spend hours manually researching potential clients,
writing outreach emails, and tracking responses.
This process is slow, inconsistent, and hard to scale.

**Smart Marketing Assistant solves this by automating the entire pipeline
using AI — from website analysis to personalized email generation —
in under 60 seconds.**

---

## 💡 Solution

A full-stack AI SaaS platform that:
1. Scrapes and analyzes any company website
2. Extracts their core services using AI
3. Discovers 10 relevant B2B leads automatically
4. Summarizes each potential client
5. Generates personalized outreach emails
6. Creates a professional portfolio PDF
7. Uploads portfolio to Google Drive
8. Logs all data to Google Sheets

---

## 🎯 Key Features

| Feature | Description |
|---------|-------------|
| AI Service Extraction | Extracts real services from any website using LLaMA 3.3 70B |
| Lead Discovery | Finds 10 relevant B2B companies automatically |
| Email Generation | Personalized outreach emails for each lead |
| Portfolio PDF | Auto-generated professional portfolio using ReportLab |
| Google Drive Upload | Portfolio uploaded to Drive automatically |
| Google Sheets Logging | All campaign data logged with timestamps |
| Professional Dashboard | React + TypeScript frontend with pipeline visualization |
| REST API Backend | FastAPI backend with CORS support |

---

## 🛠️ Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| Python 3.10 | Core language |
| FastAPI | REST API framework |
| Groq AI (LLaMA 3.3 70B) | Service extraction, lead discovery, email generation |
| Cloudscraper + Selenium | Website scraping with anti-bot bypass |
| BeautifulSoup4 | HTML parsing |
| ReportLab | PDF portfolio generation |
| Google Drive API | Portfolio upload |
| Google Sheets API | Campaign data logging |
| gspread | Google Sheets integration |

### Frontend
| Technology | Purpose |
|-----------|---------|
| React 18 | UI framework |
| TypeScript | Type safety |
| Tailwind CSS | Styling |
| Vite | Build tool |
| Lucide React | Icons |

---

## 🏗️ System Architecture

```
User Input (Company + URL)
        │
        ▼
┌─────────────────────────────────────────┐
│           FastAPI Backend               │
│                                         │
│  1. extractor.py  → scrape website      │
│  2. discovery.py  → find B2B leads      │
│  3. summarizer.py → analyze clients     │
│  4. emailer.py    → generate emails     │
│  5. portfolio.py  → create PDF          │
│  6. drive_uploader.py → upload to Drive │
│  7. sheets_logger.py  → log to Sheets   │
└─────────────────────────────────────────┘
        │
        ▼
React Dashboard (Results + Emails + Leads)
```

---

## 📁 Project Structure

```
smart-marketing-assistant/
│
├── backend/
│   ├── api.py              # FastAPI REST endpoints
│   ├── extractor.py        # Website scraping + service extraction
│   ├── discovery.py        # B2B lead discovery
│   ├── summarizer.py       # Client website summarization
│   ├── emailer.py          # Personalized email generation
│   ├── portfolio.py        # PDF portfolio generation
│   ├── drive_uploader.py   # Google Drive upload
│   ├── sheets_logger.py    # Google Sheets logging
│   ├── scheduler.py        # Automated campaign scheduler
│   ├── cli.py              # Command line interface
│   ├── utils.py            # Utility functions
│   └── requirements.txt    # Python dependencies
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── dashboard/
│   │   │   │   ├── EmailCards.tsx
│   │   │   │   ├── LeadsTable.tsx
│   │   │   │   ├── MetricCards.tsx
│   │   │   │   └── OutputButtons.tsx
│   │   │   ├── pipeline/
│   │   │   │   └── PipelineProgress.tsx
│   │   │   └── Navbar.tsx
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   └── ResultsDashboard.tsx
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── index.html
│
├── .gitignore
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud account (for Drive + Sheets API)
- Groq API key (free at console.groq.com)

---

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-marketing-assistant.git
cd smart-marketing-assistant
```

---

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the backend folder:

```env
GROQ_API_KEY=your_groq_api_key
SERPAPI_KEY=your_serpapi_key (optional)
GOOGLE_SHEETS_CREDENTIALS=credentials.json
```

Add your Google API credentials:
- `credentials.json` — Google Sheets service account key
- `client_secret.json` — Google Drive OAuth key

Run the backend:

```bash
uvicorn api:app --reload --port 8000
```

Backend runs at: `http://localhost:8000`

---

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: `http://localhost:5173`

---

## 🚀 How to Use

1. Open `http://localhost:5173` in your browser
2. Enter your **Company Name**
3. Enter your **Company Website URL**
4. Choose **Fast Scan** or **Deep Scan**
5. Click **Run Campaign**
6. Watch the 6-step pipeline execute in real time
7. View discovered leads, generated emails, and metrics
8. Download portfolio PDF or open Google Sheet

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/run-campaign` | Run full marketing pipeline |
| GET | `/health` | Check API health status |

### Example Request

```json
POST http://localhost:8000/run-campaign

{
  "business_name": "NextGen Solutions",
  "website_url": "https://www.juegostudio.com",
  "page_limit": 2
}
```

### Example Response

```json
{
  "services": "- Game Development\n- AR/VR Solutions\n...",
  "leads": [
    { "title": "Electronic Arts", "link": "https://ea.com" },
    ...
  ],
  "results": [
    {
      "client": { "title": "Electronic Arts" },
      "email": {
        "subject": "Collaboration Opportunity",
        "body": "Dear EA team..."
      }
    }
  ],
  "portfolio": "NextGen_Solutions_Portfolio.pdf"
}
```

---

## 🔐 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GROQ_API_KEY | Yes | Groq AI API key |
| SERPAPI_KEY | No | SerpAPI key for lead search |
| GOOGLE_SHEETS_CREDENTIALS | Yes | Path to credentials.json |

---

## 👨‍💻 Team

| Name | Role |
|------|------|
| Amanullah Sankh | Full Stack Developer & AI Engineer |

**Institution:** P.A. College of Engineering, Vijayapura
**University:** Visvesvaraya Technological University (VTU)
**Batch:** 2022–2026

---

## 📄 License

This project is built for educational and hackathon purposes.

---

## 🙏 Acknowledgements

- [Groq](https://console.groq.com) — Free LLaMA AI API
- [FastAPI](https://fastapi.tiangolo.com) — Python web framework
- [Bolt.new](https://bolt.new) — React UI generation
- [Google Cloud](https://cloud.google.com) — Drive & Sheets APIs

---

> Smart Marketing Assistant — Turning websites into revenue opportunities with AI
```

---






```markdown

\# Smart Marketing Assistant

\### AI-Powered B2B Outreach Automation Platform





\---



\## Problem Statement



B2B sales teams spend hours manually researching potential clients, writing outreach emails, and tracking responses. This process is slow, inconsistent, and hard to scale.



\*\*Smart Marketing Assistant solves this by automating the entire pipeline using AI — from website analysis to personalized email generation — in under 60 seconds.\*\*



\---



\## Solution



A full-stack AI SaaS platform that:

1\. Scrapes and analyzes any company website

2\. Extracts core services using AI

3\. Discovers 10 relevant B2B leads automatically

4\. Summarizes each potential client

5\. Generates personalized outreach emails

6\. Creates a professional portfolio PDF

7\. Uploads portfolio to Google Drive

8\. Logs all data to Google Sheets



\---



\## Key Features



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



\---



\## Tech Stack



\### Backend

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



\### Frontend

| Technology | Purpose |

|-----------|---------|

| React 18 | UI framework |

| TypeScript | Type safety |

| Tailwind CSS | Styling |

| Vite | Build tool |

| Lucide React | Icons |



\---



\## System Architecture



```

User Input (Company + URL)

&#x20;       │

&#x20;       ▼

┌─────────────────────────────────────────┐

│           FastAPI Backend               │

│                                         │

│  1. extractor.py  → scrape website      │

│  2. discovery.py  → find B2B leads      │

│  3. summarizer.py → analyze clients     │

│  4. emailer.py    → generate emails     │

│  5. portfolio.py  → create PDF          │

│  6. drive\_uploader.py → upload to Drive │

│  7. sheets\_logger.py  → log to Sheets   │

└─────────────────────────────────────────┘

&#x20;       │

&#x20;       ▼

React Dashboard (Results + Emails + Leads)

```



\---



\## Project Structure



```

smart-marketing-assistant/

│

├── backend/

│   ├── api.py                 # FastAPI REST endpoints

│   ├── extractor.py           # Website scraping + service extraction

│   ├── discovery.py           # B2B lead discovery

│   ├── summarizer.py          # Client website summarization

│   ├── emailer.py             # Personalized email generation

│   ├── portfolio.py           # PDF portfolio generation

│   ├── drive\_uploader.py      # Google Drive upload

│   ├── sheets\_logger.py       # Google Sheets logging

│   ├── scheduler.py           # Automated campaign scheduler

│   ├── cli.py                 # Command line interface

│   ├── utils.py               # Utility functions

│   └── requirements.txt       # Python dependencies

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

│   │   └── App.tsx

│   ├── package.json

│   └── index.html

│

├── .gitignore

└── README.md

```



\---



\## Setup and Installation



\### Prerequisites

\- Python 3.10+

\- Node.js 18+

\- Google Cloud account (for Drive + Sheets API)

\- Groq API key — free at https://console.groq.com



\---



\### 1. Clone the Repository



```bash

git clone https://github.com/YOUR\_USERNAME/smart-marketing-assistant.git

cd smart-marketing-assistant

```



\### 2. Backend Setup



```bash

cd backend

pip install -r requirements.txt

```



Create a `.env` file inside the backend folder:



```env

GROQ\_API\_KEY=your\_groq\_api\_key

SERPAPI\_KEY=your\_serpapi\_key\_optional

GOOGLE\_SHEETS\_CREDENTIALS=credentials.json

```



Run the backend:



```bash

uvicorn api:app --reload --port 8000

```



Backend runs at: http://localhost:8000



\---



\### 3. Frontend Setup



```bash

cd frontend

npm install

npm run dev

```



Frontend runs at: http://localhost:5173



\---



\## How to Use



1\. Open http://localhost:5173 in your browser

2\. Enter your Company Name

3\. Enter your Company Website URL

4\. Choose Fast Scan or Deep Scan

5\. Click Run Campaign

6\. Watch the 6-step pipeline execute in real time

7\. View discovered leads, generated emails, and metrics

8\. Download portfolio PDF or open Google Sheet



\---



\## API Endpoints



| Method | Endpoint | Description |

|--------|----------|-------------|

| POST | `/run-campaign` | Run full marketing pipeline |

| GET | `/health` | Check API health status |



\### Example Request



```json

POST http://localhost:8000/run-campaign



{

&#x20; "business\_name": "NextGen Solutions",

&#x20; "website\_url": "https://www.juegostudio.com",

&#x20; "page\_limit": 2

}

```



\### Example Response



```json

{

&#x20; "services": "- Game Development\\n- AR/VR Solutions",

&#x20; "leads": \[

&#x20;   { "title": "Electronic Arts", "link": "https://ea.com" }

&#x20; ],

&#x20; "results": \[

&#x20;   {

&#x20;     "client": { "title": "Electronic Arts" },

&#x20;     "email": {

&#x20;       "subject": "Collaboration Opportunity",

&#x20;       "body": "Dear EA team..."

&#x20;     }

&#x20;   }

&#x20; ],

&#x20; "portfolio": "NextGen\_Solutions\_Portfolio.pdf"

}

```



\---



\## Environment Variables



| Variable | Required | Description |

|----------|----------|-------------|

| GROQ\_API\_KEY | Yes | Groq AI API key |

| SERPAPI\_KEY | No | SerpAPI key for lead search |

| GOOGLE\_SHEETS\_CREDENTIALS | Yes | Path to credentials.json |



\---



\## Team



| Name | Role |

|------|------|

| Amanullah Sankh | Full Stack Developer and AI Engineer |



\*\*Institution:\*\* P.A. College of Engineering, Vijayapura

\*\*University:\*\* Visvesvaraya Technological University (VTU)

\*\*Batch:\*\* 2022 - 2026



\---



\## Acknowledgements



\- Groq — Free LLaMA AI API — https://console.groq.com

\- FastAPI — Python web framework — https://fastapi.tiangolo.com

\- Bolt.new — React UI generation — https://bolt.new

\- Google Cloud — Drive and Sheets APIs — https://cloud.google.com



\---



> Smart Marketing Assistant — Turning websites into revenue opportunities with AI

```



\---




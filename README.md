# HouserFinder - Singapore Rental Search Tool

A smart rental search tool for Singapore that aggregates listings, provides visual comparisons, and uses AI to filter properties based on natural language descriptions.

## Features

- **Multi-source aggregation**: Scrapes listings from PropertyGuru, 99.co, and EdgeProp
- **Visual comparison**: Interactive maps, price charts, and side-by-side listing cards
- **AI-powered filtering**: Describe your ideal home in plain language and let Claude find it for you

## Tech Stack

- **Backend**: Python + FastAPI, Playwright (scraping), Claude API (AI filtering)
- **Frontend**: Next.js + React, Tailwind CSS, Recharts, Leaflet (maps)

## Project Structure

```
houserfinder/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI entry point
│   │   ├── scrapers/        # Site-specific scrapers
│   │   ├── ai/              # Claude AI filtering logic
│   │   ├── models/          # Pydantic data models
│   │   └── api/             # API route handlers
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js app directory
│   │   ├── components/      # UI components
│   │   └── lib/             # API client, utilities
│   ├── package.json
│   └── .env.example
└── docker-compose.yml
```

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

## Environment Variables

### Backend (`backend/.env`)
```
ANTHROPIC_API_KEY=your_key_here
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

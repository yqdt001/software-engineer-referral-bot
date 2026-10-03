# Software Engineer Referral Bot

A system for processing software engineer referral applications with AI-powered technical skill evaluation.

## Project Structure

```
software-engineer-referral-bot/
├── local_bridge.py          # Flask webhook server
├── frontend/                # Next.js candidate submission form
│   ├── app/
│   │   ├── components/      # React components
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Candidate submission form
│   │   └── globals.css      # Global styles
│   ├── lib/                 # Utility functions
│   ├── public/              # Static assets
│   ├── package.json         # Node dependencies
│   ├── tsconfig.json        # TypeScript config
│   ├── tailwind.config.ts   # Tailwind CSS config
│   ├── postcss.config.js    # PostCSS config
│   └── next.config.js       # Next.js config
└── README.md
```

## Setup

### Flask Bridge Server

1. Install Python dependencies:
```bash
pip install flask requests
```

2. Run the Flask server:
```bash
python local_bridge.py
```

The server will listen on `http://localhost:5000`

### Next.js Frontend

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Architecture

1. **Candidate Submission Form (Next.js)**: Collects candidate information and resume text
2. **Flask Bridge Server**: Receives webhook payloads, cleans resume text, and forwards to Jan AI
3. **Jan AI Endpoint**: Local AI model (`http://localhost:1337/v1/chat/completions`) performs technical skill scoring

## API Endpoints

### Flask Bridge Server

- `POST /webhook` - Receives Make.com webhook payloads with resume data
- `GET /health` - Health check endpoint

## Integration with Make.com

Configure Make.com to send POST requests to:
```
http://localhost:5000/webhook
```

Expected payload format:
```json
{
  "resume_text": "Candidate resume text here...",
  "name": "John Doe",
  "email": "john@example.com"
}
```

# CareerPilot AI 🚀

CareerPilot AI is an AI-powered career assistant that helps users find suitable jobs, analyze job opportunities, identify skill gaps, tailor resumes, research companies, get application recommendations, and track applications.

## Features

* 🔍 **AI Job Search** — Search for jobs using natural-language queries.
* 🎯 **Job Matching** — Matches job opportunities with the user's skills and profile.
* 📄 **Job Analysis** — Provides detailed information about selected jobs.
* 🏢 **Company Research** — Analyzes the company associated with a selected job.
* 🧩 **Skill Gap Analysis** — Identifies skills required by the job that the user may need to improve.
* 📝 **Resume Tailoring** — Generates a resume tailored to the selected job.
* 🤖 **Decision Agent** — Helps determine whether a job is a suitable opportunity for the user.
* 📋 **Application Tracking** — Keeps track of jobs the user has chosen to apply to.
* 📜 **Application History** — Allows users to view previously tracked applications.

## How It Works

```text
User
 ↓
Search for Jobs
 ↓
AI Job Matching
 ↓
Select a Job
 ↓
Job Analysis
 ├── Company Research
 ├── Skill Gap Analysis
 ├── Resume Tailoring
 └── Decision Agent
 ↓
Application Tracking
 ↓
Application History
```

## Technology Stack

### Frontend

* React
* Vite
* JavaScript
* Tailwind CSS
* Axios
* React Router

### Backend

* Python
* FastAPI
* LangGraph
* LangChain
* Pydantic
* Uvicorn

### AI

* Groq
* Large Language Models (LLMs)
* AI Agents
* Structured LLM outputs

### APIs & Services

* Adzuna Job API
* Groq API
* PostgreSQL

## Project Structure

```text
CareerPilot-AI/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   ├── graph/
│   │   ├── models/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── context/
│   │   └── api/
│   └── package.json
│
├── .env.example
├── .gitignore
└── README.md
```

## Installation

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/CareerPilot-AI.git
cd CareerPilot-AI
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file and add your required API keys and database configuration.

Start the backend:

```bash
uvicorn app.main:app --reload
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

The project uses environment variables for API keys and configuration.

Example:

```env
GROQ_API_KEY=your_groq_api_key
ADZUNA_APP_ID=your_adzuna_app_id
ADZUNA_APP_KEY=your_adzuna_app_key
DATABASE_URL=your_database_url
VITE_API_BASE_URL=http://127.0.0.1:8000
```

**Do not commit your `.env` file or API keys to GitHub.**

## Example

A user can search:

```text
Find backend engineering internships
```

CareerPilot AI searches for relevant opportunities and ranks them based on the user's profile.

The user can then select a job and view:

* Job details
* Match score
* Company information
* Skill gaps
* Tailored resume
* Application recommendation
* Shortlisted opportunities

The user can also track the application and view it later in application history.

## Application Tracking

The current application workflow records the user's application inside CareerPilot AI and displays it in application history.

It does **not** automatically submit the application to the employer's website.

Future versions can add browser automation and ATS integrations for real application submission.

## Current Status

CareerPilot AI is an active project under development.

The main job-search, matching, analysis, company research, skill-gap, and application-tracking workflows are implemented. Resume tailoring, decision-agent improvements, UI refinement, testing, and production hardening are being finalized.

## Future Improvements

* Real application submission through supported ATS platforms
* Browser automation with user approval
* Better resume parsing
* Improved job recommendations
* User authentication
* Application analytics
* Notifications for new jobs
* Interview preparation
* Deployment and CI/CD
* More automated testing

## Author

**Srujana Mitta**

Computer Science & Engineering
Rajiv Gandhi University of Knowledge Technologies

## License

This project is developed for educational and portfolio purposes.

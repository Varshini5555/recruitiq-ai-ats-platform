# RecruitIQ AI

AI-Powered Resume Intelligence & ATS Evaluation Platform

RecruitIQ AI is a production-oriented AI recruitment intelligence platform that evaluates resumes using ATS-style parsing, contextual skill verification, recruiter scoring logic, project maturity analysis, and hiring-readiness insights.

Designed specifically for AI Engineer, ML Engineer, Data Scientist, and GenAI-focused hiring workflows, the platform simulates how modern recruiters and ATS systems evaluate technical candidates beyond simple keyword matching.

---

## 🚀 Key Highlights

* Intelligent ATS-style resume evaluation engine
* AI/ML recruiter simulation scoring framework
* Context-aware skill verification & credibility analysis
* Semantic Job Description matching
* AI project maturity & production-readiness evaluation
* Quantified achievement and business impact detection
* Recruiter-style hiring risk assessment
* Dynamic resume improvement roadmap generation
* Explainable scoring breakdowns for transparency

---

# 📌 Why RecruitIQ AI?

Most ATS analyzers only perform keyword matching.

RecruitIQ AI goes beyond traditional ATS systems by evaluating:

* whether skills are backed by actual implementation evidence
* whether projects demonstrate production-level engineering maturity
* whether achievements show measurable business impact
* whether resumes appear keyword-stuffed or recruiter-credible
* whether candidate profiles align with modern AI hiring expectations

The system is designed to mimic recruiter reasoning rather than simplistic resume parsing.

---

# 🧠 Core Features

## ✅ ATS Parsing & Structural Validation

* ATS-compatible PDF parsing
* Resume formatting compliance analysis
* Structural readability validation
* Parsing optimization checks

## ✅ AI-Powered Skill Intelligence

* Skill extraction & categorization
* Requirement priority classification
* Skill evidence verification
* Credibility index scoring
* Missing skill detection

## ✅ Job Description Matching

* Semantic overlap analysis
* Domain-specific skill alignment
* Hiring-density evaluation
* Experience-band matching

## ✅ AI/ML Project Evaluation

* Project complexity scoring
* Production-readiness analysis
* Tutorial-pattern detection
* Deployment maturity evaluation
* Engineering depth assessment

## ✅ Recruiter Intelligence Layer

* Recruiter-style hiring verdicts
* Risk flag generation
* Candidate strength identification
* Improvement recommendations
* Resume optimization roadmap

## ✅ Impact & Achievement Analysis

* Quantified metrics extraction
* Ownership signal detection
* Scale indicator evaluation
* Business impact scoring

---

# 🏗️ System Architecture

```text
Resume PDF
   ↓
PDF Parsing Layer
   ↓
Resume Text Extraction
   ↓
NLP Skill Extraction Engine
   ↓
JD Semantic Matching Engine
   ↓
ATS Scoring Framework
   ↓
Credibility & Context Validation
   ↓
Recruiter Intelligence Layer
   ↓
Frontend Visualization Dashboard
```

---

# ⚙️ Tech Stack

## Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS
* Lucide React Icons

## Backend

* Python
* FastAPI / Flask
* REST APIs
* Modular JSON Scoring Pipelines

## AI / NLP

* Resume Parsing
* Semantic Skill Matching
* NLP-based Skill Extraction
* Weighted ATS Scoring Logic
* Recruiter Heuristic Modeling

## Visualization & UI

* Dynamic score dashboards
* Recruiter evaluation panels
* ATS insights visualization

## Deployment

* Vercel (Frontend)
* Render / Railway (Backend)
* Docker (Planned)

---

# 📊 Scoring Framework

RecruitIQ AI evaluates resumes using a weighted multi-dimensional scoring engine:

| Evaluation Area       | Weight |
| --------------------- | ------ |
| ATS Formatting        | 10%    |
| Grammar & Syntax      | 5%     |
| Skill Match Quality   | 25%    |
| Project Maturity      | 20%    |
| Business Impact       | 15%    |
| JD Semantic Match     | 15%    |
| Engineering Readiness | 10%    |

---

# 🔍 Engineering Highlights

* Designed a weighted ATS scoring engine simulating recruiter evaluation workflows
* Built contextual credibility validation to reduce keyword-stuffing bias
* Engineered explainable scoring pipelines for transparency
* Implemented recruiter-style hiring risk assessment logic
* Developed modular project maturity scoring heuristics
* Created production-oriented AI dashboard visualization workflows
* Built extensible JSON-driven evaluation pipelines

---

# 🧩 Technical Challenges Solved

* Handling inconsistent PDF parsing structures
* Balancing ATS scoring weights dynamically
* Detecting low-context keyword stuffing
* Designing explainable recruiter feedback systems
* Structuring scalable modular scoring architecture
* Simulating recruiter reasoning using deterministic evaluation pipelines

---

# 📸 Screenshots

## ATS Resume Upload

<img width="1917" height="987" alt="Screenshot 1(resume upload)" src="https://github.com/user-attachments/assets/e93e43f0-285c-4e10-a193-ef3fc52880b2" />

## Overall ATS Score and Feedback

<img width="1910" height="812" alt="Screenshot 2 (overall ATS Score)" src="https://github.com/user-attachments/assets/c093a163-a4f7-4fc1-b892-107c7da3521e" />

## Score breakdown

<img width="1896" height="718" alt="Screenshot 3 (Score breakdown)" src="https://github.com/user-attachments/assets/712112ad-15a7-48ee-b5a5-d5358f9443db" />

## Skill Match Analysis

<img width="1907" height="907" alt="Screenshot 4 (Skill Match Analysis)" src="https://github.com/user-attachments/assets/38f8d062-5f70-41b4-bb96-fc1b50e9a6bc" />

## Technical Portfolio Evaluation

<img width="1858" height="776" alt="Screenshot 5 (Technical Portfolio Evaluation)" src="https://github.com/user-attachments/assets/4f29dbc9-621e-4aee-9062-7812f14feeb9" />

## Performance Metrices

<img width="1920" height="990" alt="Screenshot 6 (Performance Metrices)" src="https://github.com/user-attachments/assets/4e40e7d5-3d38-45fa-b70e-3d0b0707212d" />

## AI Engineering match, Layout, Grammar and JD match score

<img width="1887" height="947" alt="Screenshot 7 (Ai engineering match, ats layout, grammer and jd match)" src="https://github.com/user-attachments/assets/9dce0cc9-ddf0-4f93-9960-b149349d8858" />

## Recruiter Evaluation

<img width="1891" height="983" alt="Screenshot 8 (Recruiter Evaluation)" src="https://github.com/user-attachments/assets/2e23be3e-7994-4b25-908b-8af71d5cf778" />

---

# 📈 Example Evaluation Insights

The platform can identify:

* Missing production engineering skills
* Weak deployment exposure
* Low business impact statements
* Tutorial-like projects
* Lack of quantified achievements
* Missing AI infrastructure skills
* ATS formatting problems
* Contextually weak skill claims

---

# 🔮 Future Roadmap

* Docker containerization
* CI/CD pipelines
* Cloud-native deployment
* RAG-powered recruiter intelligence
* LLM-based resume rewriting assistant
* Multi-resume batch processing
* Recruiter conversational AI assistant
* Real-time job recommendation engine
* Vector search integration
* AI governance evaluation layer

---

# 📂 Project Structure

```text
recruitiq-ai/
│
├── frontend/
├── backend/
├── docs/
│   ├── screenshots/
├── .gitignore
├── README.md
└── LICENSE
```

---

# 🛠️ Local Setup

## Frontend

```bash
cd frontend
npm install
npm run dev
```

## Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

---

# 🎯 Intended Users

* AI Engineers
* ML Engineers
* Data Scientists
* GenAI Engineers
* Recruiters
* Technical Hiring Teams
* Students preparing AI/ML resumes

---

# 📜 License

MIT License

---

# 👩‍💻 Author

Varshini S

AI/ML Engineer | NLP & GenAI Enthusiast | AI Systems Builder

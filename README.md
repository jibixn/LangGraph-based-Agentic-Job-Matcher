# Agentic Profile Matching System

A resume screening and profile matching system built with **LangGraph, LangChain, ChromaDB, Hugging Face embeddings, and Groq LLMs**.

The system reads a Job Description (JD), extracts its requirements, retrieves relevant resume information using semantic search, evaluates candidates against the requirements, and generates a ranked candidate report.

## Overview

The application is designed to automate the initial stages of a recruitment workflow.

Given a Job Description and a collection of resumes, the system:

1. Reads and extracts the Job Description.
2. Extracts required skills and qualifications using an LLM.
3. Searches a ChromaDB vector store for relevant resume information.
4. Evaluates retrieved candidates against the Job Description.
5. Produces structured candidate evaluations.
6. Generates a final ranked report for the top candidates.

The current implementation uses a deterministic LangGraph workflow. Agentic tool selection and human-feedback loops can be added as future extensions.

## Architecture

```text
                    Job Description
                           |
                           v
                    +-------------+
                    |   Parse JD  |
                    +-------------+
                           |
                           v
                  +-------------------+
                  | Extract Requirements|
                  |       (LLM)        |
                  +-------------------+
                           |
                           v
                  +-------------------+
                  |   Search Resumes  |
                  |     (RAG Tool)    |
                  +-------------------+
                           |
                           v
                  +-------------------+
                  |  Rank Candidates  |
                  |       (LLM)       |
                  +-------------------+
                           |
                           v
                  +-------------------+
                  |  Generate Report  |
                  |       (LLM)       |
                  +-------------------+
                           |
                           v
                         END
```




## Project Structure


```text
Agentic_Profile_Matching/
│
├── main.py
├── matching_agent.py
├── init_rag.py
├── requirements.txt
├── .env
├── .gitignore
│
├── tools/
│   ├── __init__.py
│   ├── fs_tools.py
│   └── rag.py
│
├── resources/
│   ├── resumes/
│   │   ├── resume1.pdf
│   │   ├── resume2.pdf
│   │   └── ...
│   │
│   └── SDE Job Description.pdf
│
└── chroma_langchain_db/
```

The Chroma database is **not** committed to GitHub.

## Installation

Clone the repository:

```bash
git clone <your-repository-url>
cd Agentic_Profile_Matching
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` to GitHub.

Add it to `.gitignore`:

```gitignore
.env
venv/
__pycache__/
chroma_langchain_db/
*.pyc
```

## Running the Application

Place the resumes inside:

```text
resources/resumes/
```

and the Job Description inside:

```text
resources/
```

Then run:

```bash
python main.py
```

The system will process the Job Description, retrieve relevant resume information, evaluate candidates, and generate a candidate ranking report.

## Resume Ingestion

Resume ingestion only needs to be performed when new resumes are added or existing resumes are modified.



## Planned Agentic Architecture

The final version can move from a deterministic workflow to an agentic workflow:

```text
                    +----------------+
                    |      Agent     |
                    |      LLM       |
                    +-------+--------+
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
        RAG Search   Candidate Compare   Interview
           Tool           Tool           Questions
              |             |             |
              +-------------+-------------+
                            |
                            v
                     Candidate State
                            |
                            v
                         Ranking
                            |
                            v
                         Report
                            |
                            v
                    Human Feedback
                            |
                 +----------+----------+
                 |                     |
               Accept                Modify
                 |                     |
                 v                     v
                END                 Re-rank
```

This architecture supports conversational requests such as:

```text
Find candidates with React and 3+ years experience.

Compare the top 3 candidates.

Why did Candidate A rank higher than Candidate B?

Make Laravel a mandatory requirement.

Generate screening questions for Candidate A.
```

## Technologies

* Python
* LangChain
* LangGraph
* ChromaDB
* Hugging Face
* Sentence Transformers
* Semantic Chunking
* Groq
* Pydantic
* PyPDF

## Future Improvements

* Agentic tool selection
* Human-in-the-loop approval
* Conversational memory
* Candidate comparison
* Interview question generation
* Multi-round screening
* Requirement weighting
* Must-have vs nice-to-have classification
* Candidate-specific retrieval
* Explainable ranking
* Resume deduplication
* OCR support for scanned resumes
* Evaluation metrics for retrieval and ranking

## License

This project is intended for educational and portfolio purposes.

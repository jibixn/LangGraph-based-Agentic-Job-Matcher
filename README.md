# Agentic Profile Matching System

A resume screening and profile matching system built with **LangGraph, LangChain, ChromaDB, Hugging Face embeddings, and an LLM**.

The system reads a Job Description (JD), extracts its requirements, retrieves relevant resume information using semantic search, evaluates candidates against the requirements, and uses an **agentic feedback loop with tool calling and human approval** to refine candidate selection and ranking.

## Overview

The application is designed to automate the initial stages of a recruitment workflow while allowing a human reviewer to iteratively guide the agent.

Given a Job Description and a collection of resumes, the system:

1. Reads and extracts the Job Description.
2. Extracts required skills and qualifications using an LLM.
3. Searches a ChromaDB vector store for relevant resume information.
4. Evaluates retrieved candidates against the Job Description.
5. Produces structured candidate evaluations.
6. Presents the candidate evaluation to a human reviewer.
7. Uses human feedback to determine whether to retrieve more candidates or re-rank existing candidates.
8. Uses RAG retrieval tools through an LLM-powered agent when additional candidates are required.
9. Re-ranks candidates based on reviewer feedback when necessary.
10. Generates a final ranked report after human approval.

## Architecture

```text
## Architecture

```text
                         Start
                           |
                           v
                      +----------+
                      | Parse JD |
                      +----------+
                           |
                           v
                +----------------------+
                | extract requirements |
                +----------------------+
                           |
                           v
                    +---------------+
                    | Search Resume |
                    +---------------+
                           |
                           v
                    +----------------+
                    | extract text   |
                    |  from chunks   |<--------------------+
                    +----------------+                     |
                           |                               |
                           v                               |
                    +----------------+                     |
                    |  select resume |                     |
                    +----------------+                     |
                           |                               |
                           v                               |
                      +----------+                         |
    +---------------->| approval |                         |
    |                 +----+-----+                         |
    |                      |                               |
    |            +---------+---------+                     |
    |            |                   |                     |
    |         APPROVED            REJECTED                 |
    |            |                   |                     |
    |            v                   v                     |
    |       +---------+          +---------+               |
    |       |  output |          |  agent  |               |
    |       +---------+          +----+----+               |
    |           |                     |                    |
    |           v            +--------+--------+           |
    |          END           |                 |           |
    |                      RERANK           RETRIEVE       |
    |                        |                 |           |
    |                        v                 v           |
    |                  +-----------+    +-------------+    |
    +------------------|rank_resumes|   |retrieve_more|    |
                       +-----+-----+    +------+------+    |
                                               |           |
                                               v           |
                                          +---------+      |
                                          |  tool   |------|
                                          +----+----+
                   

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
API_KEY=your_api_key
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

The system will process the Job Description, retrieve relevant resume information, evaluate candidates, and enter a human-in-the-loop review cycle.

The reviewer can provide feedback such as:

```text
Are there any other candidates?
```

or:

```text
Prioritize Java.
```

The agent then determines whether to retrieve additional candidates or re-rank the existing candidates.

The workflow ends when the reviewer approves the results with:

```text
yes
```

## Resume Ingestion

Resume ingestion only needs to be performed when new resumes are added or existing resumes are modified.

The resumes are converted into LangChain `Document` objects, semantically chunked, embedded using Hugging Face embeddings, and stored in ChromaDB for retrieval.

## Planned Agentic Architecture

The current implementation already includes an agentic feedback loop with RAG tool selection and human approval:

```text
                    +----------------+
                    |      Agent     |
                    |      LLM       |
                    +-------+--------+
                            |
              +-------------+-------------+
              |                           |
              v                           v
        Retrieve More                 Re-rank
              |                           |
              v                           v
       +-------------+             +-------------+
       |   RAG Tool  |             | Rank Resume |
       |   Selection |             |    (LLM)    |
       +------+------+             +------+------+
              |                           |
              v                           |
        Tool Node                         |
              |                           |
              v                           |
       Vector Store                       |
              |                           |
              +-------------+-------------+
                            |
                            v
                    Candidate State
                            |
                            v
                    Human Approval
                            |
                 +----------+----------+
                 |                     |
               Accept                Modify
                 |                     |
                 v                     v
                END              Agent Decision
                                      |
                                      +------> Retrieve More
                                      |
                                      +------> Re-rank
```

The system supports conversational requests such as:

```text
Are there any other candidates?

Prioritize Java.

Get me the top 5 candidates.

Re-rank the candidates based on the feedback.
```

## Technologies

* Python
* LangChain
* LangGraph
* ChromaDB
* Hugging Face
* Sentence Transformers
* Semantic Chunking
* LLM Tool Calling
* Pydantic
* PyPDF

## Future Improvements

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

# RAG System Documentation
## Class 11 Biology RAG System

### Table of Contents
1. Project Overview
2. System Architecture
3. Tech Stack
4. Folder Structure
5. Dataset & Ingestion
6. Model Selection Strategy
7. API Key Management
8. Prompt Engineering
9. Retrieval & Grounding
10. Multilingual & Roman Urdu Support
11. Installation Guide
12. Running the Application
13. API Reference
14. Configuration Reference
15. Testing
16. Known Issues & Limitations
17. Future Improvements
18. Credits & References
19. Demo Video
20. GitHub Repository

---

### 1. Project Overview

*   **Project Name:** NCAI Class 11 Biology RAG System
*   **Subject/Class Covered:** Biology Class 11, PECTAA (Punjab Education, Curriculum, Training and Assessment Authority) Curriculum
*   **Developed By:** Azwar Waqar
*   **Date:** July 2026
*   **One-line Summary:** A specialized Retrieval-Augmented Generation (RAG) system that answers student questions, extracts exact textbook definitions, and retrieves specific educational figures and diagrams from the Class 11 Biology curriculum with strict hallucination prevention and explicit source citations.

**What does this project do?**
This project provides an interactive terminal interface for students to query the Class 11 Biology textbook and supplementary guides. It features a dual-retrieval pipeline: a semantic text retriever for answering conceptual questions with strict textbook grounding and a dedicated image retriever capable of identifying and extracting specific figures, diagrams, and photos based on user requests (e.g., "show figure 7.1"). It implements robust query routing to distinguish between semantic questions, explicit page/topic requests, and visual asset lookups, ensuring highly accurate and contextually bound responses.

---

### 2. System Architecture

**Architecture Diagram:**

```text
User Query (Terminal)
       |
       v
Query Intent Router (Regex/Logic)
       |
       +-----------------------------------+
       |                                   |
  Image Request? (e.g. "show fig 1.1")   Text Request? (e.g. "define osmosis")
       |                                   |
       v                                   v
Image Retriever Module                 Text Retriever Module (RAGPipeline)
       |                                   |
       +--> JSON Manifest Match?           +--> Page/Topic Native Filter?
       |        |                          |        |
       |        v                          |        v
       |    Return Image Path              |    Filter ChromaDB directly
       |                                   |
       +--> Semantic Caption Search        +--> Semantic Vector Search (BGE-M3)
                |                                   |
                v                                   v
            Return Image Metadata             Retrieve Top-K Chunks
                                                    |
                                                    v
                                              Context Formatting
                                                    |
                                                    v
                                              Prompt Builder (SYSTEM_RAG_PROMPT)
                                                    |
                                                    v
                                              LLM Generation (Gemini 2.5 Flash / Fallbacks)
                                                    |
                                                    v
                                              Response with Citations [Source | Chapter | Page] 

## 🛠️ Technology Stack

* **Language:** Python 3.10+
* **Core Framework:** LangChain Community
* **Embeddings:** `BAAI/bge-large-en-v1.5`
* **Vector Database:** ChromaDB (Local instances for both text and image captions)
* **LLM Engine:** `google-genai` (Primary) + Custom API Fallback routing
* **Image Processing:** Pillow (PIL)

---

## 🚀 Installation & Setup

Follow these detailed steps to run the RAG pipeline on your local machine.

### 1. Prerequisites
* Python 3.10 or higher
* Git

### 2. Clone the Repository
```bash
git clone [https://github.com/azwar-ml/Rag-biology.git](https://github.com/azwar-ml/Rag-biology.git)
cd Rag-biology
3. Initialize the Virtual Environment
Isolating dependencies ensures the system runs without conflicting with your global Python packages.

Bash
# Create the environment
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
4. Install Dependencies
Bash
pip install -r requirements.txt
5. Configure Environment Variables
The application requires API keys to function. A template is provided in the repository.

Copy the .env.example file to create your local configuration:

Bash
cp .env.example .env
Open the .env file and populate it with your API credentials:

Code snippet
GEMINI_API_KEY="your_gemini_api_key_here"
OPENROUTER_API_KEY="your_openrouter_api_key_here"
HUGGINGFACE_API_KEY="your_huggingface_api_key_here"
COHERE_API_KEY="your_cohere_api_key_here"
6. Verify Database Integrity
Ensure the pre-compiled vector databases and manifests exist in your project root before running the application:

vectordb/chroma/ (Contains textbook embeddings)

vector_db/chroma_images/ (Contains semantic image captions)

figure1_output copy/Biology-Manifest-Class11.json (Contains exact image routing paths)

💻 Usage & Query Guide
Launch the main terminal application to start interacting with the Biology database:

Bash
python app.py
 python -m uvicorn server:app --host 0.0.0.0 --port 8000 --reload  
  npm run dev 
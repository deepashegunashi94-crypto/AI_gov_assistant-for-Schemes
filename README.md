# AI-Powered Government Jobs, Schemes & Scholarship Assistant

An AI-powered conversational assistant that helps users discover relevant **government schemes, scholarships, and government job opportunities** based on their personal profile and requirements.

The system uses **Generative AI, Retrieval-Augmented Generation (RAG), semantic search, and profile-based filtering** to provide personalized and relevant information from government scheme data.

## 🚀 Features

- 💬 AI-powered conversational chatbot
- 🎯 Personalized government scheme recommendations
- 🔎 RAG-based semantic search
- 👤 Profile-based filtering using:
  - State
  - Education
  - Occupation
  - Category
  - Annual family income
  - Age
- 🏛️ Supports Central and State government schemes
- 📚 Government scholarship discovery
- 💼 Government job information support
- 🔗 Application and official information links
- 🧠 Semantic similarity search using FAISS
- 🤖 LLM-powered responses using Groq
- 📊 Structured government scheme dataset
- 🌐 Flask-based web application
🛠️ Technologies Used
Python
Flask
Generative AI
Groq LLM
RAG (Retrieval-Augmented Generation)
LangChain concepts
Sentence Transformers
FAISS
REST APIs
JSON
HTML/CSS
Git & GitHub
gov_assistant/
│
├── app/
│   ├── __init__.py
│   ├── routes.py
│   │
│   ├── rag/
│   │   ├── build_rag.py
│   │   ├── documents.py
│   │   ├── embeddings.py
│   │   ├── enrich_schemes.py
│   │   ├── prepare_documents.py
│   │   ├── scraper.py
│   │   └── search.py
│   │
│   └── templates/
│       └── index.html
│
├── data/
│   └── schemes/
│       ├── all_schemes.json
│       ├── balanced_schemes.json
│       ├── cleaned_schemes.json
│       ├── enriched_schemes.json
│       └── rag_documents.json
│
├── vectorstore/
│   ├── metadata.json
│   └── schemes.index
│
├── config.py
├── requirements.txt
├── run.py
├── README.md
└── .gitignore

🔍 How the RAG System Works

The system follows these main steps:

Government scheme information is collected and prepared.
Scheme data is cleaned and enriched.
Important scheme information is converted into searchable documents.
Documents are converted into embeddings using Sentence Transformers.
Embeddings are stored in a FAISS vector index.
When the user asks a question, the query is converted into an embedding.
FAISS retrieves semantically relevant schemes.
User profile information is used to re-rank and filter the retrieved schemes.
The relevant information is provided to the Groq LLM.
The LLM generates a natural-language response for the user

🎯 Personalized Scheme Search

The assistant does not use a fixed user profile.

Users can enter different information such as:

State: Karnataka
Education: B.E.
Occupation: Student
Category: General
Annual Family Income: ₹25,000
Age: 21

The system uses the information provided in that particular request to identify relevant schemes.

Different users can therefore receive different recommendations based on their individual profiles.

💡 Example
User
I am a 21-year-old engineering student from Karnataka.
My family income is ₹25,000 per year.
What government schemes or scholarships may be relevant to me?

🔐 Environment Variables

Create a .env file in the project root:

GROQ_API_KEY=your_groq_api_key
FLASK_SECRET_KEY=your_secret_key

Never commit your .env file to GitHub.

The project already includes .env in .gitignore.

⚙️ Installation

Clone the repository:

git clone https://github.com/deepashegunashi94-crypto/AI_gov_assistant-for-Schemes.git

Navigate to the project:

cd AI_gov_assistant-for-Schemes

Create a virtual environment:

python -m venv venv

Activate it on Windows:

venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Create your .env file and add your API keys.

▶️ Run the Application

Start the Flask application:

python run.py

Then open:

http://127.0.0.1:5000



👩‍💻 Author

Deepa Shegunashi

Final-Year Engineering Student
Interested in Generative AI, Machine Learning, RAG, and Full-Stack AI Applications.
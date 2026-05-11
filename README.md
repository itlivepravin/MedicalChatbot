# MedicalChatbot

MedicalChatbot is a Flask-based medical question-answering app that uses LangChain, OpenAI, and Pinecone to answer questions from indexed PDF documents.

## What this project does

- Loads PDF files from the `data` folder
- Splits the content into chunks and stores embeddings in Pinecone
- Serves a chat UI with Flask
- Answers questions using retrieval-augmented generation over your indexed documents

## Project structure

```text
MedicalChatbot/
├── app.py                  # Flask app and chat endpoints
├── store_index.py          # Loads PDFs and uploads embeddings to Pinecone
├── data/                   # Source PDF files
├── templates/chat.html     # Chat UI template
├── static/chat.css         # Chat UI styles
├── static/chat.js          # Chat UI behavior
└── src/
    ├── helper.py           # PDF loading, splitting, embeddings
    └── prompt.py           # System prompt for the chatbot
```

## Requirements

- Python 3.13
- A Pinecone account and API key
- An OpenAI API key

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/itlivepravin/MedicalChatbot.git
cd MedicalChatbot
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv medibot
.\medibot\Scripts\Activate.ps1
```

macOS/Linux:

```bash
python -m venv medibot
source medibot/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file in the project root

```ini
PINECONE_API_KEY="your-pinecone-api-key"
OPENAI_API_KEY="your-openai-api-key"
```

## Add your documents

Place your PDF files inside the `data` folder.

The current project already includes:

- `data/Medical_book.pdf`

## Build the Pinecone index

Run the indexing script once after adding or changing PDF files:

```bash
python store_index.py
```

What this does:

- Reads PDFs from `./data`
- Splits them into chunks
- Generates embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- Creates or updates the Pinecone index named `medical-chatbot`

## Run the application

```bash
python app.py
```

The Flask app starts on:

```text
http://localhost:8080
```

## Available routes

- `GET /` renders the chatbot UI
- `POST /chat` accepts a message and returns the generated answer and document sources

Example request body for the chat endpoint:

```json
{
  "message": "What does the document say about diabetes management?"
}
```

## Tech stack

- Python
- Flask
- LangChain
- OpenAI
- Pinecone
- Sentence Transformers

## Troubleshooting

### Missing API keys

If you see an error about missing `PINECONE_API_KEY` or `OPENAI_API_KEY`, check that your `.env` file exists in the project root and contains both keys.

### Empty or weak answers

- Make sure `python store_index.py` completed successfully
- Confirm your PDFs are present in the `data` folder
- Rebuild the index after changing documents

### Dependency issues

If your environment is outdated or partially installed, reactivate it and run:

```bash
pip install -r requirements.txt
```

## Notes

- The chat UI uses `templates/chat.html`, `static/chat.css`, and `static/chat.js`
- The current Flask app uses the `gpt-4o-mini` model in `app.py`
- The retrieval pipeline uses the prompt defined in `src/prompt.py`

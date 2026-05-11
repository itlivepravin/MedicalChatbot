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
- Gunicorn
- LangChain
- OpenAI
- Pinecone
- Sentence Transformers

## Run with Docker

### 1. Build the image

```bash
docker build -t medicalchatbot .
```

### 2. Run the container

```bash
docker run -p 8080:8080 \
  -e PINECONE_API_KEY="your-pinecone-api-key" \
  -e OPENAI_API_KEY="your-openai-api-key" \
  medicalchatbot
```

Then open:

```text
http://localhost:8080
```

## AWS deployment with Docker and CI/CD

This project can be deployed to AWS by building a Docker image, pushing it to Amazon ECR, and pulling it on an EC2 instance. A GitHub Actions workflow can automate the build and deploy steps.

### Architecture

- GitHub stores the source code
- GitHub Actions builds the Docker image on push
- Amazon ECR stores the image
- Amazon EC2 runs the container

### 1. Create an ECR repository

Create an ECR repository, for example:

```text
medicalchatbot
```

Save the repository URI. It will look like this:

```text
123456789012.dkr.ecr.us-east-1.amazonaws.com/medicalchatbot
```

### 2. Launch an EC2 instance

- Use Ubuntu
- Open inbound ports `22` and `8080`
- Install Docker on the instance

Example commands:

```bash
sudo apt-get update -y
sudo apt-get install -y docker.io
sudo usermod -aG docker ubuntu
newgrp docker
```

### 3. Prepare the EC2 host for deployment

Install the AWS CLI if needed, then log in to ECR from the instance and pull the image:

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/medicalchatbot:latest
```

Run the container:

```bash
docker run -d --name medicalchatbot \
  -p 8080:8080 \
  -e PINECONE_API_KEY="your-pinecone-api-key" \
  -e OPENAI_API_KEY="your-openai-api-key" \
  123456789012.dkr.ecr.us-east-1.amazonaws.com/medicalchatbot:latest
```

### 4. Add GitHub repository secrets

Add these secrets in GitHub:

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_REGION`
- `ECR_REPOSITORY`
- `EC2_HOST`
- `EC2_USERNAME`
- `EC2_SSH_KEY`
- `PINECONE_API_KEY`
- `OPENAI_API_KEY`

### 5. Create a GitHub Actions workflow

Create `.github/workflows/deploy.yml` with steps that:

- check out the repository
- configure AWS credentials
- log in to Amazon ECR
- build and push the Docker image
- SSH into EC2 and restart the container

Example workflow:

```yaml
name: Deploy To AWS

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}

      - name: Login to Amazon ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build and push image
        env:
          ECR_REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          ECR_REPOSITORY: ${{ secrets.ECR_REPOSITORY }}
          IMAGE_TAG: latest
        run: |
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
          docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG

      - name: Deploy on EC2
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USERNAME }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            aws ecr get-login-password --region ${{ secrets.AWS_REGION }} | docker login --username AWS --password-stdin ${{ steps.login-ecr.outputs.registry }}
            docker pull ${{ steps.login-ecr.outputs.registry }}/${{ secrets.ECR_REPOSITORY }}:latest
            docker stop medicalchatbot || true
            docker rm medicalchatbot || true
            docker run -d --name medicalchatbot -p 8080:8080 \
              -e PINECONE_API_KEY='${{ secrets.PINECONE_API_KEY }}' \
              -e OPENAI_API_KEY='${{ secrets.OPENAI_API_KEY }}' \
              ${{ steps.login-ecr.outputs.registry }}/${{ secrets.ECR_REPOSITORY }}:latest
```

### 6. Access the application

After deployment, open:

```text
http://<your-ec2-public-ip>:8080
```

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
- The Docker image starts the app with Gunicorn on port `8080`

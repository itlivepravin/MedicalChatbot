import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore

from src.helper import embeddings
from src.prompt import system_prompt


load_dotenv()

INDEX_NAME = "medical-chatbot"

app = Flask(__name__)

_rag_chain = None


def get_rag_chain():
	global _rag_chain

	if _rag_chain is not None:
		return _rag_chain

	pinecone_api_key = os.getenv("PINECONE_API_KEY")
	openai_api_key = os.getenv("OPENAI_API_KEY")

	if not pinecone_api_key or not openai_api_key:
		raise RuntimeError(
			"Missing PINECONE_API_KEY or OPENAI_API_KEY. Add them to your .env file before starting the app."
		)

	vector_store = PineconeVectorStore(index_name=INDEX_NAME, embedding=embeddings)
	retriever = vector_store.as_retriever(search_kwargs={"k": 3})

	prompt = ChatPromptTemplate.from_messages(
		[
			("system", system_prompt),
			("human", "{input}"),
		]
	)

	llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
	question_answer_chain = create_stuff_documents_chain(llm, prompt)
	_rag_chain = create_retrieval_chain(retriever, question_answer_chain)
	return _rag_chain


@app.get("/")
def index():
	return render_template("chat.html")


@app.post("/chat")
def chat():
	data = request.get_json(silent=True) or request.form
	user_message = (data.get("message") or "").strip()

	if not user_message:
		return jsonify({"error": "Please enter a message."}), 400

	try:
		response = get_rag_chain().invoke({"input": user_message})
	except Exception as exc:
		return jsonify({"error": str(exc)}), 500

	context_docs = response.get("context", [])
	sources = []
	for document in context_docs:
		source = document.metadata.get("source")
		if source and source not in sources:
			sources.append(source)

	return jsonify(
		{
			"answer": response.get("answer", "I couldn't generate a response."),
			"sources": sources,
		}
	)


if __name__ == "__main__":
	app.run(host="0.0.0.0", port=8080, debug=True)

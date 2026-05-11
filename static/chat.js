const form = document.getElementById("chat-form");
const input = document.getElementById("message");
const messages = document.getElementById("messages");
const statusLabel = document.getElementById("status");
const sendButton = document.getElementById("send-button");

function addMessage(role, content, sources = []) {
	const article = document.createElement("article");
	article.className = `message ${role}`;

	const label = document.createElement("span");
	label.className = "message-label";
	label.textContent = role === "user" ? "You" : role === "error" ? "Error" : "Assistant";

	const body = document.createElement("div");
	body.textContent = content;

	article.append(label, body);

	if (sources.length) {
		const sourceBlock = document.createElement("div");
		sourceBlock.className = "sources";
		sourceBlock.textContent = `Sources: ${sources.join(", ")}`;
		article.appendChild(sourceBlock);
	}

	messages.appendChild(article);
	messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(message) {
	statusLabel.textContent = "Thinking...";
	sendButton.disabled = true;

	try {
		const response = await fetch("/chat", {
			method: "POST",
			headers: {
				"Content-Type": "application/json"
			},
			body: JSON.stringify({ message })
		});

		const payload = await response.json();

		if (!response.ok) {
			throw new Error(payload.error || "The chatbot request failed.");
		}

		addMessage("bot", payload.answer, payload.sources || []);
		statusLabel.textContent = "Ready";
	} catch (error) {
		addMessage("error", error.message);
		statusLabel.textContent = "Failed";
	} finally {
		sendButton.disabled = false;
		input.focus();
	}
}

form.addEventListener("submit", async (event) => {
	event.preventDefault();

	const message = input.value.trim();
	if (!message) {
		return;
	}

	addMessage("user", message);
	input.value = "";
	await sendMessage(message);
});

input.addEventListener("keydown", (event) => {
	if (event.key === "Enter" && !event.shiftKey) {
		event.preventDefault();
		form.requestSubmit();
	}
});

input.focus();

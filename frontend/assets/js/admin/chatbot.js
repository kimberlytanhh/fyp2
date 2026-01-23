const API_URL = "http://127.0.0.1:8000/chatbot/admin";

function toggleSidebar() {
  document.getElementById("sidebar").classList.toggle("collapsed");
}

function appendMessage(text, sender) {
  const chat = document.getElementById("chatMessages");

  const bubble = document.createElement("div");
  bubble.className = sender === "user" ? "chat-user" : "chat-bot";
  bubble.textContent = text;

  chat.appendChild(bubble);
  chat.scrollTop = chat.scrollHeight;
}


async function sendMessage() {
  const input = document.getElementById("chatInput");
  const question = input.value.trim();

  if (!question) return;

  appendMessage(question, "user");
  input.value = "";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ question })
    });

    if (!response.ok) {
      appendMessage("⚠️ Unable to get a response from the server.", "bot");
      return;
    }

    const data = await response.json();
    appendMessage(data.answer, "bot");

  } catch (err) {
    appendMessage("⚠️ Server error. Please try again.", "bot");
  }
}

// Allow Enter key to send
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("chatInput").addEventListener("keydown", e => {
    if (e.key === "Enter") sendMessage();
  });
});

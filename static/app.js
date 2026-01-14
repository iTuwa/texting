const chatLog = document.getElementById("chat-log");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

let history = [];
let isSending = false;

function scrollToBottom() {
  chatLog.scrollTop = chatLog.scrollHeight;
}

function createMessageRow(role, text, isTyping = false) {
  const row = document.createElement("div");
  row.className = `message-row ${role}`;

  if (role === "assistant") {
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "N";
    row.appendChild(avatar);
  }

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (isTyping) {
    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.className = "typing-dot";
      indicator.appendChild(dot);
    }
    bubble.appendChild(indicator);
  } else {
    const p = document.createElement("p");
    p.textContent = text;
    bubble.appendChild(p);
  }

  row.appendChild(bubble);
  return row;
}

function addMessage(role, text) {
  const row = createMessageRow(role, text, false);
  chatLog.appendChild(row);
  scrollToBottom();
}

function addTypingIndicator() {
  const row = createMessageRow("assistant", "", true);
  row.dataset.typing = "true";
  chatLog.appendChild(row);
  scrollToBottom();
  return row;
}

function removeTypingIndicator(row) {
  if (row && row.parentNode) {
    row.parentNode.removeChild(row);
  }
}

async function sendMessageToServer(message) {
  const payload = {
    message,
    history,
  };

  const res = await fetch("/api/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(errText || `Request failed with status ${res.status}`);
  }

  return res.json();
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (isSending) return;

  const text = userInput.value.trim();
  if (!text) return;

  isSending = true;
  userInput.value = "";
  userInput.style.height = "auto";

  addMessage("user", text);
  history.push({ role: "user", content: text });

  const typingRow = addTypingIndicator();

  try {
    const data = await sendMessageToServer(text);
    const reply = data.reply || "I could not generate a reply. Please try again.";
    removeTypingIndicator(typingRow);
    addMessage("assistant", reply);
    history.push({ role: "assistant", content: reply });
  } catch (err) {
    console.error(err);
    removeTypingIndicator(typingRow);
    addMessage(
      "assistant",
      "Sorry, something went wrong while contacting the NIMS assistant. Please check your network and try again."
    );
  } finally {
    isSending = false;
  }
});

// Auto-grow textarea
userInput.addEventListener("input", () => {
  userInput.style.height = "auto";
  userInput.style.height = `${userInput.scrollHeight}px`;
});

// Send on Enter (without Shift)
userInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.dispatchEvent(new Event("submit"));
  }
});

// Ensure we start at the latest message on initial load
window.addEventListener("load", () => {
  scrollToBottom();
});

const token = localStorage.getItem("token");
const username = localStorage.getItem("username");
let sessionId = localStorage.getItem("sessionId") || null;
const historyPanel = document.getElementById("historyPanel"); // If history is in a sidebar


if (!token || !username) {
  alert("Please login first.");
  window.location.href = "login.html";
}

let historyBuffer = []; // Store chat temporarily before session ends

document.addEventListener("DOMContentLoaded", () => {
  fetchHistory();
  document.getElementById("newChatBtn").addEventListener("click", startNewChat);
});

async function sendQuery() {
  const queryInput = document.getElementById("queryInput");
  const query = queryInput.value.trim();
  if (!query) return;

  appendToChat("You", query);
  queryInput.value = "";

  try {
    const res = await fetch("http://localhost:8010/ask", {
      method: "POST",
      headers: {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ query })
    });

    if (res.ok) {
      try {
        const data = await res.json();
        appendToChat("Bot", data.answer);
        sessionId = data.session_id;
        historyBuffer.push({ query: query, answer: data.answer });
      } catch (jsonErr) {
        console.error("⚠️ Error parsing response JSON:", jsonErr);
        appendToChat("Bot", "⚠️ There was a delay or parsing issue. Please try again.");
      }
  } else if (res.status === 401) {
      const errorText = await res.text();
      console.warn("🔐 Unauthorized (token expired or invalid):", errorText);
      alert("⚠️ Session expired. Please login again.");
      logout();
  } else {
    const errorText = await res.text();
    console.error("❌ Server error:", res.status, errorText);
    appendToChat("Bot", "❌ Something went wrong. Please try again.");
  }
} catch (err) {
  console.error("❗ Network or unexpected error:", err);
  appendToChat("Bot", "❗ A network error occurred. Please check your connection and try again.");
} finally {
  // Optional cleanup or UI reset logic
  console.log("🔄 Request completed");
  // e.g. hide loading spinner
}
}

function appendToChat(sender, message) {
  const chatBox = document.getElementById("chatBox");
  const msg = document.createElement("div");
  msg.className = "mb-2";
  msg.innerHTML = `<strong>${sender}:</strong> ${message}`;
  chatBox.appendChild(msg);
  chatBox.scrollTop = chatBox.scrollHeight;
}

function clearChat() {
  document.getElementById("chatBox").innerHTML = "";
}

function logout() {
  localStorage.clear();
  window.location.href = "login.html";
}

function addToHistory(query, answer) {
  const historyList = document.getElementById("historyList");

  const exists = Array.from(historyList.children).some(
    (item) => item.dataset.query === query
  );
  if (exists) return;

  const item = document.createElement("li");
  item.className = "cursor-pointer text-blue-600 hover:underline text-sm mb-1";
  item.dataset.query = query;
  item.textContent = query.length > 40 ? query.slice(0, 40) + "..." : query;

  item.onclick = () => {
    clearChat();
    appendToChat("You", query);
    appendToChat("Bot", answer);
  };

  historyList.appendChild(item);
}

async function fetchHistory() {
  try {
    const res = await fetch("http://localhost:8010/history", {
      method: "GET",
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (res.ok) {
      const data = await res.json();
      for (const session of Object.values(data)) {
        for (const item of session) {
          addToHistory(item.query, item.answer);
        }
      }
    } else if (res.status === 401) {
      alert("Session expired. Please login again.");
      logout();
    }
  } catch (error) {
    console.error("Fetch history error:", error);
  }
}

// Called when user ends or resets chat
async function startNewChat() {
  if (sessionId && historyBuffer.length > 0) {
    try {
      const res = await fetch("http://localhost:8010/end_session", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (res.ok) {
        for (const { query, answer } of historyBuffer) {
          addToHistory(query, answer);
        }
      } else {
        console.warn("⚠️ Failed to finalize session");
      }
    } catch (err) {
      console.error("Session end error:", err);
    }
  }

  sessionId = null;
  historyBuffer = [];
  clearChat();
}

document.getElementById("newChatBtn").addEventListener("click", async () => {
  if (sessionId) {
    try {
      await fetch("http://localhost:8010/end_session", {
        method: "POST",
        headers: {
          "Authorization": "Bearer " + token,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: "", session_id: sessionId }),
      });
    } catch (err) {
      console.warn("⚠️ Error finalizing session:", err);
    }
  }

  sessionId = null;
  localStorage.removeItem("sessionId");
  clearChat();
  historyBuffer.length = 0; // Reset local history
});

document.getElementById("toggleHistoryBtn").addEventListener("click", () => {
  if (historyPanel) {
    historyPanel.classList.toggle("hidden");
  }
});


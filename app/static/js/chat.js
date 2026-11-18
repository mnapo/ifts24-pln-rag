(() => {
  const form = document.querySelector("#chat-form");
  const input = document.querySelector("#message-input");
  const sendButton = document.querySelector("#send-button");
  const messagesElement = document.querySelector("#messages");
  const welcome = document.querySelector("#welcome");
  const conversation = document.querySelector("#conversation");
  const newChatButton = document.querySelector("#new-chat");
  const storageKey = "pln-rag-conversation";
  let history = [];
  let sending = false;

  try {
    const saved = JSON.parse(sessionStorage.getItem(storageKey) || "[]");
    if (Array.isArray(saved)) {
      history = saved.filter(item =>
        item && ["user", "assistant"].includes(item.role) &&
        typeof item.content === "string"
      ).slice(-30);
    }
  } catch {
    history = [];
  }

  function persist() {
    try { sessionStorage.setItem(storageKey, JSON.stringify(history)); } catch {}
  }

  function addMessage(role, content) {
    const article = document.createElement("article");
    article.className = `message ${role}`;

    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = role === "assistant" ? "✳" : "TÚ";

    const body = document.createElement("div");
    body.className = "message-content";

    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = role === "assistant" ? "Asistente" : "Tú";

    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = content;

    body.append(label, bubble);
    article.append(avatar, body);
    messagesElement.append(article);
    welcome.hidden = true;
    conversation.scrollTop = conversation.scrollHeight;
    return article;
  }

  function showTyping() {
    const article = document.createElement("article");
    article.className = "message";
    article.id = "typing-indicator";
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "✳";
    const body = document.createElement("div");
    body.className = "message-content";
    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = "El asistente está escribiendo";
    const dots = document.createElement("div");
    dots.className = "typing";
    dots.innerHTML = "<i></i><i></i><i></i>";
    body.append(label, dots);
    article.append(avatar, body);
    messagesElement.append(article);
    conversation.scrollTop = conversation.scrollHeight;
  }

  function showError(message) {
    const article = document.createElement("article");
    article.className = "message error";
    const avatar = document.createElement("div");
    avatar.className = "avatar";
    avatar.textContent = "!";
    const body = document.createElement("div");
    body.className = "message-content";
    const label = document.createElement("div");
    label.className = "message-label";
    label.textContent = "Error";
    const bubble = document.createElement("div");
    bubble.className = "bubble";
    bubble.textContent = message;
    body.append(label, bubble);
    article.append(avatar, body);
    messagesElement.append(article);
    conversation.scrollTop = conversation.scrollHeight;
  }

  async function sendMessage(rawText) {
    const content = rawText.trim();
    if (!content || sending) return;

    sending = true;
    input.value = "";
    input.style.height = "auto";
    sendButton.disabled = true;
    addMessage("user", content);
    const requestMessages = [...history, { role: "user", content }].slice(-30);
    showTyping();

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 25000);
      let response;
      let responseText = "";
      try {
        response = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ messages: requestMessages }),
          signal: controller.signal
        });
        responseText = await response.text();
      } catch (error) {
        if (error && error.name === "AbortError") {
          throw new Error("La solicitud superó el tiempo de espera. Inténtalo nuevamente.");
        }
        throw new Error(`No se pudo conectar con el servidor: ${error instanceof Error ? error.message : String(error)}`);
      } finally {
        clearTimeout(timeoutId);
      }

      let data = {};
      try {
        data = responseText ? JSON.parse(responseText) : {};
      } catch {
        data = {};
      }
      if (!response.ok) {
        const detail = typeof data.detail === "string"
          ? data.detail
          : Array.isArray(data.detail)
            ? data.detail.map(item => item.msg || JSON.stringify(item)).join("\n")
            : responseText.trim().slice(0, 1200) ||
              `Error HTTP ${response.status}: ${response.statusText || "El servidor no pudo procesar el mensaje."}`;
        throw new Error(detail);
      }
      if (typeof data.message !== "string" || !data.message.trim()) {
        throw new Error("El servidor devolvió una respuesta vacía o con formato inválido.");
      }
      history = [...requestMessages, { role: "assistant", content: data.message }].slice(-30);
      persist();
      document.querySelector("#typing-indicator")?.remove();
      addMessage("assistant", data.message);
    } catch (error) {
      document.querySelector("#typing-indicator")?.remove();
      showError(error instanceof Error ? error.message : String(error));
    } finally {
      sending = false;
      sendButton.disabled = false;
      input.focus();
    }
  }

  form.addEventListener("submit", event => {
    event.preventDefault();
    sendMessage(input.value);
  });

  input.addEventListener("input", () => {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 140) + "px";
  });

  input.addEventListener("keydown", event => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      form.requestSubmit();
    }
  });

  document.querySelectorAll("[data-prompt]").forEach(button => {
    button.addEventListener("click", () => sendMessage(button.dataset.prompt));
  });

  newChatButton.addEventListener("click", () => {
    if (sending) return;
    history = [];
    persist();
    messagesElement.replaceChildren();
    welcome.hidden = false;
    input.value = "";
    input.focus();
  });

  history.forEach(message => addMessage(message.role, message.content));
  if (history.length) welcome.hidden = true;
})();

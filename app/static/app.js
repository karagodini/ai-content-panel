let currentMode = "post";

const chat = document.getElementById("chat");
const msgInput = document.getElementById("msg");
const sendBtn = document.getElementById("send");

document.querySelectorAll(".mode").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelector(".mode.active").classList.remove("active");
    btn.classList.add("active");
    currentMode = btn.dataset.mode;
    msgInput.placeholder = {
      post:  "Тема поста, например: запуск онлайн-курса по нейросетям…",
      title: "О чём пост? Например: как экономить на подписках",
      idea:  "Ваша ниша, например: бьюти-салон в Казани",
      image: "Опишите картинку, например: кот в очках за ноутбуком, стиль киберпанк",
    }[currentMode];
  });
});

function addMsg(text, who, imageUrl) {
  const div = document.createElement("div");
  div.className = "msg " + who;
  if (imageUrl) {
    const img = document.createElement("img");
    img.src = imageUrl;
    div.appendChild(img);
  } else {
    div.textContent = text;
  }
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

async function send() {
  const text = msgInput.value.trim();
  if (!text) return;
  msgInput.value = "";
  addMsg(text, "user");
  sendBtn.disabled = true;

  const loading = addMsg("Думаю…", "bot");

  try {
    const resp = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text, mode: currentMode }),
    });
    const data = await resp.json();
    loading.remove();
    if (data.image_url) {
      addMsg("", "bot", data.image_url);
    } else {
      addMsg(data.reply, "bot");
    }
  } catch (e) {
    loading.textContent = "Ошибка: " + e.message;
  } finally {
    sendBtn.disabled = false;
    msgInput.focus();
  }
}

sendBtn.addEventListener("click", send);
msgInput.addEventListener("keydown", e => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
});

import json
import urllib.parse
import urllib.request

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="AI Content Panel")

TEXT_API = "https://text.pollinations.ai/"
IMAGE_API = "https://image.pollinations.ai/prompt/"

# Режимы работы чата: промпт для модели под каждую задачу
MODES = {
    "post": (
        "Ты — SMM-копирайтер. Напиши один цепляющий пост для соцсетей "
        "на тему пользователя. Структура: хук в первой строке, основной текст, "
        "призыв к действию. В конце добавь 3-5 хэштегов. Пиши на русском."
    ),
    "title": (
        "Ты — SMM-специалист. Придумай 5 вариантов коротких, цепляющих "
        "заголовков для поста в соцсетях на тему пользователя. "
        "Каждый заголовок — с новой строки, с номером. Пиши на русском."
    ),
    "idea": (
        "Ты — контент-маркетолог. Предложи 5 идей для постов или коротких "
        "видео на тему пользователя: название идеи и 1-2 предложения сути. "
        "Пиши на русском."
    ),
}


class ChatRequest(BaseModel):
    message: str
    mode: str = "post"


class ChatResponse(BaseModel):
    reply: str
    image_url: str | None = None


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    # Режим "картинка": Pollinations генерирует изображение по URL, без ключа
    if req.mode == "image":
        prompt = urllib.parse.quote(req.message)
        url = f"{IMAGE_API}{prompt}?width=1024&height=1024&nologo=true"
        return ChatResponse(reply=req.message, image_url=url)

    system = MODES.get(req.mode, MODES["post"])
    payload = json.dumps({
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": req.message},
        ],
        "model": "openai",
        "private": True,
    }).encode("utf-8")

    request = urllib.request.Request(
        TEXT_API, data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=90) as resp:
        reply = resp.read().decode("utf-8")

    return ChatResponse(reply=reply.strip())


app.mount("/static", StaticFiles(directory="app/static"), name="static")

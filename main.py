from typing import Optional
from fastapi import Depends, FastAPI, HTTPException, Header
from datetime import datetime
import uuid
from models.pandora_models import ChatRequest, ChatResponse, ChatMessage, Choice, Usage
from bots.async_pandora_chat_bot import PandoraChatBot

app = FastAPI()
models_by_type = {}


async def get_chat_bot(model_type: str) -> PandoraChatBot:
    global models_by_type
    if model_type not in models_by_type or models_by_type[model_type] is None:
        models_by_type[model_type] = await PandoraChatBot.create()
    return models_by_type[model_type]


async def verify_authorization(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(request: ChatRequest,
                           _: bool = Depends(verify_authorization)):
    chat_bot = await get_chat_bot(request.model)
    if chat_bot is None:
        return build_error_response(request.model)

    await chat_bot.send_message(request.messages[-1].content)
    response_message = await chat_bot.receive_message()

    return build_chat_response(request.model, chat_bot.id, response_message)


def build_error_response(model: str) -> ChatResponse:
    return ChatResponse(id=f"chatgpt-{uuid.uuid4().hex[:6]}",
                        object="error",
                        created=int(datetime.now().timestamp()),
                        model=model,
                        choices=[
                            Choice(index=0,
                                   message=ChatMessage(
                                       role="system",
                                       content="Something went wrong!"),
                                   finish_reason="stop")
                        ],
                        usage=Usage(prompt_tokens=0,
                                    completion_tokens=0,
                                    total_tokens=0))


def build_chat_response(model: str, system_fingerprint: str,
                        response_message: str) -> ChatResponse:
    return ChatResponse(id=f"chatgpt-{uuid.uuid4().hex[:6]}",
                        object="chat.completion",
                        created=int(datetime.now().timestamp()),
                        model=model,
                        system_fingerprint=system_fingerprint,
                        choices=[
                            Choice(index=0,
                                   message=ChatMessage(
                                       role="assistant",
                                       content=response_message),
                                   finish_reason="stop")
                        ],
                        usage=Usage(prompt_tokens=0,
                                    completion_tokens=0,
                                    total_tokens=0))


# 主程序入口
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app",
                host="0.0.0.0",
                port=8000,
                reload=True,
                timeout_keep_alive=60)

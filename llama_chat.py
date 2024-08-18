from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import aiohttp
import logging

# Logging configuration
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# FastAPI application instance
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration placeholder for the base URL
OLLAMA_BASE_URL = "https://ollama.martina-home.online/api/chat"

# Model for chat message
class ChatMessage(BaseModel):
    role: str
    content: str

# Model for the chat completion request
class GenerateChatCompletionForm(BaseModel):
    model: str
    messages: list[ChatMessage]
    stream: bool = True

# Timeout setting for aiohttp
timeout = aiohttp.ClientTimeout(total=60)  # 60 seconds timeout

# Helper function to post data and stream response
async def post_streaming_url(url: str, payload: dict):
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(url, json=payload) as r:
                r.raise_for_status()

                async def stream_generator():
                    async for chunk in r.content.iter_chunked(1024):
                        yield chunk

                return StreamingResponse(
                    stream_generator(),
                    status_code=r.status,
                    headers=dict(r.headers)
                )

    except aiohttp.ClientConnectionError as e:
        log.error("Connection closed by server", exc_info=True)
        raise HTTPException(status_code=500, detail="Connection closed by server")
    except Exception as e:
        error_detail = str(e)
        log.error("Error occurred during streaming", exc_info=True)
        raise HTTPException(status_code=500, detail=error_detail)

# Endpoint to handle chat completion requests
@app.post("/api/chat")
async def generate_chat_completion(form_data: GenerateChatCompletionForm):
    payload = form_data.dict(exclude_none=True)

    # Add model version if not provided
    if ":" not in payload["model"]:
        payload["model"] = f"{payload['model']}:latest"

    url = OLLAMA_BASE_URL
    log.info(f"Sending request to: {url} with payload: {payload}")

    return await post_streaming_url(url, payload)

# Endpoint to check the server status
@app.get("/")
async def get_status():
    return {"status": "Server is up and running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

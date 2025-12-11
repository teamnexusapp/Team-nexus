from fastapi import APIRouter, HTTPException
from schema import MessageRequest, MessageResponse
import os
import cohere
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set!")

co = cohere.Client(COHERE_API_KEY)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=MessageResponse)
def chat_with_ai(request: MessageRequest):
    try:
        response = co.chat(
            model="command-xlarge-nightly",
            message=request.message,
            max_tokens=180,
            temperature=0.7
        )

       
        if hasattr(response, "message"):
            reply = response.message
        elif hasattr(response, "output"):
            reply = response.output[0].content.strip()
        else:
            reply = str(response)

        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI request failed: {e}")

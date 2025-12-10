import os
import cohere
from dotenv import load_dotenv

load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("COHERE_API_KEY is not set in your environment!")

co = cohere.Client(COHERE_API_KEY)


def hf_generate(prompt: str) -> str:

    try:
      
        response = co.chat(
            model="command-xlarge-nightly",
            message=prompt,    
            max_tokens=180,
            temperature=0.7
        )
       
        if hasattr(response, "message"):
            return response.message
        elif hasattr(response, "output"):
            return response.output[0].content.strip()
        else:
            return str(response)
    except Exception as e:
        return f"AI request failed: {e}"

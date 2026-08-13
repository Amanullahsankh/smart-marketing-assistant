import logging
import os
import time
import json
from dotenv import load_dotenv
from groq import Groq

logger = logging.getLogger(__name__)
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

try:
    ai_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {e}")
    ai_client = None

def generate_ai_response(
    prompt: str,
    model: str = "llama-3.1-8b-instant",
    max_tokens: int = 500,
    temperature: float = 0.3,
    json_mode: bool = False,
    system_prompt: str = "You are a helpful AI assistant."
):
    """
    Generate an AI response using Groq with exponential backoff for rate limits (429).
    """
    if not ai_client:
        logger.error("Groq client not initialized. Returning fallback.")
        return [] if json_mode else ""

    max_retries = 3
    base_delay = 5 # Start with 5 seconds delay for rate limit

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    for attempt in range(max_retries):
        try:
            logger.info(f"AI Request ({model}) - Attempt {attempt + 1}/{max_retries} [max_tokens: {max_tokens}]")
            response = ai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content.strip()

            if json_mode:
                if content.startswith("```json"):
                    content = content[7:]
                elif content.startswith("```"):
                    content = content[3:]
                
                if content.endswith("```"):
                    content = content[:-3]
                
                try:
                    return json.loads(content.strip())
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON response: {e}\nContent: {content}")
                    return []
            
            return content

        except Exception as e:
            error_str = str(e).lower()
            # Handle rate limits or token limits
            if "429" in error_str or "rate limit" in error_str or "tokens per day" in error_str:
                if attempt < max_retries - 1:
                    sleep_time = base_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit. Retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    logger.error("Rate limit retry exhausted. Returning fallback.")
                    return [] if json_mode else ""
            else:
                logger.error(f"AI Request failed due to unexpected error: {e}")
                return [] if json_mode else ""
    
    return [] if json_mode else ""

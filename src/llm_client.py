import os
import time
from groq import Groq
from dotenv import load_dotenv

# Load env vars once
load_dotenv()

class LLMClient:
    def __init__(self, api_key: str = None, model: str = "llama-3.1-70b-versatile"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            # Check if streamlit secrets works (later) or just raise
            pass
            
        self.client = Groq(api_key=self.api_key)
        self.model = model

    def query(self, prompt: str, system: str = None) -> str:
        """
        Send query to Groq and return response text.
        Retries on rate limit.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        
        messages.append({"role": "user", "content": prompt})
        
        # Simple retry logic
        max_retries = 3
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                chat_completion = self.client.chat.completions.create(
                    messages=messages,
                    model=self.model,
                    temperature=0.0, # Deterministic for code
                    max_tokens=4096, # Huge window for code
                    stop=None,
                    stream=False,
                )
                return chat_completion.choices[0].message.content
            
            except Exception as e:
                # Naive error handling, primarily for rate limits
                if "429" in str(e) or "rate limit" in str(e).lower():
                    sleep_time = base_delay * (2 ** attempt)
                    print(f"Rate limit hit, retrying in {sleep_time}s...")
                    time.sleep(sleep_time)
                else:
                    raise e
                    
        raise Exception("Max retries exceeded for LLM query")

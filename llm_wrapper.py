import time
from crewai import LLM
import os
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

def get_gemini_llm_with_retry(model='gemini/gemini-2.5-pro', temperature=0.0, max_retries=5, base_delay=2):
    """
    Retorna uma função LLM com retry/backoff para lidar com erro 429 (TooManyRequests).
    """
    def llm_call_with_retry(*args, **kwargs):
        retries = 0
        while True:
            try:
                llm = LLM(
                    model=model,
                    api_key=gemini_api_key,
                    temperature=temperature
                )
                return llm(*args, **kwargs)
            except Exception as e:
                if '429' in str(e) or 'TooManyRequests' in str(e):
                    if retries < max_retries:
                        wait = base_delay * (2 ** retries)
                        print(f"[LLM] 429 TooManyRequests. Retry {retries+1}/{max_retries} in {wait}s...")
                        time.sleep(wait)
                        retries += 1
                    else:
                        print("[LLM] Max retries reached. Raising exception.")
                        raise
                else:
                    raise
    return llm_call_with_retry

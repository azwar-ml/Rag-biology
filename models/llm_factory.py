import requests
from google import genai
from google.genai import types
from key_manager import key_manager
from dotenv import load_dotenv

load_dotenv()

class LLMFactory:
    @classmethod
    def generate_response(cls, prompt: str, system_instruction: str = None) -> str: # type: ignore 
        max_retries = key_manager.total_configs
        attempts = 0

        while attempts < max_retries:
            config = key_manager.get_current_config()
            provider = config["provider"]
            api_key = config["key"]
            model = config["model"]

            try:
                if provider == "gemini":
                    client = genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model,
                        contents=prompt,
                        # CHANGED: temperature=0.0 for strict verbatim extraction
                        config=types.GenerateContentConfig(temperature=0.0, system_instruction=system_instruction)
                    )
                    if response.text: return response.text
                    else: raise Exception("Empty response from Gemini")

                elif provider == "openrouter":
                    res = requests.post(
                        "https://openrouter.ai/api/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        # CHANGED: temperature: 0.0
                        json={"model": model, "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}], "temperature": 0.0}
                    )
                    if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
                    else: raise Exception(f"OpenRouter Error: {res.text}")

                elif provider == "huggingface":
                    res = requests.post(
                        f"https://api-inference.huggingface.co/models/{model}/v1/chat/completions",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        # CHANGED: temperature: 0.0
                        json={"model": model, "messages": [{"role": "system", "content": system_instruction}, {"role": "user", "content": prompt}], "temperature": 0.0, "max_tokens": 1000}
                    )
                    if res.status_code == 200: return res.json()["choices"][0]["message"]["content"]
                    else: raise Exception(f"HuggingFace Error: {res.text}")

                elif provider == "cohere":
                    res = requests.post(
                        "https://api.cohere.com/v1/chat",
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        # CHANGED: temperature: 0.0
                        json={"model": model, "message": prompt, "preamble": system_instruction, "temperature": 0.0}
                    )
                    if res.status_code == 200: return res.json()["text"]
                    else: raise Exception(f"Cohere Error: {res.text}")
                        
            # ... [keep the bottom part of the file the same] ...
                        
            except Exception as e:
                # Print the exact error so we know WHY it failed
                print(f" -> [Debug] {provider.upper()} Error: {str(e)}")
                
                # Fallback to the next provider
                key_manager.mark_config_exhausted()
                attempts += 1
                
        return "Error: All 5 AI providers failed. Please try again later."
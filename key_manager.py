import os
from dotenv import load_dotenv

load_dotenv()

class MultiProviderKeyManager:
    def __init__(self):
        # The fallback loop: Provider -> Key -> Heavy Free Model
        # The fallback loop: Provider -> Key -> Heavy Free Model
        raw_configs = [
            # 1. Gemini (Switched to 2.5-flash which we know works flawlessly)
            {"provider": "gemini", "key": os.getenv("GEMINI_API_KEY_1"), "model": "gemini-2.5-flash"},
            
            # 2. OpenRouter (Using Gemma 2 9B Free since Llama 3.1 is now paid)
            {"provider": "openrouter", "key": os.getenv("OPENROUTER_API_KEY_1"), "model": "google/gemma-2-9b-it:free"},
            
            # 3. HuggingFace (Model is fine, your internet just timed out earlier)
            {"provider": "huggingface", "key": os.getenv("HF_API_KEY_1"), "model": "mistralai/Mistral-Nemo-Instruct-2407"},
            
            # 4. Cohere (Updated to active command-r-plus model)
            {"provider": "cohere", "key": os.getenv("COHERE_API_KEY_1"), "model": "command-r-plus"},
            
            # 5. OpenRouter Backup (Microsoft Phi-3 Free)
            {"provider": "openrouter", "key": os.getenv("BACKUP_API_KEY"), "model": "microsoft/phi-3-mini-128k-instruct:free"}
        ]
        
        # Only keep providers where you actually pasted a key in the .env
        self.configs = [c for c in raw_configs if c["key"] and c["key"].strip()]
        
        if not self.configs:
            raise ValueError("CRITICAL ERROR: No API keys found in .env file.")
            
        self.current_index = 0
        self.total_configs = len(self.configs)

    def get_current_config(self) -> dict:
        return self.configs[self.current_index]

    def mark_config_exhausted(self):
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % self.total_configs
        next_config = self.configs[self.current_index]
        print(f"\n[!] Provider {self.configs[old_index]['provider']} failed. Switching to {next_config['provider']} ({next_config['model']})...")

# Singleton instance
key_manager = MultiProviderKeyManager()
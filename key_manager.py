import os
from dotenv import load_dotenv

load_dotenv()

class MultiProviderKeyManager:
    def __init__(self):
        # The fallback loop: Priority Provider -> Key -> Model
        raw_configs = [
            # --- PRIMARY POOL: GEMINI ---
            # Updated to 2.0/2.5-flash to fix the 404 Not Found error
            {"provider": "gemini", "key": os.getenv("GEMINI_API_KEY_1"), "model": "gemini-2.5-flash"},
            {"provider": "gemini", "key": os.getenv("GEMINI_API_KEY_2"), "model": "gemini-2.5-flash"},
            {"provider": "gemini", "key": os.getenv("GEMINI_API_KEY_3"), "model": "gemini-2.5-flash"},
            
            # --- SECONDARY POOL: FALLBACK PROVIDERS ---
            # Updated to a working, stable FREE model on OpenRouter
            {"provider": "openrouter", "key": os.getenv("OPENROUTER_API_KEY_1"), "model": "meta-llama/llama-3.1-8b-instruct:free"},
            
            # 2. HuggingFace 
            {"provider": "huggingface", "key": os.getenv("HF_API_KEY_1"), "model": "meta-llama/Meta-Llama-3-8B-Instruct"},
            
            # 3. Cohere 
            {"provider": "cohere", "key": os.getenv("COHERE_API_KEY_1"), "model": "command-r-08-2024"},
            
            # 4. OpenRouter Backup 
            {"provider": "openrouter", "key": os.getenv("BACKUP_API_KEY"), "model": "nvidia/nemotron-3-nano-30b-a3b:free"}
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
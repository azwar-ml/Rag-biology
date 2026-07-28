import os
from dotenv import load_dotenv

load_dotenv()

class MultiProviderKeyManager:
    def __init__(self):
        # The fallback loop: Provider -> Key -> Heavy Free Model
        # The fallback loop: Provider -> Key -> Heavy Free Model
        raw_configs = [
            # 1. Gemini (Flash-Lite is Google's lowest-latency free model, built specifically for high-speed routing)
            {"provider": "gemini", "key": os.getenv("GEMINI_API_KEY_1"), "model": "gemini-3.1-flash-lite"},
            
            # 2. OpenRouter (Llama 3.2 3B is blisteringly fast for lightweight extraction and classification)
            {"provider": "openrouter", "key": os.getenv("OPENROUTER_API_KEY_1"), "model": "meta-llama/llama-3.2-3b-instruct:free"},
            
            # 3. HuggingFace (Llama 3 8B remains the most reliably cached, fastest-to-respond model on their Serverless API)
            {"provider": "huggingface", "key": os.getenv("HF_API_KEY_1"), "model": "meta-llama/Meta-Llama-3-8B-Instruct"},
            
            # 4. Cohere (Standard Command R 08-2024 delivers 50% higher throughput and 20% lower latency than previous versions)
            {"provider": "cohere", "key": os.getenv("COHERE_API_KEY_1"), "model": "command-r-08-2024"},
            
            # 5. OpenRouter Backup (Nemotron Nano 30B is a small Mixture-of-Experts model designed for fast inference)
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
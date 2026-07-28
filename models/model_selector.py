from pipeline.prompts.templates import QA_PROMPT, MCQ_PROMPT, REASONING_PROMPT, STRICT_EXTRACTION_PROMPT

class ModelSelector:
    @staticmethod
    def analyze_task(query: str) -> dict:
        query_lower = query.lower()
        
        # Updated to the ultra-fast, free models from your raw_configs
        flash_fallbacks = [
            "meta-llama/llama-3.2-3b-instruct:free", 
            "meta-llama/Meta-Llama-3-8B-Instruct",
            "nvidia/nemotron-3-nano-30b-a3b:free"
        ]
        
        # Updated to the heavier, higher-throughput model for complex reasoning
        pro_fallbacks = [
            "command-r-08-2024"
        ]

        if any(word in query_lower for word in ["extract", "exact", "fetch", "from book", "reference", "page number", "cite", "define", "what is", "explain", "describe", "detail"]):
            return {
                "task_type": "Strict Extraction",
                "preferred_model": "gemini-3.1-flash-lite", # Fastest primary model
                "fallback_models": flash_fallbacks,
                "system_prompt": STRICT_EXTRACTION_PROMPT, 
                "temperature": 0.0 
            }
            
        elif any(word in query_lower for word in ["mcq", "multiple choice", "quiz"]):
            return {
                "task_type": "MCQ Generation",
                "preferred_model": "gemini-3.1-flash-lite", 
                "fallback_models": flash_fallbacks,
                "system_prompt": MCQ_PROMPT,
                "temperature": 0.3 
            }
            
        elif any(word in query_lower for word in ["explain why", "how does", "compare", "difference", "mechanism"]):
            return {
                "task_type": "Reasoning",
                "preferred_model": "gemini-1.5-pro", # Kept your original Pro model for reasoning
                "fallback_models": pro_fallbacks,
                "system_prompt": REASONING_PROMPT,
                "temperature": 0.7 
            }
            
        else:
            return {
                "task_type": "Question Answering",
                "preferred_model": "gemini-3.1-flash-lite",
                "fallback_models": flash_fallbacks,
                "system_prompt": QA_PROMPT, # Fixed: Now correctly uses QA_PROMPT
                "temperature": 0.0 
            }

model_selector = ModelSelector()
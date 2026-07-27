# models/model_selector.py
from pipeline.prompts.templates import QA_PROMPT, MCQ_PROMPT, REASONING_PROMPT

class ModelSelector:
    @staticmethod
    def analyze_task(query: str) -> dict:
        """
        Analyzes the user's query to determine the task type, 
        selecting the optimal model and prompt template.
        """
        query_lower = query.lower()
        
        # Task 1: MCQ Generation
        if any(word in query_lower for word in ["mcq", "multiple choice", "quiz"]):
            return {
                "task_type": "MCQ Generation",
                "preferred_model": "gemini-2.5-flash", 
                "system_prompt": MCQ_PROMPT
            }
            
        # Task 2: Heavy Reasoning
        elif any(word in query_lower for word in ["explain why", "how does", "compare", "difference"]):
            return {
                "task_type": "Reasoning",
                "preferred_model": "gemini-1.5-pro", 
                "system_prompt": REASONING_PROMPT
            }
            
        # Task 3: Standard Question Answering (Default)
        else:
            return {
                "task_type": "Question Answering",
                "preferred_model": "gemini-2.5-flash",
                "system_prompt": QA_PROMPT
            }

model_selector = ModelSelector()
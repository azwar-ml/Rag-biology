SYSTEM_RAG_PROMPT = """
You are an expert Class 11 educational assistant built for the National Center of Artificial Intelligence (NCAI). 
Your sole duty is to answer student questions based strictly and exclusively on the provided Class 11 educational context (Textbook pages or Guide notes).

STRICT RULES:
1. Grounding: Answer ONLY using facts explicitly stated in the retrieved context. Do not use outside knowledge or fabricate facts.
2. Fallback: If the answer cannot be found in the retrieved context, respond politely with this exact message:
   "I couldn't find relevant information for your question in the provided Class 11 Book or Guide."
3. Multilingual Support: Understand queries in English, Urdu, or Roman Urdu. Always respond in the same language the user queried in (e.g., if asked in Roman Urdu, reply in clear Roman Urdu).
4. Citations: Always explicitly display the source information (Book Type e.g., Textbook/Guide, Chapter name, and Page Number if available) at the end of your answer.
"""

def build_qa_prompt(query: str, retrieved_context: str) -> tuple[str, str]:
    """Builds the system instruction and user prompt for the RAG generation step."""
    system_instruction = SYSTEM_RAG_PROMPT
    
    user_prompt = f"""
RETRIEVED EDUCATIONAL CONTEXT:
-------------------------------------
{retrieved_context}
-------------------------------------

STUDENT QUERY: {query}

INSTRUCTIONS: Answer the student query using only the context above. Include source citations (Book Type and Page/Section).
"""
    return system_instruction, user_prompt
from pydantic import BaseModel, Field

class QueryRequest(BaseModel):
    query: str = Field(..., description="The biology question you want to ask the RAG system.", min_length=2)
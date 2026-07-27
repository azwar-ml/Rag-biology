from fastapi import APIRouter, HTTPException
from api.request_models import QueryRequest
from api.response_models import QueryResponse
from utils.logger import get_logger
from pipeline.retrieval.retriever import rag_pipeline

logger = get_logger(__name__)
router = APIRouter()

@router.post("/ask", response_model=QueryResponse, tags=["RAG Interface"])
def ask_question(request: QueryRequest):
    logger.info(f"Received query: {request.query}")
    try:
        result = rag_pipeline.answer_query(request.query)
        logger.info("Successfully generated response.")
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during RAG generation.")
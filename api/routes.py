import os
import base64
import mimetypes
import re
from fastapi import APIRouter, HTTPException

from api.request_models import QueryRequest
from api.response_models import QueryResponse
from utils.logger import get_logger
from pipeline.retrieval.retriever import rag_pipeline
from pipeline.retrieval.image_retriever import ImageRetriever

logger = get_logger(__name__)
router = APIRouter()
img_retriever = ImageRetriever()

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def get_data_uri(image_path: str, base64_data: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"
    return f"data:{mime_type};base64,{base64_data}"

def validate_image_match(query: str, caption: str) -> bool:
    """
    Validates if the retrieved image caption actually aligns with the user's query.
    """
    query_lower = query.lower()
    caption_lower = caption.lower()

    # 1. Check for specific figure requests (e.g., "figure 2.1")
    # Matches "figure 1", "fig 2.1", "figure 3-2", etc.
    fig_pattern = r'fig(?:ure)?\s*[-_]?\s*(\d+(?:[\.\-]\d+)?)'
    query_figures = re.findall(fig_pattern, query_lower)
    
    if query_figures:
        # If user asked for a specific figure number, it MUST be in the caption
        return any(q_fig in caption_lower for q_fig in query_figures)

    # 2. Fallback to keyword overlap for descriptive queries (e.g., "electron microscope")
    # Remove common filler words that might cause false positives
    stop_words = {"picture", "of", "show", "me", "a", "the", "image", "give", "can", "you", "is", "what", "an", "and"}
    
    query_words = set(re.findall(r'\b[a-z]{3,}\b', query_lower)) - stop_words
    caption_words = set(re.findall(r'\b[a-z]{3,}\b', caption_lower)) - stop_words

    # If there is at least one meaningful keyword overlap, allow it
    if query_words.intersection(caption_words):
        return True

    # If neither condition is met, the image is likely a hallucination/bad retrieval
    return False

@router.post("/ask", response_model=QueryResponse, tags=["RAG Interface"])
def ask_question(request: QueryRequest):
    logger.info(f"Received query: {request.query}")
    try:
        # --- STEP 1: IMAGE RETRIEVAL CHECK ---
        image_result = img_retriever.retrieve_image(request.query)

        if image_result.get("status") == "success" and image_result.get("data"):
            fig_data = image_result["data"][0]
            caption = fig_data.get('caption', '')
            
            # APPLY VALIDATION HERE
            is_valid = validate_image_match(request.query, caption)
            
            if is_valid:
                img_path = fig_data.get('image') or fig_data.get('image_path') or fig_data.get('file_path')

                if img_path:
                    # Temporary fix for your path naming
                    img_path = img_path.replace("figure1_output", "figure1_output - Copy")
                    
                    if os.path.exists(img_path):
                        base64_img = encode_image_to_base64(img_path)
                        data_uri = get_data_uri(img_path, base64_img)
                        
                        display_caption = caption if caption else "Requested Figure"
                        markdown_answer = f"Here is the figure you requested:\n\n**{display_caption}**\n\n![{display_caption}]({data_uri})"
                        
                        logger.info(f"Successfully returned valid image response for: {display_caption}")
                        return QueryResponse(
                            answer=markdown_answer,
                            sources=[f"Image Match: {img_path}"]
                        )
                    else:
                        logger.warning(f"Image valid but missing on disk: {img_path}")
            else:
                logger.warning(f"Image rejected. Query '{request.query}' did not match retrieved caption: '{caption}'")

        # --- STEP 2: FALLBACK TO TEXT RAG ---
        # If image was not found, OR if it failed validation, generate text.
        logger.info("Generating text fallback response...")
        result = rag_pipeline.answer_query(request.query)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result.get("sources", [])
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during RAG generation.")
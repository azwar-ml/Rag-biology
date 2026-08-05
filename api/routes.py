import os
import base64
import mimetypes
import re
import asyncio
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
    query_lower = query.lower()
    caption_lower = caption.lower()

    fig_pattern = r'(?:fig|figure|image|img)\s*[-_]?\s*(\d+(?:[\.\-]\d+)?)'
    query_figures = re.findall(fig_pattern, query_lower)
    
    if query_figures:
        caption_figures = re.findall(r'(?:fig|figure)\s*[-_]?\s*(\d+(?:[\.\-]\d+)?)', caption_lower)
        
        for q_fig in query_figures:
            normalized_q = q_fig.replace('-', '.')
            match_found = any(normalized_q == c_fig.replace('-', '.') for c_fig in caption_figures)
            if not match_found:
                return False 
        return True

    stop_words = {"picture", "of", "show", "me", "a", "the", "image", "give", "can", "you", "is", "what", "an", "and", "figure", "fig"}
    
    query_words = set(re.findall(r'\b[a-z]{3,}\b', query_lower)) - stop_words
    caption_words = set(re.findall(r'\b[a-z]{3,}\b', caption_lower)) - stop_words

    if query_words.intersection(caption_words):
        return True

    return False


@router.post("/ask", response_model=QueryResponse, tags=["RAG Interface"])
async def ask_question(request: QueryRequest):
    logger.info(f"Received query: {request.query}")
    try:
        image_markdown = ""
        image_sources = []

        # Prepare text-only query by removing explicit image requests
        text_query = re.sub(r'(?i)\b(?:and\s+)?(?:show\s+(?:me\s+)?)?(?:figure|fig|image)\s*[-_]?\s*\d+(?:[\.]\d+)?\b', '', request.query).strip()

        # Determine if the user specifically requested an image/figure
        image_requested = bool(re.search(r'(?i)(?:figure|fig|image|img|diagram)\s*[-_]?\s*\d+(?:[\.]\d+)?', request.query))

        # Route guide queries strictly to Guide database
        guide_keywords = ["guide", "mcq", "mcqs", "practice", "practice question", "practice questions", "exercise"]
        force_book_type = None
        rq_lower = request.query.lower()
        if any(k in rq_lower for k in guide_keywords):
            force_book_type = "Guide"

        # Run image retrieval and text RAG concurrently when both are relevant
        tasks = []
        if image_requested:
            tasks.append(asyncio.to_thread(img_retriever.retrieve_image, request.query))

        # Only run text pipeline if there's remaining text to search
        text_task = None
        if text_query:
            # Clean conversational filler here as well for the RAG call
            filler_patterns = [
                r'(?i)\b(?:explain the process of|explain in detail|step by step|detailed notes on|what is the definition of|what is|can you explain|tell me about)\b',
                r'(?i)\b(?:please|kindly|how do|how does|why do|why does)\b'
            ]
            search_query = text_query
            for pattern in filler_patterns:
                search_query = re.sub(pattern, '', search_query).strip()
            if not search_query:
                search_query = text_query

            text_task = asyncio.to_thread(rag_pipeline.answer_query, search_query, force_book_type)
            tasks.append(text_task)

        # If nothing to do, return empty
        if not tasks:
            return QueryResponse(answer="", sources=[])

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Parse results
        image_result = None
        text_result = None
        for res in results:
            if isinstance(res, Exception):
                logger.error(f"Background task error: {res}")
                continue
            # Heuristics: image retriever returns dict with status key
            if isinstance(res, dict) and res.get("status") in ("success", "not_found", "error"):
                image_result = res
            elif isinstance(res, dict) and "answer" in res:
                text_result = res

        # Process image result if present
        if image_result and image_result.get("status") == "success" and image_result.get("data"):
            fig_data = image_result["data"][0]
            caption = fig_data.get('caption', '')
            is_valid = validate_image_match(request.query, caption)
            if is_valid:
                img_path = fig_data.get('image') or fig_data.get('image_path') or fig_data.get('file_path')
                if img_path:
                    img_path = img_path.replace("figure1_output", "figure1_output - Copy")
                    if os.path.exists(img_path):
                        base64_img = encode_image_to_base64(img_path)
                        data_uri = get_data_uri(img_path, base64_img)
                        display_caption = caption if caption else "Requested Figure"
                        image_markdown = f"**{display_caption}**\n\n![{display_caption}]({data_uri})\n\n"
                        image_sources = [f"Image Match: {img_path}"]
                        logger.info(f"Successfully loaded image for: {display_caption}")
                    else:
                        logger.warning(f"Image valid but missing on disk: {img_path}")
            else:
                logger.warning(f"Image rejected. Query '{request.query}' did not match retrieved caption: '{caption}'")

        # Merge image markdown and text results safely
        if text_result:
            cleaned_text_answer = re.sub(r'!\[.*?\]\(.*?\)', '', text_result.get("answer", ""))
            final_answer = (image_markdown or "") + cleaned_text_answer
            final_sources = (image_sources or []) + text_result.get("sources", [])
        else:
            final_answer = image_markdown
            final_sources = image_sources

        return QueryResponse(answer=final_answer, sources=final_sources)
        
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during RAG generation.")
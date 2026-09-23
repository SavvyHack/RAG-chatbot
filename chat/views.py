import logging
import json
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .rag_pipeline import RAGPipeline
from .llm import generate_response

logger = logging.getLogger(__name__)

# Global instances for single-user local setup
rag_pipeline = RAGPipeline()

def chat_page(request):
    """Render the chat UI."""
    return render(request, "chat/index.html")

@require_POST
def upload_context(request):
    """Process uploaded documents and context text."""
    try:
        files = request.FILES.getlist('documents')
        text_context = request.POST.get('text_context', '')
        
        num_chunks = rag_pipeline.add_context(files=files, text_context=text_context)
        return JsonResponse({"status": "success", "chunks_added": num_chunks})
    except Exception as e:
        logger.error(f"Error uploading context: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@require_POST
def query_rag(request):
    """Generate a reply using local RAG pipeline."""
    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()
        if not query:
            return JsonResponse({"error": "No query provided"}, status=400)
            
        chunks = rag_pipeline.search(query, top_k=3)
        response_text = generate_response(chunks, query)
        
        return JsonResponse({
            "response": response_text,
            "context_used": chunks
        })
    except Exception as e:
        logger.error(f"Error querying RAG: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@require_POST
def clear_context(request):
    """Clear the current knowledge base."""
    try:
        rag_pipeline.reset()
        return JsonResponse({"status": "success"})
    except Exception as e:
        logger.error(f"Error clearing context: {e}")
        return JsonResponse({"error": str(e)}, status=500)
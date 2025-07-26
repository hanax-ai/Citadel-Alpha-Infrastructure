"""
RAG Pipeline API Endpoints
Enterprise retrieval-augmented generation endpoints
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel, Field

from app.core.embeddings.rag_pipeline import rag_pipeline
from app.services.vector_service import qdrant_service
from app.utils.performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models for request/response validation

class DocumentIngestRequest(BaseModel):
    """Document ingestion request"""
    text: str = Field(..., description="Document text content")
    document_id: Optional[str] = Field(None, description="Document ID (auto-generated if not provided)")
    metadata: Dict[str, Any] = Field(default={}, description="Document metadata")
    document_type: str = Field(default="text", description="Document type")
    source: str = Field(default="api", description="Document source")
    collection_name: Optional[str] = Field(None, description="Target collection")

class RAGQueryRequest(BaseModel):
    """RAG query request"""
    query: str = Field(..., description="User query")
    collection_name: Optional[str] = Field(None, description="Collection to search")
    llm_url: str = Field(default="http://192.168.10.34:8002", description="LLM server URL")
    model: str = Field(default="phi3", description="LLM model")
    max_tokens: int = Field(default=1000, description="Maximum response tokens")
    temperature: float = Field(default=0.7, description="LLM temperature")
    top_k: Optional[int] = Field(5, description="Number of context chunks")
    similarity_threshold: Optional[float] = Field(0.5, description="Similarity threshold")

class ContextRetrievalRequest(BaseModel):
    """Context retrieval request"""
    query: str = Field(..., description="Search query")
    collection_name: Optional[str] = Field(None, description="Collection to search")
    top_k: int = Field(default=5, description="Number of results")
    similarity_threshold: float = Field(default=0.5, description="Similarity threshold")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")

class CollectionCreateRequest(BaseModel):
    """Collection creation request"""
    collection_name: str = Field(..., description="Collection name")
    vector_size: int = Field(default=1024, description="Vector dimension")
    distance_metric: str = Field(default="cosine", description="Distance metric")
    optimize_for_performance: bool = Field(default=True, description="Enable optimizations")

# Health and status endpoints

@router.get("/rag/health")
async def rag_health_check():
    """Check RAG pipeline health"""
    try:
        # Check Qdrant connectivity
        qdrant_health = await qdrant_service.health_check()
        
        # Test embedding generation
        try:
            test_embeddings = await rag_pipeline.generate_embeddings("test")
            embedding_status = "healthy"
        except Exception as e:
            embedding_status = f"unhealthy: {str(e)}"
        
        return {
            "status": "healthy" if qdrant_health["status"] == "healthy" and embedding_status == "healthy" else "degraded",
            "qdrant": qdrant_health,
            "embedding_service": embedding_status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@router.get("/rag/collections")
async def list_collections():
    """List all available collections"""
    try:
        qdrant_health = await qdrant_service.health_check()
        return {
            "status": "success",
            "collections": qdrant_health.get("collections", []),
            "total_collections": qdrant_health.get("total_collections", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to list collections: {e}")
        raise HTTPException(status_code=500, detail=f"Collection listing failed: {e}")

@router.get("/rag/collections/{collection_name}/info")
async def get_collection_info(collection_name: str):
    """Get detailed collection information"""
    try:
        info = await qdrant_service.get_collection_info(collection_name)
        return {
            "status": "success",
            "collection_info": info,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get collection info: {e}")
        raise HTTPException(status_code=404, detail=f"Collection info retrieval failed: {e}")

# Collection management endpoints

@router.post("/rag/collections/create")
async def create_collection(request: CollectionCreateRequest):
    """Create new RAG collection"""
    try:
        from qdrant_client.models import Distance
        
        # Map distance metric string to enum
        distance_map = {
            "cosine": Distance.COSINE,
            "euclidean": Distance.EUCLID,
            "dot": Distance.DOT
        }
        
        distance = distance_map.get(request.distance_metric.lower(), Distance.COSINE)
        
        result = await qdrant_service.create_rag_collection(
            collection_name=request.collection_name,
            vector_size=request.vector_size,
            distance=distance,
            optimize_for_performance=request.optimize_for_performance
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Collection creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Collection creation failed: {e}")

@router.post("/rag/collections/initialize")
async def initialize_default_collections():
    """Initialize standard RAG collections"""
    try:
        result = await qdrant_service.initialize_rag_collections()
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Collection initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Collection initialization failed: {e}")

# Document ingestion endpoints

@router.post("/rag/ingest/document")
async def ingest_document(request: DocumentIngestRequest):
    """Ingest single document into RAG pipeline"""
    try:
        document = {
            "id": request.document_id,
            "text": request.text,
            "metadata": request.metadata,
            "document_type": request.document_type,
            "source": request.source
        }
        
        result = await rag_pipeline.ingest_document(
            document=document,
            collection_name=request.collection_name
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Document ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document ingestion failed: {e}")

@router.post("/rag/ingest/batch")
async def batch_ingest_documents(documents: List[DocumentIngestRequest]):
    """Batch ingest multiple documents"""
    try:
        # Convert requests to document format
        doc_list = []
        for req in documents:
            doc_list.append({
                "id": req.document_id,
                "text": req.text,
                "metadata": req.metadata,
                "document_type": req.document_type,
                "source": req.source
            })
        
        # Use first document's collection or default
        collection_name = documents[0].collection_name if documents else None
        
        result = await rag_pipeline.batch_ingest(
            documents=doc_list,
            collection_name=collection_name
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch ingestion failed: {e}")

@router.post("/rag/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    collection_name: Optional[str] = Form(None),
    document_type: str = Form("file"),
    metadata: Optional[str] = Form(None)
):
    """Ingest document from uploaded file"""
    try:
        # Read file content
        content = await file.read()
        text = content.decode('utf-8')
        
        # Parse metadata if provided
        import json
        parsed_metadata = json.loads(metadata) if metadata else {}
        parsed_metadata.update({
            "filename": file.filename,
            "content_type": file.content_type,
            "file_size": len(content)
        })
        
        document = {
            "text": text,
            "metadata": parsed_metadata,
            "document_type": document_type,
            "source": f"file_upload:{file.filename}"
        }
        
        result = await rag_pipeline.ingest_document(
            document=document,
            collection_name=collection_name
        )
        
        return {
            "status": "success",
            "result": result,
            "file_info": {
                "filename": file.filename,
                "size": len(content),
                "content_type": file.content_type
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"File ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"File ingestion failed: {e}")

# Retrieval endpoints

@router.post("/rag/retrieve")
async def retrieve_context(request: ContextRetrievalRequest):
    """Retrieve relevant context for query"""
    try:
        result = await rag_pipeline.retrieve_context(
            query=request.query,
            collection_name=request.collection_name,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            filters=request.filters
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Context retrieval failed: {e}")

@router.post("/rag/search")
async def vector_search(request: ContextRetrievalRequest):
    """Perform vector similarity search"""
    try:
        # Generate query embedding
        query_embeddings = await rag_pipeline.generate_embeddings(request.query)
        query_vector = query_embeddings[0]
        
        # Perform search
        result = await qdrant_service.similarity_search(
            collection_name=request.collection_name or rag_pipeline.default_collection,
            query_vector=query_vector,
            limit=request.top_k,
            score_threshold=request.similarity_threshold,
            filters=request.filters
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vector search failed: {e}")

# RAG query endpoint

@router.post("/rag/query")
async def rag_query(request: RAGQueryRequest):
    """Complete RAG query with retrieval and generation"""
    try:
        result = await rag_pipeline.rag_query(
            query=request.query,
            llm_url=request.llm_url,
            collection_name=request.collection_name,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

# Embedding utilities

@router.post("/rag/embeddings/generate")
async def generate_embeddings(
    text: str,
    model: Optional[str] = None
):
    """Generate embeddings for text"""
    try:
        embeddings = await rag_pipeline.generate_embeddings(text, model)
        return {
            "status": "success",
            "text": text,
            "model": model or rag_pipeline.embedding_model,
            "embedding": embeddings[0],
            "dimension": len(embeddings[0]),
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {e}")

# Document management

@router.delete("/rag/documents/{collection_name}")
async def delete_documents(
    collection_name: str,
    document_ids: List[str]
):
    """Delete documents from collection"""
    try:
        result = await qdrant_service.delete_documents(
            collection_name=collection_name,
            document_ids=document_ids
        )
        return {
            "status": "success",
            "result": result,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Document deletion failed: {e}")

# Performance monitoring

@router.get("/rag/metrics")
async def get_rag_metrics():
    """Get RAG pipeline performance metrics"""
    try:
        # Basic metrics - could be enhanced with more detailed monitoring
        qdrant_health = await qdrant_service.health_check()
        
        metrics = {
            "qdrant_status": qdrant_health["status"],
            "total_collections": qdrant_health.get("total_collections", 0),
            "collections": qdrant_health.get("collections", []),
            "embedding_model": rag_pipeline.embedding_model,
            "default_collection": rag_pipeline.default_collection,
            "pipeline_config": rag_pipeline.config
        }
        
        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Metrics retrieval failed: {e}")

# Demo and testing endpoints

@router.post("/rag/demo/quick-test")
async def rag_demo_test():
    """Quick RAG pipeline demonstration"""
    try:
        # Test document
        test_doc = {
            "text": """
            Citadel AI Operating System is an enterprise-grade artificial intelligence platform 
            designed for distributed AI workloads. The system features comprehensive orchestration 
            capabilities, vector database integration, and advanced RAG (Retrieval-Augmented Generation) 
            pipelines. The orchestration server coordinates multiple LLM instances and provides 
            intelligent request routing across the cluster.
            """,
            "metadata": {"type": "demo", "category": "documentation"},
            "document_type": "demo",
            "source": "rag_demo"
        }
        
        # Ingest test document
        ingest_result = await rag_pipeline.ingest_document(
            document=test_doc,
            collection_name="rag_demo"
        )
        
        # Test query
        query_result = await rag_pipeline.rag_query(
            query="What is Citadel AI Operating System?",
            llm_url="http://192.168.10.34:8002",
            collection_name="rag_demo",
            model="phi3"
        )
        
        return {
            "status": "success",
            "demo_results": {
                "ingestion": ingest_result,
                "query": query_result
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"RAG demo failed: {e}")
        raise HTTPException(status_code=500, detail=f"RAG demo failed: {e}")

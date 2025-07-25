import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
import httpx

logger = logging.getLogger(__name__)

class VectorService:
    _client: Optional[QdrantClient] = None
    _qdrant_config: Dict[str, Any] = None
    _ollama_url: str = "http://localhost:11434" # Default Ollama API URL
    _api_key: Optional[str] = None # For Qdrant Cloud or secured instances

    @classmethod
    async def initialize(cls, qdrant_config: Dict[str, Any], ollama_url: str, api_key: Optional[str] = None):
        """Initializes the Qdrant client."""
        cls._qdrant_config = qdrant_config
        cls._ollama_url = ollama_url
        cls._api_key = api_key

        host = cls._qdrant_config.get('host')
        port = cls._qdrant_config.get('port', 8000) # REST API Port
        grpc_port = cls._qdrant_config.get('grpc_port', 6334) # gRPC Port
        collection_name = cls._qdrant_config.get('collection_name', 'llm_embeddings')
        timeout = cls._qdrant_config.get('timeout_seconds', 60)

        try:
            # Try gRPC first for performance if possible, fall back to REST
            try:
                cls._client = QdrantClient(
                    host=host,
                    port=grpc_port,
                    prefer_grpc=True,
                    timeout=timeout,
                    api_key=cls._api_key # Pass API key if using secured Qdrant
                )
                # Test gRPC connection
                cls._client.get_collections() 
                logger.info(f"VectorService initialized using gRPC client on {host}:{grpc_port}.")
            except Exception as e_grpc:
                logger.warning(f"gRPC connection failed: {e_grpc}. Falling back to REST client on {host}:{port}.")
                # Use HTTP URL for local Qdrant instances
                cls._client = QdrantClient(
                    url=f"http://{host}:{port}",
                    timeout=timeout,
                    api_key=cls._api_key,
                    https=False,  # Force HTTP for local instances
                    check_compatibility=False  # Skip version compatibility check
                )
                # Test REST connection
                cls._client.get_collections()
                logger.info(f"VectorService initialized using REST client on {host}:{port}.")

            # Ensure the collection exists
            await cls._ensure_collection_exists(collection_name)

        except Exception as e:
            logger.error(f"Failed to initialize VectorService: {e}", exc_info=True)
            cls._client = None
            raise

    @classmethod
    async def _ensure_collection_exists(cls, collection_name: str):
        """Ensures the vector collection exists or creates it."""
        if not cls._client:
            raise RuntimeError("VectorService client not initialized.")

        try:
            # Check if collection exists
            cls._client.get_collection(collection_name=collection_name)
            logger.info(f"Collection '{collection_name}' already exists.")
        except UnexpectedResponse as e:
            if e.status_code == 404: # Collection not found
                logger.info(f"Collection '{collection_name}' not found. Creating new collection...")
                # Define vector size. This is critical.
                # For Ollama embeddings, typically a model like "all-MiniLM-L6-v2" or similar
                # would be used, which commonly produce 384 or 768 dimensional vectors.
                # Assuming a common embedding dimension, adjust if your specific model differs.
                # You'll need to know the dimension of the embeddings produced by the Ollama model
                # you plan to use for RAG. For now, let's use a common default like 768.
                # We should also add this to the config.
                vector_size = cls._qdrant_config.get('vector_size', 768) 

                cls._client.recreate_collection(
                    collection_name=collection_name,
                    vectors_config=models.VectorParams(size=vector_size, distance=models.Distance.COSINE),
                )
                logger.info(f"Collection '{collection_name}' created with vector size {vector_size} and COSINE distance.")
            else:
                raise e # Re-raise other unexpected errors
        except Exception as e:
            logger.error(f"Error ensuring collection '{collection_name}' exists: {e}", exc_info=True)
            raise

    @classmethod
    async def close(cls):
        """Closes the Qdrant client."""
        if cls._client:
            cls._client.close()
            logger.info("VectorService client closed.")

    @classmethod
    async def generate_embedding(cls, text: str, model: str = "nomic-embed-text") -> List[float]:
        """
        Generates embeddings for a given text using Ollama.

        Args:
            text: The text to embed.
            model: The Ollama embedding model to use (e.g., "nomic-embed-text").
        Returns:
            A list of floats representing the embedding.
        Raises:
            httpx.RequestError: If there's a network error connecting to Ollama.
            httpx.HTTPStatusError: If Ollama returns a non-200 status code.
        """
        if not cls._ollama_url:
            raise RuntimeError("Ollama URL not configured for embedding generation.")

        embedding_url = f"{cls._ollama_url}/api/embeddings"
        headers = {"Content-Type": "application/json"}
        payload = {
            "model": model,
            "prompt": text
        }

        try:
            async with httpx.AsyncClient(timeout=cls._qdrant_config.get('ollama_timeout_seconds', 120)) as client:
                response = await client.post(embedding_url, headers=headers, json=payload)
                response.raise_for_status() # Raise an exception for 4xx or 5xx responses
                embedding_data = response.json()
                return embedding_data["embedding"]
        except httpx.RequestError as e:
            logger.error(f"Network error during embedding generation (Ollama): {e}", exc_info=True)
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from Ollama during embedding generation: {e.response.status_code} - {e.response.text}", exc_info=True)
            raise
        except KeyError:
            logger.error("Embedding not found in Ollama response.", exc_info=True)
            raise ValueError("Invalid response from Ollama: 'embedding' key missing.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during embedding generation: {e}", exc_info=True)
            raise


    @classmethod
    async def upsert_vectors(cls, points: List[Dict[str, Any]], collection_name: str = None):
        """
        Upserts (inserts or updates) vectors into a collection.
        'points' should be a list of dicts, each with 'id', 'vector', and 'payload' (optional).
        """
        if not cls._client:
            raise RuntimeError("VectorService client not initialized.")

        if not collection_name:
            collection_name = cls._qdrant_config.get('collection_name', 'llm_embeddings')

        qdrant_points = []
        for p in points:
            qdrant_points.append(models.PointStruct(
                id=p['id'],
                vector=p['vector'],
                payload=p.get('payload', {})
            ))

        try:
            operation_info = await cls._client.upsert(
                collection_name=collection_name,
                wait=True,
                points=qdrant_points,
            )
            logger.info(f"Upserted {len(points)} vectors to '{collection_name}': {operation_info.status.value}")
            return operation_info
        except Exception as e:
            logger.error(f"Error upserting vectors to '{collection_name}': {e}", exc_info=True)
            raise

    @classmethod
    async def search_vectors(
        cls, 
        query_vector: List[float], 
        limit: int = 5, 
        collection_name: str = None, 
        query_filter: Optional[models.Filter] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches for similar vectors in a collection.
        Returns a list of dictionaries with 'id', 'score', and 'payload'.
        """
        if not cls._client:
            raise RuntimeError("VectorService client not initialized.")

        if not collection_name:
            collection_name = cls._qdrant_config.get('collection_name', 'llm_embeddings')

        try:
            search_result = await cls._client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True,
                with_vectors=False # Usually don't need vectors back
            )
            return [
                {"id": hit.id, "score": hit.score, "payload": hit.payload}
                for hit in search_result
            ]
        except Exception as e:
            logger.error(f"Error searching vectors in '{collection_name}': {e}", exc_info=True)
            raise

    @classmethod
    async def health_check(cls) -> bool:
        """Performs a simple health check on the Qdrant connection."""
        if not cls._client:
            logger.warning("VectorService client is not initialized.")
            return False
        try:
            cls._client.get_collections()  # Remove await - this is synchronous
            logger.debug("VectorService health check successful.")
            return True
        except Exception as e:
            logger.error(f"VectorService health check failed: {e}", exc_info=True)
            return False

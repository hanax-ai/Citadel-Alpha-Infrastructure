#!/usr/bin/env python3
"""
AI Model Download Script

Automated download and verification of embedded AI models from Hugging Face Hub.
Implements Task 2.1: AI Model Downloads and Verification.

Author: Citadel AI Team
License: MIT
"""

import os
import sys
import json
import hashlib
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hana_x_vector.utils.logging import get_logger
from hana_x_vector.utils.config import get_config

logger = get_logger(__name__)


@dataclass
class ModelInfo:
    """Model information for download and verification."""
    name: str
    model_id: str
    description: str
    dimension: int
    max_length: int
    expected_size_mb: float
    use_cases: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "model_id": self.model_id,
            "description": self.description,
            "dimension": self.dimension,
            "max_length": self.max_length,
            "expected_size_mb": self.expected_size_mb,
            "use_cases": self.use_cases
        }


class ModelDownloader:
    """
    AI Model Downloader
    
    Downloads and verifies embedded AI models from Hugging Face Hub.
    Implements comprehensive error handling and progress tracking.
    """
    
    # Embedded models configuration (from PRD)
    EMBEDDED_MODELS = {
        "all-MiniLM-L6-v2": ModelInfo(
            name="all-MiniLM-L6-v2",
            model_id="sentence-transformers/all-MiniLM-L6-v2",
            description="General-purpose sentence embeddings",
            dimension=384,
            max_length=256,
            expected_size_mb=90.0,
            use_cases=["general", "similarity", "clustering"]
        ),
        "phi-3-mini": ModelInfo(
            name="phi-3-mini",
            model_id="microsoft/Phi-3-mini-4k-instruct",
            description="Lightweight text embeddings and generation",
            dimension=768,
            max_length=4096,
            expected_size_mb=2400.0,
            use_cases=["text_generation", "embeddings", "qa"]
        ),
        "e5-small": ModelInfo(
            name="e5-small",
            model_id="intfloat/e5-small-v2",
            description="Multilingual embeddings",
            dimension=384,
            max_length=512,
            expected_size_mb=130.0,
            use_cases=["multilingual", "embeddings", "retrieval"]
        ),
        "bge-base": ModelInfo(
            name="bge-base",
            model_id="BAAI/bge-base-en-v1.5",
            description="High-quality English embeddings",
            dimension=768,
            max_length=512,
            expected_size_mb=440.0,
            use_cases=["embeddings", "retrieval", "high_quality"]
        )
    }
    
    def __init__(self, storage_path: str = "/opt/citadel/models/embedded"):
        """Initialize model downloader."""
        self.storage_path = Path(storage_path)
        self.cache_dir = Path(os.getenv("HUGGINGFACE_CACHE_DIR", "/opt/citadel/models/cache"))
        self.manifest_path = self.storage_path / "model_manifest.json"
        self.logger = get_logger(__name__)
        
        # Create directories
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing manifest
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict[str, Any]:
        """Load model manifest from file."""
        try:
            if self.manifest_path.exists():
                with open(self.manifest_path, 'r') as f:
                    return json.load(f)
            return {"models": {}, "last_updated": None}
        except Exception as e:
            self.logger.error(f"Failed to load manifest: {e}")
            return {"models": {}, "last_updated": None}
    
    def _save_manifest(self) -> None:
        """Save model manifest to file."""
        try:
            with open(self.manifest_path, 'w') as f:
                json.dump(self.manifest, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save manifest: {e}")
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file."""
        try:
            hash_sha256 = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""
    
    def _get_directory_size(self, directory: Path) -> float:
        """Get directory size in MB."""
        try:
            total_size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
            return total_size / (1024 * 1024)  # Convert to MB
        except Exception as e:
            self.logger.error(f"Failed to calculate directory size: {e}")
            return 0.0
    
    async def download_model(self, model_name: str, force_download: bool = False) -> bool:
        """Download a specific model."""
        try:
            if model_name not in self.EMBEDDED_MODELS:
                raise ValueError(f"Unknown model: {model_name}")
            
            model_info = self.EMBEDDED_MODELS[model_name]
            model_path = self.storage_path / model_name
            
            # Check if model already exists
            if model_path.exists() and not force_download:
                self.logger.info(f"Model {model_name} already exists, skipping download")
                return True
            
            self.logger.info(f"Downloading model: {model_name}")
            self.logger.info(f"Model ID: {model_info.model_id}")
            self.logger.info(f"Expected size: {model_info.expected_size_mb:.1f} MB")
            
            # Import here to avoid dependency issues during testing
            try:
                from transformers import AutoTokenizer, AutoModel
                from sentence_transformers import SentenceTransformer
            except ImportError as e:
                self.logger.error(f"Required libraries not installed: {e}")
                return False
            
            # Download based on model type
            if model_name == "all-MiniLM-L6-v2" or model_name == "e5-small" or model_name == "bge-base":
                # Sentence transformer models
                model = SentenceTransformer(model_info.model_id, cache_folder=str(self.cache_dir))
                model.save(str(model_path))
            else:
                # Standard transformer models
                tokenizer = AutoTokenizer.from_pretrained(
                    model_info.model_id, 
                    cache_dir=str(self.cache_dir)
                )
                model = AutoModel.from_pretrained(
                    model_info.model_id, 
                    cache_dir=str(self.cache_dir)
                )
                
                # Save to model path
                tokenizer.save_pretrained(str(model_path))
                model.save_pretrained(str(model_path))
            
            # Verify download
            if not model_path.exists():
                raise Exception(f"Model path {model_path} not created")
            
            # Calculate actual size
            actual_size = self._get_directory_size(model_path)
            
            # Update manifest
            self.manifest["models"][model_name] = {
                "model_info": model_info.to_dict(),
                "download_path": str(model_path),
                "actual_size_mb": actual_size,
                "download_timestamp": asyncio.get_event_loop().time(),
                "verified": False
            }
            
            self.logger.info(f"Model {model_name} downloaded successfully")
            self.logger.info(f"Actual size: {actual_size:.1f} MB")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download model {model_name}: {e}")
            return False
    
    async def verify_model(self, model_name: str) -> bool:
        """Verify a downloaded model."""
        try:
            if model_name not in self.manifest["models"]:
                self.logger.error(f"Model {model_name} not found in manifest")
                return False
            
            model_info = self.EMBEDDED_MODELS[model_name]
            model_path = Path(self.manifest["models"][model_name]["download_path"])
            
            if not model_path.exists():
                self.logger.error(f"Model path {model_path} does not exist")
                return False
            
            self.logger.info(f"Verifying model: {model_name}")
            
            # Import here to avoid dependency issues during testing
            try:
                from transformers import AutoTokenizer, AutoModel
                from sentence_transformers import SentenceTransformer
                import torch
            except ImportError as e:
                self.logger.error(f"Required libraries not installed: {e}")
                return False
            
            # Load and test model
            try:
                if model_name == "all-MiniLM-L6-v2" or model_name == "e5-small" or model_name == "bge-base":
                    # Sentence transformer models
                    model = SentenceTransformer(str(model_path))
                    
                    # Test embedding generation
                    test_text = "This is a test sentence for model verification."
                    embeddings = model.encode([test_text])
                    
                    # Verify embedding dimensions
                    if embeddings.shape[1] != model_info.dimension:
                        raise Exception(f"Dimension mismatch: expected {model_info.dimension}, got {embeddings.shape[1]}")
                    
                else:
                    # Standard transformer models
                    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
                    model = AutoModel.from_pretrained(str(model_path))
                    
                    # Test tokenization and model forward pass
                    test_text = "This is a test sentence for model verification."
                    inputs = tokenizer(test_text, return_tensors="pt", max_length=512, truncation=True)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                    
                    # Verify output shape
                    if outputs.last_hidden_state.shape[-1] != model_info.dimension:
                        raise Exception(f"Dimension mismatch: expected {model_info.dimension}, got {outputs.last_hidden_state.shape[-1]}")
                
                # Update manifest
                self.manifest["models"][model_name]["verified"] = True
                self.manifest["models"][model_name]["verification_timestamp"] = asyncio.get_event_loop().time()
                
                self.logger.info(f"Model {model_name} verified successfully")
                return True
                
            except Exception as e:
                self.logger.error(f"Model verification failed: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to verify model {model_name}: {e}")
            return False
    
    async def download_all_models(self, force_download: bool = False) -> Dict[str, bool]:
        """Download all embedded models."""
        results = {}
        
        self.logger.info("Starting download of all embedded models")
        
        for model_name in self.EMBEDDED_MODELS.keys():
            self.logger.info(f"Processing model: {model_name}")
            results[model_name] = await self.download_model(model_name, force_download)
        
        # Save manifest
        self.manifest["last_updated"] = asyncio.get_event_loop().time()
        self._save_manifest()
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        self.logger.info(f"Download complete: {successful}/{total} models successful")
        
        return results
    
    async def verify_all_models(self) -> Dict[str, bool]:
        """Verify all downloaded models."""
        results = {}
        
        self.logger.info("Starting verification of all models")
        
        for model_name in self.manifest["models"].keys():
            self.logger.info(f"Verifying model: {model_name}")
            results[model_name] = await self.verify_model(model_name)
        
        # Save manifest
        self._save_manifest()
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        self.logger.info(f"Verification complete: {successful}/{total} models verified")
        
        return results
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models."""
        status = {
            "total_models": len(self.EMBEDDED_MODELS),
            "downloaded_models": len(self.manifest["models"]),
            "verified_models": sum(1 for model in self.manifest["models"].values() if model.get("verified", False)),
            "models": {}
        }
        
        for model_name, model_info in self.EMBEDDED_MODELS.items():
            model_status = {
                "expected_size_mb": model_info.expected_size_mb,
                "downloaded": model_name in self.manifest["models"],
                "verified": False,
                "actual_size_mb": 0.0
            }
            
            if model_name in self.manifest["models"]:
                manifest_entry = self.manifest["models"][model_name]
                model_status["verified"] = manifest_entry.get("verified", False)
                model_status["actual_size_mb"] = manifest_entry.get("actual_size_mb", 0.0)
            
            status["models"][model_name] = model_status
        
        return status
    
    def cleanup_cache(self) -> None:
        """Clean up Hugging Face cache."""
        try:
            import shutil
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                self.logger.info("Cache cleaned up successfully")
        except Exception as e:
            self.logger.error(f"Failed to cleanup cache: {e}")


async def main():
    """Main function for script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download and verify AI models")
    parser.add_argument("--model", help="Specific model to download")
    parser.add_argument("--force", action="store_true", help="Force re-download")
    parser.add_argument("--verify", action="store_true", help="Verify models only")
    parser.add_argument("--status", action="store_true", help="Show model status")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup cache")
    parser.add_argument("--storage", default="/opt/citadel/models/embedded", help="Storage path")
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = ModelDownloader(args.storage)
    
    try:
        if args.status:
            # Show status
            status = downloader.get_model_status()
            print(json.dumps(status, indent=2))
            
        elif args.cleanup:
            # Cleanup cache
            downloader.cleanup_cache()
            
        elif args.verify:
            # Verify models
            results = await downloader.verify_all_models()
            print(f"Verification results: {results}")
            
        elif args.model:
            # Download specific model
            success = await downloader.download_model(args.model, args.force)
            if success:
                print(f"Model {args.model} downloaded successfully")
                # Verify after download
                verified = await downloader.verify_model(args.model)
                print(f"Model {args.model} verification: {'PASSED' if verified else 'FAILED'}")
            else:
                print(f"Failed to download model {args.model}")
                sys.exit(1)
                
        else:
            # Download all models
            results = await downloader.download_all_models(args.force)
            print(f"Download results: {results}")
            
            # Verify all models
            verification_results = await downloader.verify_all_models()
            print(f"Verification results: {verification_results}")
            
            # Show final status
            status = downloader.get_model_status()
            print(f"\nFinal status: {status['verified_models']}/{status['total_models']} models ready")
            
    except KeyboardInterrupt:
        print("\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

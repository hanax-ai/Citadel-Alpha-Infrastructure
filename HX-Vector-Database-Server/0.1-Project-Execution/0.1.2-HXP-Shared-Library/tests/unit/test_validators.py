"""
Unit Tests for Validation Utilities
===================================

Comprehensive unit tests for the hana_x_vector.utils.validators module.
Tests all validation functions and classes for vector data, collections, search queries, and API requests.
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Import the validators module
from hana_x_vector.utils.validators import (
    VectorValidator,
    CollectionValidator,
    SearchValidator,
    BatchValidator,
    APIValidator,
    validate_vector_data,
    validate_collection_data,
    validate_search_data,
    validate_batch_data,
    validate_api_request,
    validate_api_key,
    validate_request_data
)
from hana_x_vector.utils.exceptions import (
    VectorValidationError,
    CollectionValidationError,
    SearchValidationError,
    BatchValidationError,
    APIValidationError
)


class TestVectorValidator:
    """Test cases for VectorValidator class."""
    
    def test_validate_vector_data_valid_input(self, sample_vector_data):
        """Test validation with valid vector data."""
        validator = VectorValidator()
        result = validator.validate(sample_vector_data)
        assert result is True
    
    def test_validate_vector_data_invalid_vector_type(self):
        """Test validation with invalid vector type."""
        validator = VectorValidator()
        invalid_data = {
            "id": "test-vector-1",
            "vector": "not-a-list",  # Invalid type
            "payload": {"category": "test"}
        }
        
        with pytest.raises(VectorValidationError):
            validator.validate(invalid_data)
    
    def test_validate_vector_data_empty_vector(self):
        """Test validation with empty vector."""
        validator = VectorValidator()
        invalid_data = {
            "id": "test-vector-1",
            "vector": [],  # Empty vector
            "payload": {"category": "test"}
        }
        
        with pytest.raises(VectorValidationError):
            validator.validate(invalid_data)
    
    def test_validate_vector_data_missing_id(self):
        """Test validation with missing ID."""
        validator = VectorValidator()
        invalid_data = {
            "vector": [0.1, 0.2, 0.3],
            "payload": {"category": "test"}
            # Missing "id" field
        }
        
        with pytest.raises(VectorValidationError):
            validator.validate(invalid_data)
    
    def test_validate_vector_dimensions(self):
        """Test vector dimension validation."""
        validator = VectorValidator()
        
        # Valid dimensions
        valid_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        assert validator.validate_dimensions(valid_vector, expected_dimension=5) is True
        
        # Invalid dimensions
        invalid_vector = [0.1, 0.2, 0.3]
        with pytest.raises(VectorValidationError):
            validator.validate_dimensions(invalid_vector, expected_dimension=5)
    
    def test_validate_vector_values(self):
        """Test vector value validation."""
        validator = VectorValidator()
        
        # Valid values
        valid_vector = [0.1, 0.2, 0.3, 0.4, 0.5]
        assert validator.validate_values(valid_vector) is True
        
        # Invalid values (NaN)
        invalid_vector = [0.1, float('nan'), 0.3]
        with pytest.raises(VectorValidationError):
            validator.validate_values(invalid_vector)
        
        # Invalid values (infinity)
        invalid_vector = [0.1, float('inf'), 0.3]
        with pytest.raises(VectorValidationError):
            validator.validate_values(invalid_vector)


class TestCollectionValidator:
    """Test cases for CollectionValidator class."""
    
    def test_validate_collection_data_valid_input(self, sample_collection_config):
        """Test validation with valid collection data."""
        validator = CollectionValidator()
        result = validator.validate(sample_collection_config)
        assert result is True
    
    def test_validate_collection_name_valid(self):
        """Test collection name validation with valid names."""
        validator = CollectionValidator()
        
        valid_names = ["test_collection", "collection-1", "my_vectors"]
        for name in valid_names:
            assert validator.validate_name(name) == name
    
    def test_validate_collection_name_invalid(self):
        """Test collection name validation with invalid names."""
        validator = CollectionValidator()
        
        invalid_names = ["", "collection with spaces", "collection@special", "a" * 256]
        for name in invalid_names:
            with pytest.raises(CollectionValidationError):
                validator.validate_name(name)
    
    def test_validate_collection_config_missing_vectors(self):
        """Test validation with missing vectors configuration."""
        validator = CollectionValidator()
        invalid_config = {
            "name": "test_collection"
            # Missing "vectors" configuration
        }
        
        with pytest.raises(CollectionValidationError):
            validator.validate(invalid_config)


class TestSearchValidator:
    """Test cases for SearchValidator class."""
    
    def test_validate_search_query_valid_input(self, sample_search_query):
        """Test validation with valid search query."""
        validator = SearchValidator()
        result = validator.validate(sample_search_query)
        assert result is True
    
    def test_validate_search_query_missing_vector(self):
        """Test validation with missing vector in search query."""
        validator = SearchValidator()
        invalid_query = {
            "collection": "test_collection",
            "limit": 10
            # Missing "vector" field
        }
        
        with pytest.raises(SearchValidationError):
            validator.validate(invalid_query)
    
    def test_validate_search_limit(self):
        """Test search limit validation."""
        validator = SearchValidator()
        
        # Valid limits
        valid_limits = [1, 10, 100, 1000]
        for limit in valid_limits:
            assert validator.validate_limit(limit) == limit
        
        # Invalid limits
        invalid_limits = [0, -1, 10001]
        for limit in invalid_limits:
            with pytest.raises(SearchValidationError):
                validator.validate_limit(limit)
    
    def test_validate_search_filter(self):
        """Test search filter validation."""
        validator = SearchValidator()
        
        # Valid filters
        valid_filters = [
            {"category": "test"},
            {"category": {"$eq": "test"}},
            {"score": {"$gte": 0.5}},
            {}  # Empty filter
        ]
        for filter_dict in valid_filters:
            assert validator.validate_filter(filter_dict) == filter_dict
        
        # Invalid filter (not a dict)
        with pytest.raises(SearchValidationError):
            validator.validate_filter("invalid_filter")


class TestBatchValidator:
    """Test cases for BatchValidator class."""
    
    def test_validate_batch_data_valid_input(self, sample_vectors_batch):
        """Test validation with valid batch data."""
        validator = BatchValidator()
        batch_data = {"vectors": sample_vectors_batch}
        result = validator.validate(batch_data)
        assert result is True
    
    def test_validate_batch_size_limits(self):
        """Test batch size validation."""
        validator = BatchValidator()
        
        # Valid batch size
        valid_batch = {"vectors": [{"id": f"vec-{i}", "vector": [0.1, 0.2]} for i in range(100)]}
        assert validator.validate(valid_batch) is True
        
        # Invalid batch size (too large)
        invalid_batch = {"vectors": [{"id": f"vec-{i}", "vector": [0.1, 0.2]} for i in range(10001)]}
        with pytest.raises(BatchValidationError):
            validator.validate(invalid_batch)
    
    def test_validate_batch_empty(self):
        """Test validation with empty batch."""
        validator = BatchValidator()
        empty_batch = {"vectors": []}
        
        with pytest.raises(BatchValidationError):
            validator.validate(empty_batch)


class TestAPIValidator:
    """Test cases for APIValidator class."""
    
    def test_validate_api_request_valid_input(self, sample_api_request):
        """Test validation with valid API request."""
        validator = APIValidator()
        result = validator.validate(sample_api_request["body"])
        assert result is True
    
    def test_validate_api_request_missing_required_fields(self):
        """Test validation with missing required fields."""
        validator = APIValidator()
        invalid_request = {
            "vector": [0.1, 0.2, 0.3]
            # Missing "collection" field
        }
        
        with pytest.raises(APIValidationError):
            validator.validate(invalid_request)


class TestConvenienceFunctions:
    """Test cases for convenience validation functions."""
    
    def test_validate_vector_data_function(self, sample_vector_data):
        """Test validate_vector_data convenience function."""
        result = validate_vector_data(sample_vector_data)
        assert result is True
    
    def test_validate_collection_data_function(self, sample_collection_config):
        """Test validate_collection_data convenience function."""
        result = validate_collection_data(sample_collection_config)
        assert result is True
    
    def test_validate_search_data_function(self, sample_search_query):
        """Test validate_search_data convenience function."""
        result = validate_search_data(sample_search_query)
        assert result is True
    
    def test_validate_batch_data_function(self, sample_vectors_batch):
        """Test validate_batch_data convenience function."""
        batch_data = {"vectors": sample_vectors_batch}
        result = validate_batch_data(batch_data)
        assert result is True
    
    def test_validate_api_request_function(self, sample_api_request):
        """Test validate_api_request convenience function."""
        result = validate_api_request(sample_api_request["body"])
        assert result is True


class TestAPIKeyValidation:
    """Test cases for API key validation."""
    
    def test_validate_api_key_valid_keys(self):
        """Test API key validation with valid keys."""
        valid_keys = [
            "test-api-key-123456789",
            "abcdef1234567890abcdef1234567890",
            "my_api_key_with_underscores",
            "api-key-with-hyphens-123"
        ]
        
        for key in valid_keys:
            assert validate_api_key(key) is True
    
    def test_validate_api_key_invalid_keys(self):
        """Test API key validation with invalid keys."""
        invalid_keys = [
            "",  # Empty string
            "short",  # Too short
            "a" * 129,  # Too long
            "key with spaces",  # Contains spaces
            "key@with#special!chars",  # Contains special characters
            None,  # None value
            123  # Non-string type
        ]
        
        for key in invalid_keys:
            assert validate_api_key(key) is False
    
    def test_validate_api_key_edge_cases(self):
        """Test API key validation edge cases."""
        # Minimum length (16 characters)
        min_key = "a" * 16
        assert validate_api_key(min_key) is True
        
        # Maximum length (128 characters)
        max_key = "a" * 128
        assert validate_api_key(max_key) is True
        
        # Just below minimum
        too_short = "a" * 15
        assert validate_api_key(too_short) is False
        
        # Just above maximum
        too_long = "a" * 129
        assert validate_api_key(too_long) is False


class TestRequestDataValidation:
    """Test cases for request data validation."""
    
    def test_validate_request_data_vector_type(self, sample_vector_data):
        """Test request data validation with vector type."""
        request_data = {
            "type": "vector",
            **sample_vector_data
        }
        
        result = validate_request_data(request_data)
        assert result is True
    
    def test_validate_request_data_collection_type(self):
        """Test request data validation with collection type."""
        request_data = {
            "type": "collection",
            "name": "test_collection",
            "vectors": {"size": 5, "distance": "Cosine"}
        }
        
        result = validate_request_data(request_data)
        assert result is True
    
    def test_validate_request_data_search_type(self, sample_search_query):
        """Test request data validation with search type."""
        request_data = {
            "type": "search",
            **sample_search_query
        }
        
        result = validate_request_data(request_data)
        assert result is True
    
    def test_validate_request_data_untyped_request(self):
        """Test request data validation with untyped request."""
        request_data = {
            "some_field": "some_value",
            "another_field": 123
        }
        
        # Should pass for generic requests
        result = validate_request_data(request_data)
        assert result is True
    
    def test_validate_request_data_invalid_type(self):
        """Test request data validation with invalid data type."""
        # Non-dict input
        result = validate_request_data("not_a_dict")
        assert result is False
        
        # None input
        result = validate_request_data(None)
        assert result is False


@pytest.mark.performance
class TestValidationPerformance:
    """Performance tests for validation functions."""
    
    def test_vector_validation_performance(self, benchmark, performance_test_vectors):
        """Benchmark vector validation performance."""
        validator = VectorValidator()
        
        def validate_vectors():
            for vector in performance_test_vectors[:100]:  # Test with 100 vectors
                vector_data = {
                    "id": f"perf-test-{hash(str(vector))}",
                    "vector": vector,
                    "payload": {"test": True}
                }
                validator.validate(vector_data)
        
        result = benchmark(validate_vectors)
        # Performance should be reasonable for 100 vectors
        assert result is None  # benchmark returns None on success
    
    def test_api_key_validation_performance(self, benchmark):
        """Benchmark API key validation performance."""
        test_keys = [f"test-api-key-{i:010d}" for i in range(1000)]
        
        def validate_keys():
            for key in test_keys:
                validate_api_key(key)
        
        result = benchmark(validate_keys)
        assert result is None


# Integration with pytest markers
pytestmark = pytest.mark.unit

#!/usr/bin/env python3
"""
Performance Benchmarking Tool

Comprehensive performance benchmarking for vector database operations.
Implements Task 4.2: Performance Benchmarking.

Author: Citadel AI Team
License: MIT
"""

import asyncio
import time
import statistics
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor
import numpy as np

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hana_x_vector.utils.logging import get_logger
from hana_x_vector.utils.metrics import MetricsCollector
from hana_x_vector.models.vector_models import Vector, VectorSearchRequest

logger = get_logger(__name__)


@dataclass
class BenchmarkResult:
    """Benchmark result data structure."""
    operation: str
    total_operations: int
    duration_seconds: float
    operations_per_second: float
    avg_latency_ms: float
    min_latency_ms: float
    max_latency_ms: float
    p50_latency_ms: float
    p95_latency_ms: float
    p99_latency_ms: float
    success_rate: float
    error_count: int
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: str


@dataclass
class BenchmarkConfig:
    """Benchmark configuration."""
    operation: str
    num_operations: int
    concurrency: int
    vector_dimension: int
    collection_name: str
    batch_size: int
    warmup_operations: int
    timeout_seconds: float


class PerformanceBenchmark:
    """
    Performance Benchmark Tool
    
    Comprehensive benchmarking for vector database operations.
    Tests performance against PRD requirements (>10,000 ops/sec, <10ms latency).
    """
    
    # PRD Performance Requirements
    TARGET_OPS_PER_SECOND = 10000
    TARGET_LATENCY_MS = 10
    TARGET_EMBEDDING_LATENCY_MS = 100
    
    def __init__(self, mock_mode: bool = True):
        """Initialize performance benchmark."""
        self.logger = get_logger(__name__)
        self.metrics = MetricsCollector()
        self.mock_mode = mock_mode
        self.results: List[BenchmarkResult] = []
        
        # Mock data for testing without actual vector database
        self.mock_vectors = self._generate_mock_vectors()
    
    def _generate_mock_vectors(self, count: int = 10000) -> List[Vector]:
        """Generate mock vectors for testing."""
        vectors = []
        for i in range(count):
            # Generate random embedding
            embedding = np.random.random(384).tolist()
            
            vector = Vector(
                id=f"test_vector_{i}",
                embedding=embedding,
                metadata={"index": i, "type": "test"},
                collection="benchmark_collection"
            )
            vectors.append(vector)
        
        return vectors
    
    def _get_system_metrics(self) -> Tuple[float, float]:
        """Get current system metrics."""
        try:
            import psutil
            memory_mb = psutil.virtual_memory().used / (1024 * 1024)
            cpu_percent = psutil.cpu_percent(interval=0.1)
            return memory_mb, cpu_percent
        except ImportError:
            return 0.0, 0.0
    
    async def _mock_vector_search(self, request: VectorSearchRequest) -> Dict[str, Any]:
        """Mock vector search operation."""
        # Simulate processing time
        await asyncio.sleep(0.001 + np.random.exponential(0.002))  # 1-5ms typical
        
        # Return mock results
        return {
            "vectors": self.mock_vectors[:request.limit],
            "total_count": len(self.mock_vectors),
            "query_time_ms": 2.5,
            "success": True
        }
    
    async def _mock_vector_insert(self, vector: Vector) -> Dict[str, Any]:
        """Mock vector insert operation."""
        # Simulate processing time
        await asyncio.sleep(0.0005 + np.random.exponential(0.001))  # 0.5-2ms typical
        
        return {
            "success": True,
            "vector_id": vector.id,
            "processing_time_ms": 1.2
        }
    
    async def _mock_embedding_generation(self, texts: List[str]) -> Dict[str, Any]:
        """Mock embedding generation."""
        # Simulate processing time based on text length
        processing_time = 0.05 + len(texts) * 0.01  # 50ms base + 10ms per text
        await asyncio.sleep(processing_time)
        
        # Generate mock embeddings
        embeddings = [np.random.random(384).tolist() for _ in texts]
        
        return {
            "embeddings": embeddings,
            "model_name": "all-MiniLM-L6-v2",
            "dimension": 384,
            "processing_time_ms": processing_time * 1000,
            "success": True
        }
    
    async def _benchmark_operation(self, operation_func, operation_name: str, 
                                 config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark a specific operation."""
        self.logger.info(f"Starting benchmark: {operation_name}")
        self.logger.info(f"Operations: {config.num_operations}, Concurrency: {config.concurrency}")
        
        # Warmup
        if config.warmup_operations > 0:
            self.logger.info(f"Warming up with {config.warmup_operations} operations")
            warmup_tasks = []
            for _ in range(config.warmup_operations):
                task = operation_func()
                warmup_tasks.append(task)
            
            await asyncio.gather(*warmup_tasks, return_exceptions=True)
        
        # Benchmark
        latencies = []
        errors = 0
        start_memory, start_cpu = self._get_system_metrics()
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(config.concurrency)
        
        async def timed_operation():
            async with semaphore:
                start_time = time.time()
                try:
                    await operation_func()
                    end_time = time.time()
                    latency_ms = (end_time - start_time) * 1000
                    latencies.append(latency_ms)
                    return True
                except Exception as e:
                    self.logger.debug(f"Operation failed: {e}")
                    return False
        
        # Execute benchmark
        start_time = time.time()
        
        tasks = [timed_operation() for _ in range(config.num_operations)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        end_memory, end_cpu = self._get_system_metrics()
        
        # Count errors
        errors = sum(1 for result in results if not result or isinstance(result, Exception))
        
        # Calculate metrics
        duration_seconds = end_time - start_time
        operations_per_second = config.num_operations / duration_seconds
        success_rate = (config.num_operations - errors) / config.num_operations
        
        # Latency statistics
        if latencies:
            avg_latency = statistics.mean(latencies)
            min_latency = min(latencies)
            max_latency = max(latencies)
            p50_latency = statistics.median(latencies)
            p95_latency = np.percentile(latencies, 95)
            p99_latency = np.percentile(latencies, 99)
        else:
            avg_latency = min_latency = max_latency = p50_latency = p95_latency = p99_latency = 0
        
        # System metrics
        memory_usage = end_memory - start_memory
        cpu_usage = (start_cpu + end_cpu) / 2
        
        result = BenchmarkResult(
            operation=operation_name,
            total_operations=config.num_operations,
            duration_seconds=duration_seconds,
            operations_per_second=operations_per_second,
            avg_latency_ms=avg_latency,
            min_latency_ms=min_latency,
            max_latency_ms=max_latency,
            p50_latency_ms=p50_latency,
            p95_latency_ms=p95_latency,
            p99_latency_ms=p99_latency,
            success_rate=success_rate,
            error_count=errors,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        self.results.append(result)
        
        # Log results
        self.logger.info(f"Benchmark completed: {operation_name}")
        self.logger.info(f"Operations/sec: {operations_per_second:.2f}")
        self.logger.info(f"Avg latency: {avg_latency:.2f}ms")
        self.logger.info(f"P95 latency: {p95_latency:.2f}ms")
        self.logger.info(f"Success rate: {success_rate:.2%}")
        
        return result
    
    async def benchmark_vector_search(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark vector search operations."""
        
        async def search_operation():
            query_vector = np.random.random(config.vector_dimension).tolist()
            request = VectorSearchRequest(
                query_vector=query_vector,
                collection=config.collection_name,
                limit=10,
                include_vectors=True,
                include_metadata=True
            )
            return await self._mock_vector_search(request)
        
        return await self._benchmark_operation(
            search_operation, 
            "vector_search", 
            config
        )
    
    async def benchmark_vector_insert(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark vector insert operations."""
        
        async def insert_operation():
            embedding = np.random.random(config.vector_dimension).tolist()
            vector = Vector(
                id=f"bench_{time.time()}_{np.random.randint(0, 1000000)}",
                embedding=embedding,
                metadata={"benchmark": True},
                collection=config.collection_name
            )
            return await self._mock_vector_insert(vector)
        
        return await self._benchmark_operation(
            insert_operation,
            "vector_insert",
            config
        )
    
    async def benchmark_batch_insert(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark batch vector insert operations."""
        
        async def batch_insert_operation():
            vectors = []
            for i in range(config.batch_size):
                embedding = np.random.random(config.vector_dimension).tolist()
                vector = Vector(
                    id=f"batch_{time.time()}_{i}",
                    embedding=embedding,
                    metadata={"batch": True, "index": i},
                    collection=config.collection_name
                )
                vectors.append(vector)
            
            # Simulate batch processing time
            await asyncio.sleep(0.001 * config.batch_size)
            return {"success": True, "inserted_count": len(vectors)}
        
        return await self._benchmark_operation(
            batch_insert_operation,
            "batch_insert",
            config
        )
    
    async def benchmark_embedding_generation(self, config: BenchmarkConfig) -> BenchmarkResult:
        """Benchmark embedding generation operations."""
        
        test_texts = [
            "This is a test sentence for embedding generation.",
            "Vector databases are essential for AI applications.",
            "Performance benchmarking helps optimize systems.",
            "Embeddings capture semantic meaning of text.",
            "High-dimensional vectors enable similarity search."
        ]
        
        async def embedding_operation():
            # Select random texts for embedding
            selected_texts = np.random.choice(test_texts, size=config.batch_size, replace=True).tolist()
            return await self._mock_embedding_generation(selected_texts)
        
        return await self._benchmark_operation(
            embedding_operation,
            "embedding_generation",
            config
        )
    
    async def run_comprehensive_benchmark(self, base_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run comprehensive benchmark suite."""
        self.logger.info("Starting comprehensive benchmark suite")
        
        # Default configurations
        default_config = {
            "num_operations": 1000,
            "concurrency": 10,
            "vector_dimension": 384,
            "collection_name": "benchmark_collection",
            "batch_size": 32,
            "warmup_operations": 100,
            "timeout_seconds": 300
        }
        
        # Merge with provided config
        config_dict = {**default_config, **base_config}
        
        # Benchmark configurations
        benchmarks = [
            ("vector_search", self.benchmark_vector_search),
            ("vector_insert", self.benchmark_vector_insert),
            ("batch_insert", self.benchmark_batch_insert),
            ("embedding_generation", self.benchmark_embedding_generation)
        ]
        
        # Run benchmarks
        benchmark_results = {}
        
        for benchmark_name, benchmark_func in benchmarks:
            self.logger.info(f"Running {benchmark_name} benchmark")
            
            config = BenchmarkConfig(**config_dict, operation=benchmark_name)
            
            try:
                result = await benchmark_func(config)
                benchmark_results[benchmark_name] = asdict(result)
                
                # Check against PRD requirements
                self._check_performance_requirements(result)
                
            except Exception as e:
                self.logger.error(f"Benchmark {benchmark_name} failed: {e}")
                benchmark_results[benchmark_name] = {"error": str(e)}
        
        # Generate summary
        summary = self._generate_benchmark_summary(benchmark_results)
        
        return {
            "summary": summary,
            "results": benchmark_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": config_dict
        }
    
    def _check_performance_requirements(self, result: BenchmarkResult) -> None:
        """Check benchmark results against PRD requirements."""
        # Check operations per second
        if result.operation in ["vector_search", "vector_insert"]:
            if result.operations_per_second < self.TARGET_OPS_PER_SECOND:
                self.logger.warning(
                    f"{result.operation}: {result.operations_per_second:.2f} ops/sec "
                    f"< target {self.TARGET_OPS_PER_SECOND} ops/sec"
                )
            else:
                self.logger.info(
                    f"{result.operation}: {result.operations_per_second:.2f} ops/sec "
                    f">= target {self.TARGET_OPS_PER_SECOND} ops/sec ✓"
                )
        
        # Check latency
        target_latency = (
            self.TARGET_EMBEDDING_LATENCY_MS 
            if result.operation == "embedding_generation" 
            else self.TARGET_LATENCY_MS
        )
        
        if result.avg_latency_ms > target_latency:
            self.logger.warning(
                f"{result.operation}: {result.avg_latency_ms:.2f}ms "
                f"> target {target_latency}ms"
            )
        else:
            self.logger.info(
                f"{result.operation}: {result.avg_latency_ms:.2f}ms "
                f"<= target {target_latency}ms ✓"
            )
    
    def _generate_benchmark_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate benchmark summary."""
        summary = {
            "total_benchmarks": len(results),
            "successful_benchmarks": sum(1 for r in results.values() if "error" not in r),
            "failed_benchmarks": sum(1 for r in results.values() if "error" in r),
            "performance_analysis": {},
            "recommendations": []
        }
        
        # Performance analysis
        for operation, result in results.items():
            if "error" not in result:
                ops_per_sec = result.get("operations_per_second", 0)
                avg_latency = result.get("avg_latency_ms", 0)
                
                # Check against targets
                target_ops = self.TARGET_OPS_PER_SECOND
                target_latency = (
                    self.TARGET_EMBEDDING_LATENCY_MS 
                    if operation == "embedding_generation" 
                    else self.TARGET_LATENCY_MS
                )
                
                summary["performance_analysis"][operation] = {
                    "ops_per_second": ops_per_sec,
                    "avg_latency_ms": avg_latency,
                    "meets_ops_target": ops_per_sec >= target_ops,
                    "meets_latency_target": avg_latency <= target_latency,
                    "performance_score": min(
                        (ops_per_sec / target_ops) * 0.5 + 
                        (target_latency / max(avg_latency, 0.1)) * 0.5,
                        1.0
                    )
                }
        
        # Generate recommendations
        if summary["performance_analysis"]:
            avg_score = statistics.mean(
                analysis.get("performance_score", 0) 
                for analysis in summary["performance_analysis"].values()
            )
            
            if avg_score < 0.8:
                summary["recommendations"].append("Consider GPU optimization and memory allocation tuning")
            if avg_score < 0.6:
                summary["recommendations"].append("Review vector database configuration and indexing")
            if avg_score < 0.4:
                summary["recommendations"].append("Consider hardware upgrades or architecture changes")
        
        return summary
    
    def save_results(self, filename: str) -> None:
        """Save benchmark results to file."""
        try:
            results_data = {
                "results": [asdict(result) for result in self.results],
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_benchmarks": len(self.results)
            }
            
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            self.logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
    
    def print_results_table(self) -> None:
        """Print results in table format."""
        if not self.results:
            print("No benchmark results available")
            return
        
        # Print header
        print("\n" + "="*120)
        print("PERFORMANCE BENCHMARK RESULTS")
        print("="*120)
        
        # Print table header
        header = f"{'Operation':<20} {'Ops/sec':<10} {'Avg Lat':<10} {'P95 Lat':<10} {'P99 Lat':<10} {'Success':<10} {'Status':<15}"
        print(header)
        print("-" * len(header))
        
        # Print results
        for result in self.results:
            # Determine status
            target_ops = self.TARGET_OPS_PER_SECOND
            target_latency = (
                self.TARGET_EMBEDDING_LATENCY_MS 
                if result.operation == "embedding_generation" 
                else self.TARGET_LATENCY_MS
            )
            
            ops_ok = result.operations_per_second >= target_ops
            latency_ok = result.avg_latency_ms <= target_latency
            
            if ops_ok and latency_ok:
                status = "✓ PASS"
            elif ops_ok or latency_ok:
                status = "⚠ PARTIAL"
            else:
                status = "✗ FAIL"
            
            print(f"{result.operation:<20} "
                  f"{result.operations_per_second:<10.2f} "
                  f"{result.avg_latency_ms:<10.2f} "
                  f"{result.p95_latency_ms:<10.2f} "
                  f"{result.p99_latency_ms:<10.2f} "
                  f"{result.success_rate:<10.2%} "
                  f"{status:<15}")
        
        print("="*120)


async def main():
    """Main function for script execution."""
    parser = argparse.ArgumentParser(description="Performance benchmarking tool")
    parser.add_argument("--operations", type=int, default=1000, help="Number of operations per benchmark")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent operations")
    parser.add_argument("--dimension", type=int, default=384, help="Vector dimension")
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size for batch operations")
    parser.add_argument("--warmup", type=int, default=100, help="Warmup operations")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--benchmark", choices=["search", "insert", "batch", "embedding", "all"], 
                       default="all", help="Specific benchmark to run")
    
    args = parser.parse_args()
    
    # Initialize benchmark
    benchmark = PerformanceBenchmark(mock_mode=True)
    
    try:
        # Configuration
        config = {
            "num_operations": args.operations,
            "concurrency": args.concurrency,
            "vector_dimension": args.dimension,
            "batch_size": args.batch_size,
            "warmup_operations": args.warmup,
            "collection_name": "benchmark_collection"
        }
        
        if args.benchmark == "all":
            # Run comprehensive benchmark
            results = await benchmark.run_comprehensive_benchmark(config)
            
            # Print summary
            print(json.dumps(results["summary"], indent=2))
            
        else:
            # Run specific benchmark
            benchmark_config = BenchmarkConfig(**config, operation=args.benchmark)
            
            if args.benchmark == "search":
                result = await benchmark.benchmark_vector_search(benchmark_config)
            elif args.benchmark == "insert":
                result = await benchmark.benchmark_vector_insert(benchmark_config)
            elif args.benchmark == "batch":
                result = await benchmark.benchmark_batch_insert(benchmark_config)
            elif args.benchmark == "embedding":
                result = await benchmark.benchmark_embedding_generation(benchmark_config)
            
            print(json.dumps(asdict(result), indent=2))
        
        # Print results table
        benchmark.print_results_table()
        
        # Save results if requested
        if args.output:
            benchmark.save_results(args.output)
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

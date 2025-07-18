#!/usr/bin/env python3
"""
System Validation Script

Comprehensive validation of the HXP Vector Database Shared Library system.
Validates all components, integration, and readiness for deployment.

Author: Citadel AI Team
License: MIT
"""

import sys
import asyncio
import json
import time
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result data structure."""
    component: str
    test_name: str
    status: str  # "PASS", "FAIL", "SKIP"
    message: str
    duration_ms: float
    details: Optional[Dict[str, Any]] = None


class SystemValidator:
    """
    System Validation Tool
    
    Comprehensive validation of all system components and integration.
    """
    
    def __init__(self):
        """Initialize system validator."""
        self.results: List[ValidationResult] = []
        self.logger = logging.getLogger(__name__)
    
    def _log_result(self, result: ValidationResult):
        """Log validation result."""
        status_emoji = {
            "PASS": "✅",
            "FAIL": "❌",
            "SKIP": "⏭️"
        }
        
        emoji = status_emoji.get(result.status, "❓")
        self.logger.info(f"{emoji} {result.component}.{result.test_name}: {result.message} ({result.duration_ms:.2f}ms)")
    
    async def _run_validation(self, component: str, test_name: str, test_func) -> ValidationResult:
        """Run a single validation test."""
        start_time = time.time()
        
        try:
            await test_func()
            end_time = time.time()
            
            result = ValidationResult(
                component=component,
                test_name=test_name,
                status="PASS",
                message="Validation successful",
                duration_ms=(end_time - start_time) * 1000
            )
            
        except Exception as e:
            end_time = time.time()
            
            result = ValidationResult(
                component=component,
                test_name=test_name,
                status="FAIL",
                message=f"Validation failed: {str(e)}",
                duration_ms=(end_time - start_time) * 1000,
                details={"error": str(e), "traceback": traceback.format_exc()}
            )
        
        self.results.append(result)
        self._log_result(result)
        return result
    
    async def validate_core_imports(self):
        """Validate core module imports."""
        
        async def test_core_imports():
            # Test core imports
            from hana_x_vector import VectorDatabase, APIGateway
            from hana_x_vector.core.vector_operations import VectorOperations
            from hana_x_vector.core.embedding_service import EmbeddingService
            from hana_x_vector.core.gpu_manager import GPUMemoryManager
            
            # Verify classes can be instantiated
            vector_db = VectorDatabase()
            api_gateway = APIGateway(vector_db)
            gpu_manager = GPUMemoryManager()
            
            assert vector_db is not None
            assert api_gateway is not None
            assert gpu_manager is not None
        
        await self._run_validation("core", "imports", test_core_imports)
    
    async def validate_protocol_abstraction(self):
        """Validate protocol abstraction layer."""
        
        async def test_protocol_imports():
            from hana_x_vector.protocols import ProtocolAbstractionLayer, ProtocolType
            from hana_x_vector.protocols.graphql_schema import VectorSearchQuery
            from hana_x_vector.protocols.grpc_service import VectorServiceServicer
            
            # Test protocol types
            assert ProtocolType.REST is not None
            assert ProtocolType.GRAPHQL is not None
            assert ProtocolType.GRPC is not None
            
            # Test GraphQL schema
            assert VectorSearchQuery is not None
            
            # Test gRPC service
            assert VectorServiceServicer is not None
        
        await self._run_validation("protocols", "imports", test_protocol_imports)
    
    async def validate_migration_system(self):
        """Validate migration system."""
        
        async def test_migration_imports():
            from hana_x_vector.migration import MigrationManager, CollectionMigration, MigrationStatus
            
            # Test migration classes
            assert MigrationManager is not None
            assert CollectionMigration is not None
            assert MigrationStatus is not None
            
            # Test migration status enum
            assert MigrationStatus.PENDING is not None
            assert MigrationStatus.COMPLETED is not None
            assert MigrationStatus.FAILED is not None
        
        await self._run_validation("migration", "imports", test_migration_imports)
    
    async def validate_external_models(self):
        """Validate external model integration."""
        
        async def test_external_model_imports():
            from hana_x_vector.external_models import ExternalModelRegistry
            from hana_x_vector.external_models.model_registry import ExternalModel, ModelType
            
            # Test external model classes
            assert ExternalModelRegistry is not None
            assert ExternalModel is not None
            assert ModelType is not None
            
            # Test model types
            assert ModelType.LANGUAGE_MODEL is not None
            assert ModelType.EMBEDDING_MODEL is not None
        
        await self._run_validation("external_models", "imports", test_external_model_imports)
    
    async def validate_gateway_integration(self):
        """Validate API Gateway integration."""
        
        async def test_gateway_imports():
            from hana_x_vector.gateway import APIGateway
            from hana_x_vector.gateway.api_gateway import router
            
            # Test gateway components
            assert APIGateway is not None
            assert router is not None
        
        await self._run_validation("gateway", "imports", test_gateway_imports)
    
    async def validate_orchestration(self):
        """Validate service orchestration."""
        
        async def test_orchestration_imports():
            from hana_x_vector.orchestration import ServiceOrchestrator
            from hana_x_vector.orchestration.service_manager import ServiceStatus
            
            # Test orchestration classes
            assert ServiceOrchestrator is not None
            assert ServiceStatus is not None
        
        await self._run_validation("orchestration", "imports", test_orchestration_imports)
    
    async def validate_cli_commands(self):
        """Validate CLI commands."""
        
        async def test_cli_imports():
            from hana_x_vector.cli.main import app
            from hana_x_vector.cli.commands.database import database_app
            from hana_x_vector.cli.commands.migration import migration_app
            
            # Test CLI components
            assert app is not None
            assert database_app is not None
            assert migration_app is not None
        
        await self._run_validation("cli", "imports", test_cli_imports)
    
    async def validate_models_and_schemas(self):
        """Validate data models and schemas."""
        
        async def test_model_imports():
            from hana_x_vector.models.vector_models import Vector, VectorSearchRequest, VectorSearchResult
            from hana_x_vector.models.external_models import ExternalModel, ModelType, ModelCapability
            
            # Test vector models
            assert Vector is not None
            assert VectorSearchRequest is not None
            assert VectorSearchResult is not None
            
            # Test external model models
            assert ExternalModel is not None
            assert ModelType is not None
            assert ModelCapability is not None
        
        await self._run_validation("models", "imports", test_model_imports)
    
    async def validate_utilities(self):
        """Validate utility modules."""
        
        async def test_utility_imports():
            from hana_x_vector.utils.config import get_config
            from hana_x_vector.utils.logging import get_logger
            from hana_x_vector.utils.metrics import MetricsCollector
            
            # Test utility functions
            assert get_config is not None
            assert get_logger is not None
            assert MetricsCollector is not None
        
        await self._run_validation("utils", "imports", test_utility_imports)
    
    async def validate_gpu_manager(self):
        """Validate GPU memory manager."""
        
        async def test_gpu_manager():
            from hana_x_vector.core.gpu_manager import GPUMemoryManager
            
            # Initialize GPU manager
            gpu_manager = GPUMemoryManager()
            
            # Test GPU info (should work even without actual GPUs)
            gpu_info = gpu_manager.get_gpu_info()
            assert isinstance(gpu_info, dict)
            
            # Test allocation summary
            summary = gpu_manager.get_allocation_summary()
            assert isinstance(summary, dict)
            assert "total_models" in summary
            assert "gpu_utilization" in summary
        
        await self._run_validation("gpu_manager", "functionality", test_gpu_manager)
    
    async def validate_performance_benchmark(self):
        """Validate performance benchmark script."""
        
        async def test_benchmark_imports():
            # Import benchmark script modules
            benchmark_path = Path(__file__).parent / "performance_benchmark.py"
            
            # Check if benchmark script exists
            assert benchmark_path.exists(), "Performance benchmark script not found"
            
            # Test that script can be imported
            import importlib.util
            spec = importlib.util.spec_from_file_location("performance_benchmark", benchmark_path)
            benchmark_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(benchmark_module)
            
            # Test benchmark classes
            assert hasattr(benchmark_module, "PerformanceBenchmark")
            assert hasattr(benchmark_module, "BenchmarkResult")
            assert hasattr(benchmark_module, "BenchmarkConfig")
        
        await self._run_validation("benchmark", "script_validation", test_benchmark_imports)
    
    async def validate_integration_tests(self):
        """Validate integration test files."""
        
        async def test_integration_files():
            # Check integration test files exist
            test_files = [
                "tests/integration/test_protocol_integration.py",
                "tests/integration/test_migration_integration.py",
                "tests/integration/test_end_to_end.py"
            ]
            
            base_path = Path(__file__).parent.parent
            
            for test_file in test_files:
                file_path = base_path / test_file
                assert file_path.exists(), f"Integration test file not found: {test_file}"
                
                # Check file is not empty
                assert file_path.stat().st_size > 0, f"Integration test file is empty: {test_file}"
        
        await self._run_validation("integration_tests", "file_validation", test_integration_files)
    
    async def validate_project_structure(self):
        """Validate project structure."""
        
        async def test_project_structure():
            base_path = Path(__file__).parent.parent
            
            # Required directories
            required_dirs = [
                "src/hana_x_vector",
                "src/hana_x_vector/core",
                "src/hana_x_vector/protocols",
                "src/hana_x_vector/migration",
                "src/hana_x_vector/external_models",
                "src/hana_x_vector/gateway",
                "src/hana_x_vector/orchestration",
                "src/hana_x_vector/cli",
                "src/hana_x_vector/models",
                "src/hana_x_vector/utils",
                "tests/integration",
                "scripts"
            ]
            
            for dir_path in required_dirs:
                full_path = base_path / dir_path
                assert full_path.exists(), f"Required directory not found: {dir_path}"
                assert full_path.is_dir(), f"Path is not a directory: {dir_path}"
            
            # Required files
            required_files = [
                "pyproject.toml",
                "src/hana_x_vector/__init__.py",
                "scripts/download_models.py",
                "scripts/performance_benchmark.py"
            ]
            
            for file_path in required_files:
                full_path = base_path / file_path
                assert full_path.exists(), f"Required file not found: {file_path}"
                assert full_path.is_file(), f"Path is not a file: {file_path}"
        
        await self._run_validation("project", "structure", test_project_structure)
    
    async def validate_package_configuration(self):
        """Validate package configuration."""
        
        async def test_package_config():
            import tomllib
            
            # Read pyproject.toml
            base_path = Path(__file__).parent.parent
            pyproject_path = base_path / "pyproject.toml"
            
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
            
            # Validate project metadata
            assert "project" in config
            assert config["project"]["name"] == "hana-x-vector"
            assert "version" in config["project"]
            assert "dependencies" in config["project"]
            
            # Validate build system
            assert "build-system" in config
            assert config["build-system"]["requires"] == ["setuptools>=61.0", "wheel"]
            
            # Validate scripts
            assert "project" in config
            assert "scripts" in config["project"]
            assert "hxp-vector" in config["project"]["scripts"]
        
        await self._run_validation("package", "configuration", test_package_config)
    
    async def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run comprehensive system validation."""
        self.logger.info("Starting comprehensive system validation")
        self.logger.info("=" * 80)
        
        # Define validation tests
        validations = [
            ("Core Components", self.validate_core_imports),
            ("Protocol Abstraction", self.validate_protocol_abstraction),
            ("Migration System", self.validate_migration_system),
            ("External Models", self.validate_external_models),
            ("API Gateway", self.validate_gateway_integration),
            ("Service Orchestration", self.validate_orchestration),
            ("CLI Commands", self.validate_cli_commands),
            ("Data Models", self.validate_models_and_schemas),
            ("Utilities", self.validate_utilities),
            ("GPU Manager", self.validate_gpu_manager),
            ("Performance Benchmark", self.validate_performance_benchmark),
            ("Integration Tests", self.validate_integration_tests),
            ("Project Structure", self.validate_project_structure),
            ("Package Configuration", self.validate_package_configuration)
        ]
        
        # Run all validations
        for validation_name, validation_func in validations:
            self.logger.info(f"\n🔍 Validating: {validation_name}")
            await validation_func()
        
        # Generate summary
        summary = self._generate_validation_summary()
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info("VALIDATION SUMMARY")
        self.logger.info("=" * 80)
        
        # Print summary
        self.logger.info(f"Total Tests: {summary['total_tests']}")
        self.logger.info(f"✅ Passed: {summary['passed_tests']}")
        self.logger.info(f"❌ Failed: {summary['failed_tests']}")
        self.logger.info(f"⏭️ Skipped: {summary['skipped_tests']}")
        self.logger.info(f"Success Rate: {summary['success_rate']:.1f}%")
        
        if summary['failed_tests'] > 0:
            self.logger.info("\n❌ FAILED TESTS:")
            for result in self.results:
                if result.status == "FAIL":
                    self.logger.error(f"  - {result.component}.{result.test_name}: {result.message}")
        
        # Overall status
        if summary['failed_tests'] == 0:
            self.logger.info("\n🎉 ALL VALIDATIONS PASSED - SYSTEM READY FOR DEPLOYMENT")
        else:
            self.logger.warning(f"\n⚠️ {summary['failed_tests']} VALIDATION(S) FAILED - REVIEW REQUIRED")
        
        return {
            "summary": summary,
            "results": [asdict(result) for result in self.results],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_validation_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == "PASS")
        failed_tests = sum(1 for r in self.results if r.status == "FAIL")
        skipped_tests = sum(1 for r in self.results if r.status == "SKIP")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Component breakdown
        components = {}
        for result in self.results:
            if result.component not in components:
                components[result.component] = {"pass": 0, "fail": 0, "skip": 0}
            components[result.component][result.status.lower()] += 1
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "success_rate": success_rate,
            "components": components,
            "overall_status": "PASS" if failed_tests == 0 else "FAIL"
        }
    
    def save_results(self, filename: str) -> None:
        """Save validation results to file."""
        try:
            results_data = {
                "results": [asdict(result) for result in self.results],
                "summary": self._generate_validation_summary(),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            self.logger.info(f"Validation results saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")


async def main():
    """Main function for script execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="System validation tool")
    parser.add_argument("--output", help="Output file for validation results")
    parser.add_argument("--component", help="Validate specific component only")
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = SystemValidator()
    
    try:
        # Run validation
        if args.component:
            # Run specific component validation
            component_methods = {
                "core": validator.validate_core_imports,
                "protocols": validator.validate_protocol_abstraction,
                "migration": validator.validate_migration_system,
                "external_models": validator.validate_external_models,
                "gateway": validator.validate_gateway_integration,
                "orchestration": validator.validate_orchestration,
                "cli": validator.validate_cli_commands,
                "models": validator.validate_models_and_schemas,
                "utils": validator.validate_utilities,
                "gpu": validator.validate_gpu_manager,
                "benchmark": validator.validate_performance_benchmark,
                "tests": validator.validate_integration_tests,
                "structure": validator.validate_project_structure,
                "package": validator.validate_package_configuration
            }
            
            if args.component in component_methods:
                await component_methods[args.component]()
            else:
                print(f"Unknown component: {args.component}")
                print(f"Available components: {', '.join(component_methods.keys())}")
                sys.exit(1)
        else:
            # Run comprehensive validation
            results = await validator.run_comprehensive_validation()
        
        # Save results if requested
        if args.output:
            validator.save_results(args.output)
        
        # Exit with appropriate code
        summary = validator._generate_validation_summary()
        sys.exit(0 if summary["failed_tests"] == 0 else 1)
        
    except KeyboardInterrupt:
        print("\nValidation interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Validation failed: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

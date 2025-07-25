#!/usr/bin/env python3
"""
Comprehensive Business Model Validation for Server-02
Tests all 5 specialized business models with real-world scenarios
"""

import asyncio
import httpx
import time
import json
from typing import Dict, List

class BusinessModelValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.timeout = 180.0
        self.results = {}
        
    async def test_yi34b_business_reasoning(self):
        """Test Yi-34B for advanced business reasoning"""
        print("\n📊 Testing Yi-34B: Business Reasoning & Strategic Analysis")
        
        scenarios = [
            {
                "name": "Market Analysis",
                "prompt": "Analyze the competitive landscape for AI-driven business solutions in 2025. What are the key opportunities and threats?",
                "max_tokens": 300
            },
            {
                "name": "Decision Support",
                "prompt": "A company is deciding between expanding internationally or investing in R&D. Provide a strategic framework for this decision.",
                "max_tokens": 250
            }
        ]
        
        return await self._run_model_tests("yi-34b", scenarios)
    
    async def test_deepcoder_programming(self):
        """Test DeepCoder for code generation and programming assistance"""
        print("\n💻 Testing DeepCoder: Code Generation & Programming")
        
        scenarios = [
            {
                "name": "API Development",
                "prompt": "Create a FastAPI endpoint for user authentication with JWT tokens, including proper error handling.",
                "max_tokens": 400
            },
            {
                "name": "Database Query",
                "prompt": "Write a Python function to safely query a PostgreSQL database with connection pooling and transaction handling.",
                "max_tokens": 350
            }
        ]
        
        return await self._run_model_tests("deepcoder", scenarios)
    
    async def test_qwen_high_volume(self):
        """Test QWen for high-volume operations and quick responses"""
        print("\n⚡ Testing QWen: High-Volume Operations & Quick Responses")
        
        scenarios = [
            {
                "name": "Customer Support",
                "prompt": "Customer can't log in to their account. Provide step-by-step troubleshooting.",
                "max_tokens": 150
            },
            {
                "name": "Quick FAQ",
                "prompt": "What are your business hours and contact information?",
                "max_tokens": 100
            },
            {
                "name": "Status Check",
                "prompt": "How do I check my order status?",
                "max_tokens": 80
            }
        ]
        
        return await self._run_model_tests("qwen", scenarios)
    
    async def test_jarvis_productivity(self):
        """Test JARVIS for business productivity and assistance"""
        print("\n🤖 Testing JARVIS: Business Productivity & General Assistance")
        
        scenarios = [
            {
                "name": "Meeting Planning",
                "prompt": "Help me plan a quarterly team meeting agenda with key topics and time allocation.",
                "max_tokens": 250
            },
            {
                "name": "Task Management",
                "prompt": "Organize these tasks by priority: update documentation, client call, budget review, team standup.",
                "max_tokens": 200
            }
        ]
        
        return await self._run_model_tests("jarvis", scenarios)
    
    async def test_deepseek_research(self):
        """Test DeepSeek-R1 for research analysis and deep thinking"""
        print("\n🔬 Testing DeepSeek-R1: Research Analysis & Deep Analytical Thinking")
        
        scenarios = [
            {
                "name": "Technical Research",
                "prompt": "Analyze the implications of quantum computing on current encryption methods. What should businesses prepare for?",
                "max_tokens": 400
            },
            {
                "name": "Trend Analysis",
                "prompt": "Research the evolution of remote work technologies. What patterns emerge and what's next?",
                "max_tokens": 350
            }
        ]
        
        return await self._run_model_tests("deepseek", scenarios)
    
    async def _run_model_tests(self, model: str, scenarios: List[Dict]) -> Dict:
        """Run test scenarios for a specific model"""
        model_results = {
            "model": model,
            "scenarios": [],
            "total_time": 0,
            "avg_time": 0,
            "success_rate": 0
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for scenario in scenarios:
                print(f"  → {scenario['name']}...")
                start_time = time.time()
                
                try:
                    response = await client.post(
                        f"{self.base_url}/v1/chat/completions",
                        json={
                            "model": model,
                            "messages": [{"role": "user", "content": scenario["prompt"]}],
                            "max_tokens": scenario["max_tokens"]
                        }
                    )
                    
                    duration = time.time() - start_time
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                        token_count = len(content.split())
                        
                        scenario_result = {
                            "name": scenario["name"],
                            "success": True,
                            "duration": duration,
                            "tokens": token_count,
                            "status": "✅ PASSED"
                        }
                        print(f"    ✅ {duration:.1f}s, {token_count} tokens")
                    else:
                        scenario_result = {
                            "name": scenario["name"],
                            "success": False,
                            "duration": duration,
                            "error": f"HTTP {response.status_code}",
                            "status": "❌ FAILED"
                        }
                        print(f"    ❌ Failed: HTTP {response.status_code}")
                        
                except Exception as e:
                    duration = time.time() - start_time
                    scenario_result = {
                        "name": scenario["name"],
                        "success": False,
                        "duration": duration,
                        "error": str(e),
                        "status": "❌ ERROR"
                    }
                    print(f"    ❌ Error: {e}")
                
                model_results["scenarios"].append(scenario_result)
                model_results["total_time"] += duration
        
        # Calculate summary stats
        successful_scenarios = [s for s in model_results["scenarios"] if s["success"]]
        model_results["success_rate"] = len(successful_scenarios) / len(scenarios) * 100
        model_results["avg_time"] = model_results["total_time"] / len(scenarios)
        
        return model_results
    
    async def run_comprehensive_validation(self):
        """Run validation for all business models"""
        print("🚀 Starting Comprehensive Business Model Validation for Server-02")
        print("=" * 70)
        
        validation_start = time.time()
        
        # Test all models
        self.results["yi34b"] = await self.test_yi34b_business_reasoning()
        self.results["deepcoder"] = await self.test_deepcoder_programming()
        self.results["qwen"] = await self.test_qwen_high_volume()
        self.results["jarvis"] = await self.test_jarvis_productivity()
        self.results["deepseek"] = await self.test_deepseek_research()
        
        total_duration = time.time() - validation_start
        
        # Print summary report
        self.print_summary_report(total_duration)
        
        return self.results
    
    def print_summary_report(self, total_duration: float):
        """Print comprehensive validation summary"""
        print("\n" + "=" * 70)
        print("📋 BUSINESS MODEL VALIDATION SUMMARY REPORT")
        print("=" * 70)
        
        overall_success = True
        total_scenarios = 0
        successful_scenarios = 0
        
        for model_name, results in self.results.items():
            print(f"\n🔹 {results['model'].upper()}:")
            print(f"   Success Rate: {results['success_rate']:.1f}%")
            print(f"   Average Time: {results['avg_time']:.1f}s")
            print(f"   Total Time: {results['total_time']:.1f}s")
            
            for scenario in results["scenarios"]:
                print(f"   • {scenario['name']}: {scenario['status']}")
                
            total_scenarios += len(results["scenarios"])
            successful_scenarios += len([s for s in results["scenarios"] if s["success"]])
            
            if results['success_rate'] < 100:
                overall_success = False
        
        print(f"\n📊 OVERALL RESULTS:")
        print(f"   Total Test Duration: {total_duration:.1f}s")
        print(f"   Models Tested: {len(self.results)}/5")
        print(f"   Scenarios Tested: {successful_scenarios}/{total_scenarios}")
        print(f"   Overall Success Rate: {(successful_scenarios/total_scenarios*100):.1f}%")
        
        if overall_success:
            print(f"\n🎉 VALIDATION RESULT: ✅ ALL BUSINESS MODELS PASSED")
        else:
            print(f"\n⚠️  VALIDATION RESULT: ❌ SOME ISSUES DETECTED")
        
        print("=" * 70)

async def main():
    validator = BusinessModelValidator()
    await validator.run_comprehensive_validation()

if __name__ == "__main__":
    asyncio.run(main())

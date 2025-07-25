"""
Business Model Configuration for Server-02
Maps user-friendly names to Ollama model identifiers
"""

BUSINESS_MODEL_MAPPING = {
    "yi-34b": "yi:34b-chat",          # Business reasoning and analysis
    "deepcoder": "deepcoder:14b",     # Code generation and programming
    "qwen": "qwen:1.8b",              # High-volume operations and quick responses
    "jarvis": "hadad/JARVIS:latest",  # Business assistant and general queries
    "deepseek": "deepseek-r1:32b"     # Research analysis and deep thinking
}

# Model capabilities and use cases
MODEL_CAPABILITIES = {
    "yi-34b": {
        "description": "Advanced business reasoning and strategic analysis",
        "use_cases": ["Business strategy", "Market analysis", "Decision support"],
        "size": "19 GB",
        "vram_required": "16+ GB"
    },
    "deepcoder": {
        "description": "Specialized code generation and programming assistance", 
        "use_cases": ["Code generation", "Debugging", "Technical documentation"],
        "size": "9.0 GB",
        "vram_required": "8+ GB"
    },
    "qwen": {
        "description": "High-volume operations and quick responses",
        "use_cases": ["Customer service", "Quick queries", "High-frequency tasks"],
        "size": "1.1 GB", 
        "vram_required": "2+ GB"
    },
    "jarvis": {
        "description": "Business assistant for general productivity",
        "use_cases": ["General assistance", "Productivity", "Task management"],
        "size": "29 GB",
        "vram_required": "16+ GB"  
    },
    "deepseek": {
        "description": "Research analysis and deep analytical thinking",
        "use_cases": ["Research", "Complex analysis", "Academic work"],
        "size": "19 GB",
        "vram_required": "16+ GB"
    }
}

# Default model for different use cases
DEFAULT_MODELS = {
    "high_volume": "qwen",        # Fastest for high-frequency operations
    "business": "yi-34b",         # Best for business reasoning
    "coding": "deepcoder",        # Best for code generation
    "general": "jarvis",          # Best general assistant
    "research": "deepseek",       # Best for research and analysis
    "fallback": "qwen"            # Fastest fallback model
}

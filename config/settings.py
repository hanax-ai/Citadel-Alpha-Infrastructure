"""
Server-02 Configuration Settings
HX-Enterprise-LLM-Server-02 Business Model Configuration
"""

# Server identification
SERVER_NAME = "hx-llm-server-02"
SERVER_IP = "192.168.10.28"
SERVER_PORT = 8000

# Ollama configuration (update from Server-01 settings)
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_TIMEOUT = 3600

# Database connections (keep Server-01 proven connections)
POSTGRES_HOST = "192.168.10.35"
POSTGRES_PORT = 5432
POSTGRES_DB = "citadel_llm"
POSTGRES_USER = "citadel_user"

# Vector database 
QDRANT_HOST = "192.168.10.30"
QDRANT_PORT = 6333

# Metrics server
PROMETHEUS_HOST = "192.168.10.37"
PROMETHEUS_PORT = 9090

# Business model specific settings
DEFAULT_BUSINESS_MODEL = "qwen"  # For high-volume operations
FALLBACK_MODEL = "qwen"          # Fastest model for fallback

# Environment and paths
CITADEL_HOME = "/opt/citadel-02"
LOG_DIR = "/opt/citadel-02/logs"

# API Configuration
API_VERSION = "v1"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Health check settings
HEALTH_CHECK_INTERVAL = 30  # seconds
HEALTH_CHECK_TIMEOUT = 10   # seconds

# Rate limiting (requests per minute)
RATE_LIMIT_RPM = 60
RATE_LIMIT_BURST = 10

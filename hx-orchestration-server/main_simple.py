"""
Citadel AI Operating System - Gateway v2.0
Enterprise AI Runtime Environment for Business Process Automation
HANA-X Lab Infrastructure Integration (hx-orchestration-server: 192.168.10.31)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="Citadel AI Operating System - Gateway",
    description="Enterprise AI Runtime Environment and Business Process Automation Gateway",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Citadel AI Operating System - Gateway",
        "version": "2.0.0",
        "status": "operational",
        "server": "hx-orchestration-server",
        "ip": "192.168.10.31",
        "port": 8002,
        "role": "enterprise_gateway",
        "capabilities": [
            "business_process_automation",
            "ai_workflow_orchestration", 
            "hana_x_lab_integration",
            "enterprise_security"
        ],
        "hana_x_infrastructure": {
            "llm_servers": ["192.168.10.29", "192.168.10.28"],
            "vector_db": "192.168.10.30",
            "sql_db": "192.168.10.35",
            "dev_server": "192.168.10.33",
            "test_server": "192.168.10.34",
            "devops_server": "192.168.10.36"
        },
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "api_status": "/status"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "citadel-gateway",
        "version": "2.0.0",
        "timestamp": "2025-07-25T22:58:00Z"
    }

@app.get("/status")
async def api_status():
    """API status endpoint"""
    return {
        "api_version": "v2.0",
        "environment": "production",
        "features": {
            "business_automation": "ready",
            "ai_orchestration": "ready",
            "hana_x_integration": "ready"
        }
    }

if __name__ == "__main__":
    print("🚀 Starting Citadel AI Operating System - Gateway")
    print("📡 Server: hx-orchestration-server (192.168.10.31:8002)")
    print("🎯 Role: Enterprise AI Gateway")
    print("🔗 HANA-X Lab Integration: Active")
    print()
    
    uvicorn.run(
        "main_simple:app",
        host="0.0.0.0",           # Accept all interfaces
        port=8002,                # Production gateway port
        workers=8,                # High-performance workers
        reload=False
    )

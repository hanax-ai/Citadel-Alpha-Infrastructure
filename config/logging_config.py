"""
Logging Configuration for Server-02
HX-Enterprise-LLM-Server-02 Business Model Logging
"""

import os

# Update log file paths for Server-02
LOG_DIR = "/opt/citadel-02/logs"

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - [Server-02] %(message)s"
        },
        "simple": {
            "format": "%(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },
        "gateway_file": {
            "class": "logging.FileHandler",
            "filename": f"{LOG_DIR}/gateway/server-02-gateway.log",
            "formatter": "detailed",
            "level": "INFO"
        },
        "business_models": {
            "class": "logging.FileHandler", 
            "filename": f"{LOG_DIR}/gateway/business-models.log",
            "formatter": "detailed",
            "level": "INFO"
        },
        "sql_service": {
            "class": "logging.FileHandler",
            "filename": f"{LOG_DIR}/gateway/sql-service.log", 
            "formatter": "detailed",
            "level": "INFO"
        },
        "vector_service": {
            "class": "logging.FileHandler",
            "filename": f"{LOG_DIR}/gateway/vector-service.log",
            "formatter": "detailed", 
            "level": "INFO"
        }
    },
    "loggers": {
        "citadel_llm.api.gateway": {
            "level": "INFO",
            "handlers": ["gateway_file", "console"],
            "propagate": False
        },
        "citadel_llm.services": {
            "level": "INFO", 
            "handlers": ["business_models", "console"],
            "propagate": False
        },
        "citadel_llm.services.sql_service": {
            "level": "INFO",
            "handlers": ["sql_service", "console"],
            "propagate": False
        },
        "citadel_llm.services.vector_service": {
            "level": "INFO",
            "handlers": ["vector_service", "console"], 
            "propagate": False
        }
    },
    "root": {
        "level": "INFO",
        "handlers": ["gateway_file", "console"]
    }
}

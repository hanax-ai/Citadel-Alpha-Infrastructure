# Complete Model Inventory by Server
**Generated**: July 23, 2025  
**Source**: Direct API calls to Ollama instances

---

## 📊 **Server 01: 192.168.10.28:11434**

### **Available Models (5 total - 72GB)**
| Model Name | Size | Type | Last Modified |
|------------|------|------|---------------|
| **deepseek-r1:32b** | 18GB | Advanced Reasoning | July 23, 2025 |
| **hadad/JARVIS:latest** | 27GB | Large Conversational AI | July 23, 2025 |
| **qwen:1.8b** | 1GB | Lightweight Efficient | July 23, 2025 |
| **deepcoder:14b** | 8GB | Code Generation | July 23, 2025 |
| **yi:34b-chat** | 18GB | Large Chat Model | July 23, 2025 |

### **Model Specializations (Server 01)**
- **Reasoning**: deepseek-r1:32b (18GB) - Advanced reasoning and problem-solving
- **Conversational**: hadad/JARVIS:latest (27GB) - Large-scale conversational AI
- **Lightweight**: qwen:1.8b (1GB) - Fast, efficient responses
- **Code**: deepcoder:14b (8GB) - Programming and code generation
- **Chat**: yi:34b-chat (18GB) - General purpose chat model

---

## 📊 **Server 02: 192.168.10.29:11434**

### **Available Models (6 total - 77GB)**
| Model Name | Size | Type | Last Modified |
|------------|------|------|---------------|
| **nomic-embed-text:latest** | <1GB | Text Embeddings | July 23, 2025 |
| **mixtral:8x7b** | 24GB | Mixture of Experts | July 22, 2025 |
| **phi3:latest** | 2GB | Microsoft Small Model | July 22, 2025 |
| **mixtral:latest** | 24GB | Mixture of Experts | July 22, 2025 |
| **openchat:latest** | 3GB | Conversational | July 22, 2025 |
| **nous-hermes2-mixtral:latest** | 24GB | Enhanced Mixtral | July 22, 2025 |

### **Model Specializations (Server 02)**
- **Embeddings**: nomic-embed-text:latest (<1GB) - Text embeddings and similarity
- **MoE Large**: mixtral variants (24GB each) - Mixture of Experts architecture
- **Lightweight**: phi3:latest (2GB) - Microsoft's efficient model
- **Conversational**: openchat:latest (3GB) - Optimized for chat
- **Enhanced**: nous-hermes2-mixtral:latest (24GB) - Fine-tuned Mixtral

---

## 🔍 **Model Distribution Analysis**

### **By Model Type**
- **Large Models (>15GB)**: 7 models total
  - Server 01: deepseek-r1, JARVIS, yi:34b-chat (3 models)
  - Server 02: mixtral variants, nous-hermes2 (4 models)

- **Medium Models (5-15GB)**: 1 model total
  - Server 01: deepcoder:14b (1 model)

- **Small Models (<5GB)**: 3 models total
  - Server 01: qwen:1.8b (1 model)
  - Server 02: phi3, openchat (2 models)

- **Embedding Models**: 1 model total
  - Server 02: nomic-embed-text (1 model)

### **By Use Case**
- **Code Generation**: deepcoder:14b (Server 01)
- **Text Embeddings**: nomic-embed-text (Server 02)
- **Conversational AI**: JARVIS, openchat, yi:34b-chat
- **Reasoning**: deepseek-r1 (Server 01)
- **Efficient/Lightweight**: qwen:1.8b (Server 01), phi3 (Server 02)
- **Mixture of Experts**: mixtral variants, nous-hermes2 (Server 02)

### **Total Capacity**
- **Server 01**: 5 models, ~72GB total
- **Server 02**: 6 models, ~77GB total
- **Combined**: 11 unique models, ~149GB total

---

## 🚀 **Access Configuration Options**

### **Option A: Direct OpenWebUI Multi-Server Access**
```bash
# .env configuration for OpenWebUI
OLLAMA_BASE_URLS=http://192.168.10.28:11434;http://192.168.10.29:11434
```
**Result**: All 11 models available with automatic load balancing

### **Option B: Current Gateway (Limited)**
**Current gateway models** (needs updating):
```
phi3, openchat, mixtral, nous-hermes2-mixtral, nomic-embed-text
```
**Available through gateway**: Only 5 models from Server 02

### **Option C: Enhanced Gateway (Recommended)**
**Updated gateway would support**:
- All 11 models from both servers
- Intelligent load balancing
- Health monitoring
- Cache across all models
- Comprehensive metrics

---

## 📋 **Recommendations**

### **Immediate Access (Option A)**
Use OpenWebUI multi-server configuration to access all models immediately.

### **Production Enhancement**
Implement Enhanced Gateway with:
1. **Model mapping** for all 11 models
2. **Server routing** based on model location
3. **Load balancing** for overlapping capabilities
4. **Health checks** for server availability

### **Model-to-Server Routing Strategy**
```python
# Recommended routing
SERVER_01_MODELS = ["deepseek-r1", "jarvis", "qwen", "deepcoder", "yi-chat"]
SERVER_02_MODELS = ["nomic-embed-text", "mixtral", "phi3", "openchat", "nous-hermes2"]

# Load balancing candidates (similar capabilities)
CONVERSATIONAL_MODELS = {
    "lightweight": ["qwen:1.8b", "phi3:latest"],
    "medium": ["openchat:latest", "yi:34b-chat"],
    "large": ["hadad/JARVIS:latest", "nous-hermes2-mixtral:latest"]
}
```

This gives you the complete picture of your model inventory and access options!

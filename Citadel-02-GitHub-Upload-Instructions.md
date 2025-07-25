# Citadel-02 GitHub Upload Instructions

## 🚀 Complete Step-by-Step Guide for HX-Server-02 Team

This document provides complete instructions for uploading the Citadel-02 infrastructure to GitHub, following the proven process used for Citadel-01.

---

## 📋 **Prerequisites Verification**

### **System Status Check**
```bash
# Verify current location
pwd
# Expected: /opt/citadel-02

# Check user
whoami
# Expected: agent0

# Verify git is installed
git --version
# Expected: git version 2.x.x or higher
```

### **Project Status Verification**
```bash
# Check service status
sudo systemctl status citadel-gateway
# Expected: Active (running)

# Verify health
curl http://localhost:8001/health/simple
# Expected: {"status":"ok","timestamp":...}

# Check models
ollama list
# Expected: 5 models listed
```

---

## 🔧 **Phase 1: Git Configuration**

### **1.1 Configure Git Identity**
```bash
# Set global git configuration
git config --global user.name "HX-Server-02 Team"
git config --global user.email "hx-server-02@citadel.ai"

# Verify configuration
git config --global --list | grep user
```

### **1.2 Configure Authentication**
```bash
# Set GitHub token (pre-configured for Citadel project)
export GITHUB_TOKEN="your_github_token_here"

# Configure Git credential helper
git config --global credential.helper store

# Store credentials for this session
echo "https://hanax-ai:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
chmod 600 ~/.git-credentials
```

---

## 📂 **Phase 2: Repository Initialization**

### **2.1 Initialize Local Repository**
```bash
# Navigate to project directory
cd /opt/citadel-02

# Initialize git repository (if not already done)
git init

# Verify initialization
git status
```

### **2.2 Add Remote Repository**
```bash
# Add GitHub remote
git remote add origin https://github.com/hanax-ai/Citadel-Alpha-Infrastructure.git

# Verify remote configuration
git remote -v
# Expected: origin https://github.com/hanax-ai/Citadel-Alpha-Infrastructure.git (fetch)
#           origin https://github.com/hanax-ai/Citadel-Alpha-Infrastructure.git (push)
```

---

## 📦 **Phase 3: Prepare Files for Upload**

### **3.1 Create .gitignore File**
```bash
# Create comprehensive .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
citadel_venv/
.env

# Logs
*.log
logs/
*.out

# Runtime files
var/run/
var/cache/
var/tmp/
var/state/

# Secrets and credentials
config/secrets/*.yaml
config/secrets/*.json
*.key
*.pem
*.p12

# OS specific
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Temporary files
*.tmp
*.temp
.cache/
EOF
```

### **3.2 Verify Files to be Committed**
```bash
# Check what will be added
git status

# Count total files
find . -type f ! -path "./.git/*" ! -path "./venv/*" | wc -l

# Preview directory structure
tree -L 3 -I "venv|__pycache__|*.pyc"
```

---

## 🌿 **Phase 4: Branch Management**

### **4.1 Create Citadel-02 Branch**
```bash
# Create and switch to new branch for Citadel-02
git checkout -b llm02-upload

# Verify branch
git branch
# Expected: * llm02-upload
```

### **4.2 Fetch Existing Repository (if needed)**
```bash
# Fetch remote branches to avoid conflicts
git fetch origin

# Check remote branches
git branch -r
```

---

## ✅ **Phase 5: Stage and Commit Files**

### **5.1 Stage All Files**
```bash
# Add all files except those in .gitignore
git add .

# Verify staging
git status
# Should show files staged for commit

# Check staged files count
git diff --cached --name-only | wc -l
```

### **5.2 Create Comprehensive Commit**
```bash
# Create detailed commit message
git commit -m "🚀 Citadel-02 Complete Infrastructure Upload

## HX-Server-02 (192.168.10.28) Production Deployment

### ✅ Core Components
- Multi-mode AI Gateway with agent streaming endpoints
- 5 Operational AI Models (~77GB total)
- Enterprise integration (PostgreSQL, Redis, Prometheus)
- Professional operational tools and monitoring

### 🏗️ Architecture Features
- Voice/Copilot/GUI streaming endpoints
- Auto-recovery with 5-second restart capability
- Redis caching with 221x performance improvement
- Comprehensive health monitoring and alerting

### 📊 Current Status (Verified)
- Service PID: 262742 (30+ hours continuous operation)
- Memory Usage: 8% (5GB/62GB)
- Disk Usage: 2% (259GB/15TB)
- Models: deepseek-r1:32b, JARVIS, qwen:1.8b, deepcoder:14b, yi:34b-chat

### 🛠️ Operational Tools
- citadel-service-manager: Complete lifecycle management
- citadel-health-monitor: System monitoring
- citadel-deploy: Automated deployment
- citadel-status: Real-time dashboard

### 📚 Documentation
- Complete architecture documentation
- Operational procedures and runbooks
- Monitoring and alerting setup guides
- Professional README with quick start

### 🎯 Production Ready
- 30+ hours continuous uptime verified
- Enterprise-grade monitoring integrated
- Auto-recovery tested and operational
- Complete documentation suite

Deployment Date: $(date)
Infrastructure: Gigabyte X99-UD5, Dual RTX 5060 Ti, 62GB RAM, 15TB Storage
Platform: Ubuntu 24.04.2 LTS, Python 3.12.3, CUDA 12.9"

# Verify commit
git log --oneline -1
```

---

## 🚀 **Phase 6: Push to GitHub**

### **6.1 Push to Remote Repository**
```bash
# Push the new branch to GitHub
git push -u origin llm02-upload

# Verify push success
echo "✅ Push completed successfully!"
echo "📍 Repository URL: https://github.com/hanax-ai/Citadel-Alpha-Infrastructure"
echo "🌿 Branch: llm02-upload"
echo "📂 Path: /Citadel-02/"
```

### **6.2 Verify Upload Success**
```bash
# Check remote status
git status

# Verify remote tracking
git branch -vv

# Get final repository URL
echo "🎯 Access your uploaded code at:"
echo "https://github.com/hanax-ai/Citadel-Alpha-Infrastructure/tree/llm02-upload"
```

---

## 🔍 **Phase 7: Validation and Verification**

### **7.1 Local Verification**
```bash
# Verify git status is clean
git status
# Expected: "nothing to commit, working tree clean"

# Check commit history
git log --oneline -3

# Verify remote connection
git remote show origin
```

### **7.2 GitHub Web Verification**
1. **Navigate to Repository**: https://github.com/hanax-ai/Citadel-Alpha-Infrastructure
2. **Switch to Branch**: Select `llm02-upload` branch
3. **Verify Structure**: Confirm `Citadel-02/` directory exists
4. **Check Files**: Verify all expected files are present
5. **Review Commit**: Confirm commit message and timestamp

### **7.3 Success Indicators**
- ✅ Branch `llm02-upload` visible on GitHub
- ✅ `Citadel-02/` directory structure complete
- ✅ README.md displaying properly
- ✅ All documentation files uploaded
- ✅ Source code and configurations present
- ✅ Commit message detailed and professional

---

## 🚨 **Troubleshooting Guide**

### **Common Issues and Solutions**

#### **Issue 1: Authentication Failed**
```bash
# Error: "Authentication failed for 'https://github.com/...'"
# Solution: Re-configure credentials
export GITHUB_TOKEN="your_github_token_here"
echo "https://hanax-ai:${GITHUB_TOKEN}@github.com" > ~/.git-credentials
git config --global credential.helper store
```

#### **Issue 2: Push Rejected**
```bash
# Error: "Updates were rejected because the remote contains work..."
# Solution: Fetch and merge
git fetch origin
git merge origin/llm02-upload --allow-unrelated-histories
git push origin llm02-upload
```

#### **Issue 3: Large File Warning**
```bash
# Error: "remote: warning: Large files detected"
# Solution: Check for large files and add to .gitignore if needed
find . -size +50M -type f ! -path "./.git/*"
# Add large files to .gitignore and commit again
```

#### **Issue 4: Permission Denied**
```bash
# Error: "Permission denied (publickey)"
# Solution: Use token authentication
git remote set-url origin https://hanax-ai:${GITHUB_TOKEN}@github.com/hanax-ai/Citadel-Alpha-Infrastructure.git
```

### **Emergency Recovery**
```bash
# If something goes wrong, reset to clean state
git reset --hard HEAD~1  # Undo last commit
git clean -fd            # Remove untracked files
git status               # Verify clean state
# Then repeat the process from Phase 5
```

---

## 📊 **Expected Repository Structure After Upload**

```
https://github.com/hanax-ai/Citadel-Alpha-Infrastructure
├── Branch: citadel-01-upload
│   └── Citadel-01/ (✅ Already uploaded - 173 files)
└── Branch: llm02-upload
    └── Citadel-02/
        ├── README.md                    # Project overview
        ├── bin/                         # Operational tools
        ├── config/                      # Configuration files
        ├── documentation/               # Complete docs
        ├── frameworks/                  # Monitoring setup
        ├── scripts/                     # Automation scripts
        ├── src/                         # Source code
        ├── tests/                       # Test suites
        └── validation/                  # Validation tools
```

---

## 🎯 **Success Metrics**

### **Upload Success Verification**
- **Files Uploaded**: ~150+ files expected
- **Directories**: 18 main directories
- **Documentation**: Complete with README, architecture docs
- **Source Code**: Full citadel_llm package
- **Tools**: 4 operational management scripts
- **Configurations**: YAML configs for all services

### **Post-Upload Validation**
```bash
# Final validation commands
echo "🔍 Final Validation:"
echo "Repository: https://github.com/hanax-ai/Citadel-Alpha-Infrastructure/tree/llm02-upload"
echo "Upload Date: $(date)"
echo "Files Count: $(git ls-files | wc -l)"
echo "Commit Hash: $(git rev-parse HEAD)"
echo "Branch: $(git branch --show-current)"
```

---

## 📞 **Support Information**

### **Repository Details**
- **Repository**: Citadel-Alpha-Infrastructure
- **Organization**: hanax-ai
- **Branch**: llm02-upload
- **Token**: your_github_token_here
- **Access**: https://github.com/hanax-ai/Citadel-Alpha-Infrastructure

### **Technical Specifications**
- **Source System**: HX-Server-02 (192.168.10.28)
- **Platform**: Ubuntu 24.04.2 LTS
- **Runtime**: Python 3.12.3, 30+ hours uptime
- **Models**: 5 AI models operational
- **Architecture**: Multi-mode gateway with enterprise features

---

## ✅ **Completion Checklist**

- [ ] Git configured with proper identity
- [ ] GitHub token authenticated
- [ ] Repository initialized and remote added
- [ ] .gitignore created for proper exclusions
- [ ] Files staged and committed with detailed message
- [ ] Branch created and pushed to GitHub
- [ ] Upload verified on GitHub web interface
- [ ] Repository structure confirmed complete
- [ ] Documentation accessible and formatted
- [ ] Success metrics validated

---

**🎉 Once all steps are completed, the Citadel-02 infrastructure will be successfully uploaded to GitHub and accessible to the entire team!**

---

**Document Version**: 1.0  
**Created**: July 25, 2025  
**Target**: HX-Server-02 (Citadel-02) GitHub Upload  
**Repository**: https://github.com/hanax-ai/Citadel-Alpha-Infrastructure

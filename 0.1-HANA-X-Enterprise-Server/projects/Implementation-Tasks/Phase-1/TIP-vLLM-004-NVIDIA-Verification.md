# 🔧 Task 0.4: NVIDIA Driver Verification

**Objective**: Verify NVIDIA drivers for enterprise model GPU acceleration  
**Duration**: 15 minutes  
**Dependencies**: Task 0.3 (Operating System Validation)  
**Related Models**: DeepSeek-R1-Distill-Qwen-32B, Mixtral-8x7B-Instruct-v0.1, Yi-34B-Chat, openchat-3.5-0106  
**Success Criteria**: nvidia-smi functional, GPU detection for enterprise models, CUDA runtime accessible

## Prerequisites
- [ ] Task 0.3 completed successfully (OS validated)
- [ ] Both servers have NVIDIA GPUs detected
- [ ] SSH access with administrative privileges

## Step 1: NVIDIA Driver Status - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Checking NVIDIA driver status on hx-llm-server-01..."

# Check if nvidia-smi is available and functional
ssh agent0@192.168.10.29 'nvidia-smi' && echo "✅ nvidia-smi: FUNCTIONAL" || echo "❌ nvidia-smi: NOT AVAILABLE"

# Check NVIDIA driver version
DRIVER_VERSION=$(ssh agent0@192.168.10.29 'nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>/dev/null | head -1')
if [[ "$DRIVER_VERSION" == 5* ]]; then
    echo "✅ Driver Version: PASS ($DRIVER_VERSION - 5xx series)"
else
    echo "❌ Driver Version: FAIL ($DRIVER_VERSION - expected 5xx series)"
fi

# Check loaded NVIDIA kernel modules
ssh agent0@192.168.10.29 'lsmod | grep nvidia' && echo "✅ NVIDIA Modules: LOADED" || echo "❌ NVIDIA Modules: NOT LOADED"
```

## Step 2: GPU Detection and Memory - hx-llm-server-01
```bash
echo "🔍 Verifying GPU detection and memory on hx-llm-server-01..."

# Count detected GPUs
GPU_COUNT=$(ssh agent0@192.168.10.29 'nvidia-smi -L 2>/dev/null | wc -l')
if [ "$GPU_COUNT" -ge 2 ]; then
    echo "✅ GPU Count: PASS ($GPU_COUNT GPUs detected)"
else
    echo "❌ GPU Count: FAIL ($GPU_COUNT GPUs, expected ≥2)"
fi

# Check GPU models
ssh agent0@192.168.10.29 'nvidia-smi -L'

# Check total VRAM for enterprise models
# DeepSeek-R1-Distill-Qwen-32B and Yi-34B-Chat require substantial VRAM
TOTAL_VRAM=$(ssh agent0@192.168.10.29 'nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | awk "{sum+=\$1} END {print sum}"')
if [ "$TOTAL_VRAM" -ge 30000 ]; then
    echo "✅ Total VRAM: PASS (${TOTAL_VRAM}MB ≥ 30GB for enterprise models)"
else
    echo "❌ Total VRAM: FAIL (${TOTAL_VRAM}MB < 30GB required for enterprise models)"
fi
```

## Step 3: CUDA Runtime Verification - hx-llm-server-01
```bash
echo "🔍 Checking CUDA runtime on hx-llm-server-01..."

# Check CUDA version
CUDA_VERSION=$(ssh agent0@192.168.10.29 'nvidia-smi | grep "CUDA Version" | awk "{print \$9}" 2>/dev/null')
if [[ "$CUDA_VERSION" == 12.* ]]; then
    echo "✅ CUDA Version: PASS ($CUDA_VERSION - 12.x series)"
else
    echo "ℹ️  CUDA Version: $CUDA_VERSION (12.x preferred)"
fi

# Check if nvcc is available (CUDA toolkit)
ssh agent0@192.168.10.29 'nvcc --version' && echo "✅ CUDA Toolkit: INSTALLED" || echo "ℹ️  CUDA Toolkit: NOT INSTALLED (may be installed later)"

# Test GPU accessibility
ssh agent0@192.168.10.29 'nvidia-smi -q -d TEMPERATURE' && echo "✅ GPU Access: FUNCTIONAL" || echo "❌ GPU Access: FAILED"
```

## Step 4: GPU Performance Check - hx-llm-server-01
```bash
echo "🔍 Basic GPU performance check on hx-llm-server-01..."

# Check GPU utilization (should be low/idle)
GPU_UTIL=$(ssh agent0@192.168.10.29 'nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits 2>/dev/null | head -1')
echo "ℹ️  Current GPU Utilization: ${GPU_UTIL}%"

# Check GPU temperature
GPU_TEMP=$(ssh agent0@192.168.10.29 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null | head -1')
if [ "$GPU_TEMP" -lt 85 ]; then
    echo "✅ GPU Temperature: NORMAL (${GPU_TEMP}°C < 85°C)"
else
    echo "⚠️  GPU Temperature: HIGH (${GPU_TEMP}°C ≥ 85°C)"
fi

# Check power usage
GPU_POWER=$(ssh agent0@192.168.10.29 'nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | head -1')
echo "ℹ️  Current Power Draw: ${GPU_POWER}W"
```

## Step 5: Repeat for hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Verifying NVIDIA configuration on hx-llm-server-02..."

# Driver verification
ssh agent0@192.168.10.28 'nvidia-smi' && echo "✅ nvidia-smi: FUNCTIONAL" || echo "❌ nvidia-smi: NOT AVAILABLE"
DRIVER_VERSION_02=$(ssh agent0@192.168.10.28 'nvidia-smi --query-gpu=driver_version --format=csv,noheader,nounits 2>/dev/null | head -1')
[[ "$DRIVER_VERSION_02" == 5* ]] && echo "✅ Driver: PASS ($DRIVER_VERSION_02)" || echo "❌ Driver: FAIL ($DRIVER_VERSION_02)"

# GPU detection
GPU_COUNT_02=$(ssh agent0@192.168.10.28 'nvidia-smi -L 2>/dev/null | wc -l')
[ "$GPU_COUNT_02" -ge 2 ] && echo "✅ GPU Count: PASS ($GPU_COUNT_02)" || echo "❌ GPU Count: FAIL ($GPU_COUNT_02)"

# VRAM check
TOTAL_VRAM_02=$(ssh agent0@192.168.10.28 'nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | awk "{sum+=\$1} END {print sum}"')
[ "$TOTAL_VRAM_02" -ge 30000 ] && echo "✅ VRAM: PASS (${TOTAL_VRAM_02}MB)" || echo "❌ VRAM: FAIL (${TOTAL_VRAM_02}MB)"

# CUDA check
CUDA_VERSION_02=$(ssh agent0@192.168.10.28 'nvidia-smi | grep "CUDA Version" | awk "{print \$9}" 2>/dev/null')
echo "ℹ️  CUDA Version: $CUDA_VERSION_02"

# Temperature check
GPU_TEMP_02=$(ssh agent0@192.168.10.28 'nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits 2>/dev/null | head -1')
[ "$GPU_TEMP_02" -lt 85 ] && echo "✅ Temperature: NORMAL (${GPU_TEMP_02}°C)" || echo "⚠️  Temperature: HIGH (${GPU_TEMP_02}°C)"
```

## Step 6: GPU Configuration Report
```bash
echo "📊 Generating GPU configuration report..."

cat > /tmp/gpu-inventory.md << EOF
# GPU Configuration Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **Driver Version**: $DRIVER_VERSION
- **CUDA Version**: $CUDA_VERSION  
- **GPU Count**: $GPU_COUNT devices
- **Total VRAM**: ${TOTAL_VRAM}MB
- **GPU Models**: $(ssh agent0@192.168.10.29 'nvidia-smi -L 2>/dev/null')
- **Current Temperature**: ${GPU_TEMP}°C
- **Current Power**: ${GPU_POWER}W

## hx-llm-server-02 (192.168.10.28)
- **Driver Version**: $DRIVER_VERSION_02
- **CUDA Version**: $CUDA_VERSION_02
- **GPU Count**: $GPU_COUNT_02 devices  
- **Total VRAM**: ${TOTAL_VRAM_02}MB
- **GPU Models**: $(ssh agent0@192.168.10.28 'nvidia-smi -L 2>/dev/null')
- **Current Temperature**: ${GPU_TEMP_02}°C

## Configuration Differences
$([ "$DRIVER_VERSION" != "$DRIVER_VERSION_02" ] && echo "⚠️  Driver versions differ: $DRIVER_VERSION vs $DRIVER_VERSION_02")
$([ "$GPU_COUNT" != "$GPU_COUNT_02" ] && echo "⚠️  GPU counts differ: $GPU_COUNT vs $GPU_COUNT_02")
$([ "$TOTAL_VRAM" != "$TOTAL_VRAM_02" ] && echo "⚠️  VRAM totals differ: ${TOTAL_VRAM}MB vs ${TOTAL_VRAM_02}MB")
EOF

echo "📄 GPU inventory saved to: /tmp/gpu-inventory.md"
cat /tmp/gpu-inventory.md
```

## Validation
Calculate NVIDIA readiness:
- Verify nvidia-smi functional on both servers
- Confirm driver version is 5xx series (570.x preferred)
- Validate GPU count ≥2 per server
- Check total VRAM ≥30GB per server
- Monitor GPU temperatures <85°C
- If all requirements met → Task SUCCESS

## Troubleshooting

**nvidia-smi Not Found:**
```bash
# Check if NVIDIA drivers are installed
ssh agent0@192.168.10.29 'dpkg -l | grep nvidia'

# Check for NVIDIA hardware
ssh agent0@192.168.10.29 'lspci | grep -i nvidia'

# Install NVIDIA drivers if needed
ssh agent0@192.168.10.29 'sudo apt update && sudo apt install -y nvidia-driver-570'
```

**Driver Version Issues:**
```bash
# Check available driver versions
ssh agent0@192.168.10.29 'apt search nvidia-driver'

# Remove old drivers
ssh agent0@192.168.10.29 'sudo apt purge nvidia-* --autoremove'

# Install specific driver version
ssh agent0@192.168.10.29 'sudo apt install -y nvidia-driver-570'
```

**GPU Not Detected:**
```bash
# Check PCI devices
ssh agent0@192.168.10.29 'lspci -v | grep -i nvidia'

# Check kernel modules
ssh agent0@192.168.10.29 'lsmod | grep nvidia'

# Reload NVIDIA modules
ssh agent0@192.168.10.29 'sudo modprobe nvidia'
```

**High GPU Temperature:**
```bash
# Check fan status
ssh agent0@192.168.10.29 'nvidia-smi -q -d FAN'

# Check thermal throttling
ssh agent0@192.168.10.29 'nvidia-smi -q -d PERFORMANCE'

# Monitor continuous temperature
ssh agent0@192.168.10.29 'watch -n 2 nvidia-smi'
```

## Post-Task Checklist
- [ ] nvidia-smi command functional on both servers
- [ ] NVIDIA drivers version 5xx series confirmed
- [ ] GPU detection showing ≥2 devices per server
- [ ] Total VRAM ≥30GB per server verified
- [ ] GPU temperatures within normal range
- [ ] CUDA runtime version compatible
- [ ] GPU configuration documented

## Result Documentation
Document results in format:
```
Task 0.4 Results:
- hx-llm-server-01: nvidia-smi [PASS/FAIL], Driver [PASS/FAIL], GPU Count [PASS/FAIL], VRAM [PASS/FAIL]
- hx-llm-server-02: nvidia-smi [PASS/FAIL], Driver [PASS/FAIL], GPU Count [PASS/FAIL], VRAM [PASS/FAIL]
- GPU Configuration: [READY/NEEDS_ATTENTION]
- Overall: [X/8] checks passed ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Task 0.5: Storage Configuration Validation

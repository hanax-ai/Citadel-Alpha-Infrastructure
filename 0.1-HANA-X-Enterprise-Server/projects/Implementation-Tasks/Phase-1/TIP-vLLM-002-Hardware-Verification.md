# 🔧 Task 0.2: Hardware Specification Verification

**Objective**: Document and verify hardware specifications for enterprise models deployment  
**Duration**: 30 minutes  
**Dependencies**: Task 0.1 (Server Connectivity Validation)  
**Related Models**: DeepSeek-R1-Distill-Qwen-32B, Mixtral-8x7B-Instruct-v0.1, Yi-34B-Chat, openchat-3.5-0106  
**Success Criteria**: Hardware meets enterprise model requirements and is properly documented

## Prerequisites
- [ ] Task 0.1 completed successfully (SSH access confirmed)
- [ ] Both servers accessible via SSH
- [ ] Administrative access to both servers

## Step 1: CPU Verification - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Verifying CPU specifications on hx-llm-server-01..."

# Get CPU information
ssh agent0@192.168.10.29 'lscpu | grep -E "(Model name|CPU\(s\)|Socket|Thread)"'

# Count cores and threads
ssh agent0@192.168.10.29 'nproc && echo "Total cores: $(nproc)"'

# Verify minimum requirement for enterprise models (16+ cores)
# Enterprise models like DeepSeek-R1-Distill-Qwen-32B require significant CPU resources
CORES=$(ssh agent0@192.168.10.29 'nproc')
if [ "$CORES" -ge 16 ]; then
    echo "✅ CPU Cores: PASS ($CORES cores ≥ 16 required for enterprise models)"
else
    echo "❌ CPU Cores: FAIL ($CORES cores < 16 required for enterprise models)"
fi
```

## Step 2: Memory Verification - hx-llm-server-01
```bash
echo "🔍 Verifying memory on hx-llm-server-01..."

# Get memory information
ssh agent0@192.168.10.29 'free -h'

# Check total memory for enterprise models (minimum 128GB)
# Yi-34B-Chat and DeepSeek-R1-Distill-Qwen-32B require substantial memory
MEMORY_GB=$(ssh agent0@192.168.10.29 'free -g | grep "Mem:" | awk "{print \$2}"')
if [ "$MEMORY_GB" -ge 125 ]; then
    echo "✅ Memory: PASS (${MEMORY_GB}GB ≥ 125GB required for enterprise models)"
else
    echo "❌ Memory: FAIL (${MEMORY_GB}GB < 125GB required for enterprise models)"
fi
```

## Step 3: GPU Detection - hx-llm-server-01
```bash
echo "🔍 Verifying GPU configuration on hx-llm-server-01..."

# Check for NVIDIA GPUs
ssh agent0@192.168.10.29 'lspci | grep -i nvidia'

# Count NVIDIA devices
GPU_COUNT=$(ssh agent0@192.168.10.29 'lspci | grep -i nvidia | wc -l')
if [ "$GPU_COUNT" -ge 2 ]; then
    echo "✅ GPU Count: PASS ($GPU_COUNT GPUs ≥ 2 required)"
else
    echo "❌ GPU Count: FAIL ($GPU_COUNT GPUs < 2 required)"
fi

# Check if NVIDIA drivers are installed
ssh agent0@192.168.10.29 'nvidia-smi' && echo "✅ NVIDIA Drivers: PASS" || echo "ℹ️  NVIDIA Drivers: Not installed (expected)"
```

## Step 4: Storage Verification - hx-llm-server-01
```bash
echo "🔍 Verifying storage configuration on hx-llm-server-01..."

# Check disk layout
ssh agent0@192.168.10.29 'lsblk'

# Verify NVMe devices
NVME_COUNT=$(ssh agent0@192.168.10.29 'lsblk | grep nvme | wc -l')
if [ "$NVME_COUNT" -ge 2 ]; then
    echo "✅ NVMe Storage: PASS ($NVME_COUNT NVMe devices ≥ 2 required)"
else
    echo "❌ NVMe Storage: FAIL ($NVME_COUNT NVMe devices < 2 required)"
fi

# Check mounted storage
ssh agent0@192.168.10.29 'df -h | grep -E "(citadel|nvme|sda)"' && echo "✅ Storage Mounts: PASS" || echo "ℹ️  Storage Mounts: Not configured yet"
```

## Step 5: Repeat for hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Verifying hardware specifications on hx-llm-server-02..."

# CPU verification
ssh agent0@192.168.10.28 'lscpu | grep -E "(Model name|CPU\(s\)|Socket|Thread)"'
CORES_02=$(ssh agent0@192.168.10.28 'nproc')
[ "$CORES_02" -ge 16 ] && echo "✅ CPU Cores: PASS ($CORES_02 cores)" || echo "❌ CPU Cores: FAIL ($CORES_02 cores)"

# Memory verification
ssh agent0@192.168.10.28 'free -h'
MEMORY_GB_02=$(ssh agent0@192.168.10.28 'free -g | grep "Mem:" | awk "{print \$2}"')
[ "$MEMORY_GB_02" -ge 125 ] && echo "✅ Memory: PASS (${MEMORY_GB_02}GB)" || echo "❌ Memory: FAIL (${MEMORY_GB_02}GB)"

# GPU verification
ssh agent0@192.168.10.28 'lspci | grep -i nvidia'
GPU_COUNT_02=$(ssh agent0@192.168.10.28 'lspci | grep -i nvidia | wc -l')
[ "$GPU_COUNT_02" -ge 2 ] && echo "✅ GPU Count: PASS ($GPU_COUNT_02 GPUs)" || echo "❌ GPU Count: FAIL ($GPU_COUNT_02 GPUs)"

# Storage verification
ssh agent0@192.168.10.28 'lsblk'
NVME_COUNT_02=$(ssh agent0@192.168.10.28 'lsblk | grep nvme | wc -l')
[ "$NVME_COUNT_02" -ge 2 ] && echo "✅ NVMe Storage: PASS ($NVME_COUNT_02 devices)" || echo "❌ NVMe Storage: FAIL ($NVME_COUNT_02 devices)"
```

## Step 6: Hardware Comparison and Documentation
```bash
echo "📊 Generating hardware comparison report..."

# Create hardware inventory
cat > /tmp/hardware-inventory.md << EOF
# Hardware Inventory Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **CPU**: $(ssh agent0@192.168.10.29 'lscpu | grep "Model name" | sed "s/Model name: *//"')
- **Cores**: $CORES cores
- **Memory**: ${MEMORY_GB}GB total
- **GPUs**: $GPU_COUNT NVIDIA devices
- **NVMe Devices**: $NVME_COUNT detected

## hx-llm-server-02 (192.168.10.28)  
- **CPU**: $(ssh agent0@192.168.10.28 'lscpu | grep "Model name" | sed "s/Model name: *//"')
- **Cores**: $CORES_02 cores
- **Memory**: ${MEMORY_GB_02}GB total
- **GPUs**: $GPU_COUNT_02 NVIDIA devices
- **NVMe Devices**: $NVME_COUNT_02 detected

## Hardware Differences
$(if [ "$CORES" != "$CORES_02" ]; then echo "⚠️  CPU cores differ: $CORES vs $CORES_02"; fi)
$(if [ "$MEMORY_GB" != "$MEMORY_GB_02" ]; then echo "⚠️  Memory differs: ${MEMORY_GB}GB vs ${MEMORY_GB_02}GB"; fi)
$(if [ "$GPU_COUNT" != "$GPU_COUNT_02" ]; then echo "⚠️  GPU count differs: $GPU_COUNT vs $GPU_COUNT_02"; fi)
EOF

echo "📄 Hardware inventory saved to: /tmp/hardware-inventory.md"
cat /tmp/hardware-inventory.md
```

## Validation
Calculate hardware compliance:
- Count PASS results from all hardware checks
- Minimum requirements: CPU ≥16 cores, Memory ≥125GB, GPU ≥2 devices, NVMe ≥2 devices
- If all critical requirements met → Task SUCCESS
- If any critical requirement fails → Review and document limitations

## Troubleshooting

**SSH Connection Issues:**
```bash
# If SSH fails, refer to Task 0.1 troubleshooting
ssh -v agent0@192.168.10.29
```

**Hardware Detection Issues:**
```bash
# Check system information
ssh agent0@192.168.10.29 'dmidecode -t system'

# Verify PCI devices
ssh agent0@192.168.10.29 'lspci -v'

# Check memory details
ssh agent0@192.168.10.29 'dmidecode -t memory | grep Size'
```

**GPU Not Detected:**
```bash
# Check PCI slots
ssh agent0@192.168.10.29 'lspci | grep -i vga'

# Verify NVIDIA devices in PCI
ssh agent0@192.168.10.29 'lspci -d 10de:*'

# Check BIOS/UEFI settings remotely (if IPMI available)
echo "⚠️  May need physical access to verify GPU seating and BIOS settings"
```

## Post-Task Checklist
- [ ] CPU specifications documented for both servers
- [ ] Memory capacity verified (≥125GB each)
- [ ] GPU detection confirmed (≥2 NVIDIA devices each)
- [ ] Storage layout documented (≥2 NVMe devices each)
- [ ] Hardware differences identified and documented
- [ ] All minimum requirements met
- [ ] Hardware inventory report generated

## Result Documentation
Document results in format:
```
Task 0.2 Results:
- hx-llm-server-01: CPU [PASS/FAIL], Memory [PASS/FAIL], GPU [PASS/FAIL], Storage [PASS/FAIL]
- hx-llm-server-02: CPU [PASS/FAIL], Memory [PASS/FAIL], GPU [PASS/FAIL], Storage [PASS/FAIL]
- Hardware Differences: [LIST ANY DIFFERENCES]
- Overall: [X/8] requirements met ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Task 0.3: Operating System Validation

# 🔧 Task 0.5: Storage Configuration Validation

**Objective**: Verify storage mounts and directory structure  
**Duration**: 15 minutes  
**Dependencies**: Task 0.4 (NVIDIA Driver Verification)  
**Success Criteria**: Required mounts accessible, sufficient space available, proper permissions

## Prerequisites
- [ ] Task 0.4 completed successfully (NVIDIA verified)
- [ ] SSH access to both servers
- [ ] Storage devices expected to be configured

## Step 1: Storage Mount Verification - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Checking storage mounts on hx-llm-server-01..."

# Check if citadel-models mount exists
ssh agent0@192.168.10.29 'df -h | grep citadel-models' && echo "✅ Model Storage: MOUNTED" || echo "❌ Model Storage: NOT MOUNTED"

# Check if citadel-backup mount exists  
ssh agent0@192.168.10.29 'df -h | grep citadel-backup' && echo "✅ Backup Storage: MOUNTED" || echo "❌ Backup Storage: NOT MOUNTED"

# Show all mounted filesystems
ssh agent0@192.168.10.29 'df -h'

# Check mount points exist
ssh agent0@192.168.10.29 'ls -la /mnt/' && echo "✅ Mount Points: EXIST" || echo "❌ Mount Points: MISSING"
```

## Step 2: Storage Capacity Check - hx-llm-server-01
```bash
echo "🔍 Verifying storage capacity on hx-llm-server-01..."

# Check model storage capacity
if ssh agent0@192.168.10.29 'mountpoint -q /mnt/citadel-models'; then
    MODEL_CAPACITY=$(ssh agent0@192.168.10.29 'df -BG /mnt/citadel-models | tail -1 | awk "{print \$2}" | sed "s/G//"')
    if [ "$MODEL_CAPACITY" -ge 2000 ]; then
        echo "✅ Model Storage Capacity: PASS (${MODEL_CAPACITY}GB ≥ 2TB)"
    else
        echo "❌ Model Storage Capacity: FAIL (${MODEL_CAPACITY}GB < 2TB)"
    fi
else
    echo "ℹ️  Model Storage: Not mounted yet"
    MODEL_CAPACITY=0
fi

# Check backup storage capacity
if ssh agent0@192.168.10.29 'mountpoint -q /mnt/citadel-backup'; then
    BACKUP_CAPACITY=$(ssh agent0@192.168.10.29 'df -BG /mnt/citadel-backup | tail -1 | awk "{print \$2}" | sed "s/G//"')
    if [ "$BACKUP_CAPACITY" -ge 5000 ]; then
        echo "✅ Backup Storage Capacity: PASS (${BACKUP_CAPACITY}GB ≥ 5TB)"
    else
        echo "❌ Backup Storage Capacity: FAIL (${BACKUP_CAPACITY}GB < 5TB)"
    fi
else
    echo "ℹ️  Backup Storage: Not mounted yet"
    BACKUP_CAPACITY=0
fi
```

## Step 3: Storage Permissions - hx-llm-server-01
```bash
echo "🔍 Checking storage permissions on hx-llm-server-01..."

# Test write access to model storage
if ssh agent0@192.168.10.29 'test -d /mnt/citadel-models'; then
    ssh agent0@192.168.10.29 'touch /mnt/citadel-models/test-write.tmp 2>/dev/null && rm /mnt/citadel-models/test-write.tmp' && echo "✅ Model Storage Write: PASS" || echo "❌ Model Storage Write: FAIL"
else
    echo "ℹ️  Model Storage: Directory not available"
fi

# Test write access to backup storage
if ssh agent0@192.168.10.29 'test -d /mnt/citadel-backup'; then
    ssh agent0@192.168.10.29 'touch /mnt/citadel-backup/test-write.tmp 2>/dev/null && rm /mnt/citadel-backup/test-write.tmp' && echo "✅ Backup Storage Write: PASS" || echo "❌ Backup Storage Write: FAIL"
else
    echo "ℹ️  Backup Storage: Directory not available"
fi

# Check ownership
ssh agent0@192.168.10.29 'ls -la /mnt/' | grep citadel && echo "✅ Storage Ownership: VISIBLE" || echo "ℹ️  Storage Ownership: Check manually"
```

## Step 4: Block Device Detection - hx-llm-server-01
```bash
echo "🔍 Checking block devices on hx-llm-server-01..."

# Show block device layout
ssh agent0@192.168.10.29 'lsblk'

# Count NVMe devices
NVME_COUNT=$(ssh agent0@192.168.10.29 'lsblk | grep nvme | wc -l')
if [ "$NVME_COUNT" -ge 2 ]; then
    echo "✅ NVMe Devices: PASS ($NVME_COUNT devices ≥ 2 required)"
else
    echo "❌ NVMe Devices: FAIL ($NVME_COUNT devices < 2 required)"
fi

# Check for backup drive (SDA or similar)
ssh agent0@192.168.10.29 'lsblk | grep -E "(sda|sdb|sdc)"' && echo "✅ Backup Drive: DETECTED" || echo "ℹ️  Backup Drive: Not detected or different naming"

# Check filesystem types
ssh agent0@192.168.10.29 'mount | grep -E "(citadel|ext4|xfs)"' && echo "✅ Filesystems: DETECTED" || echo "ℹ️  Filesystems: Check configuration"
```

## Step 5: Repeat for hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Verifying storage configuration on hx-llm-server-02..."

# Mount verification
ssh agent0@192.168.10.28 'df -h | grep citadel-models' && echo "✅ Model Storage: MOUNTED" || echo "❌ Model Storage: NOT MOUNTED"
ssh agent0@192.168.10.28 'df -h | grep citadel-backup' && echo "✅ Backup Storage: MOUNTED" || echo "❌ Backup Storage: NOT MOUNTED"

# Capacity check
if ssh agent0@192.168.10.28 'mountpoint -q /mnt/citadel-models'; then
    MODEL_CAPACITY_02=$(ssh agent0@192.168.10.28 'df -BG /mnt/citadel-models | tail -1 | awk "{print \$2}" | sed "s/G//"')
    [ "$MODEL_CAPACITY_02" -ge 2000 ] && echo "✅ Model Capacity: PASS (${MODEL_CAPACITY_02}GB)" || echo "❌ Model Capacity: FAIL (${MODEL_CAPACITY_02}GB)"
else
    MODEL_CAPACITY_02=0
    echo "ℹ️  Model Storage: Not mounted"
fi

if ssh agent0@192.168.10.28 'mountpoint -q /mnt/citadel-backup'; then
    BACKUP_CAPACITY_02=$(ssh agent0@192.168.10.28 'df -BG /mnt/citadel-backup | tail -1 | awk "{print \$2}" | sed "s/G//"')
    [ "$BACKUP_CAPACITY_02" -ge 5000 ] && echo "✅ Backup Capacity: PASS (${BACKUP_CAPACITY_02}GB)" || echo "❌ Backup Capacity: FAIL (${BACKUP_CAPACITY_02}GB)"
else
    BACKUP_CAPACITY_02=0
    echo "ℹ️  Backup Storage: Not mounted"
fi

# Permission check
ssh agent0@192.168.10.28 'test -d /mnt/citadel-models && touch /mnt/citadel-models/test.tmp && rm /mnt/citadel-models/test.tmp' && echo "✅ Model Write: PASS" || echo "❌ Model Write: FAIL"

# Block device check
NVME_COUNT_02=$(ssh agent0@192.168.10.28 'lsblk | grep nvme | wc -l')
[ "$NVME_COUNT_02" -ge 2 ] && echo "✅ NVMe Devices: PASS ($NVME_COUNT_02)" || echo "❌ NVMe Devices: FAIL ($NVME_COUNT_02)"
```

## Step 6: Storage Configuration Report
```bash
echo "📊 Generating storage configuration report..."

cat > /tmp/storage-inventory.md << EOF
# Storage Configuration Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **Model Storage**: $(ssh agent0@192.168.10.29 'mountpoint -q /mnt/citadel-models && echo "MOUNTED (${MODEL_CAPACITY}GB)" || echo "NOT MOUNTED"')
- **Backup Storage**: $(ssh agent0@192.168.10.29 'mountpoint -q /mnt/citadel-backup && echo "MOUNTED (${BACKUP_CAPACITY}GB)" || echo "NOT MOUNTED"')
- **NVMe Devices**: $NVME_COUNT detected
- **Block Layout**: 
$(ssh agent0@192.168.10.29 'lsblk | head -10')

## hx-llm-server-02 (192.168.10.28)
- **Model Storage**: $(ssh agent0@192.168.10.28 'mountpoint -q /mnt/citadel-models && echo "MOUNTED (${MODEL_CAPACITY_02}GB)" || echo "NOT MOUNTED"')
- **Backup Storage**: $(ssh agent0@192.168.10.28 'mountpoint -q /mnt/citadel-backup && echo "MOUNTED (${BACKUP_CAPACITY_02}GB)" || echo "NOT MOUNTED"')
- **NVMe Devices**: $NVME_COUNT_02 detected

## Storage Readiness
- Model storage available: $([ "$MODEL_CAPACITY" -gt 0 ] && [ "$MODEL_CAPACITY_02" -gt 0 ] && echo "✅ BOTH SERVERS" || echo "❌ NEEDS CONFIGURATION")
- Backup storage available: $([ "$BACKUP_CAPACITY" -gt 0 ] && [ "$BACKUP_CAPACITY_02" -gt 0 ] && echo "✅ BOTH SERVERS" || echo "❌ NEEDS CONFIGURATION")
- Hardware requirements: $([ "$NVME_COUNT" -ge 2 ] && [ "$NVME_COUNT_02" -ge 2 ] && echo "✅ MET" || echo "❌ INSUFFICIENT")
EOF

echo "📄 Storage inventory saved to: /tmp/storage-inventory.md"
cat /tmp/storage-inventory.md
```

## Validation
Calculate storage readiness:
- Verify mount points accessible (/mnt/citadel-models, /mnt/citadel-backup)
- Confirm adequate capacity (≥2TB models, ≥5TB backup per server)
- Validate write permissions for agent0 user
- Check hardware availability (≥2 NVMe devices per server)
- If all requirements met → Task SUCCESS
- If storage not configured → Document current state and proceed

## Troubleshooting

**Mount Points Missing:**
```bash
# Create mount point directories
ssh agent0@192.168.10.29 'sudo mkdir -p /mnt/citadel-models /mnt/citadel-backup'

# Check fstab entries
ssh agent0@192.168.10.29 'cat /etc/fstab | grep citadel'

# List available block devices
ssh agent0@192.168.10.29 'sudo fdisk -l'
```

**Permission Issues:**
```bash
# Check current ownership
ssh agent0@192.168.10.29 'ls -la /mnt/'

# Fix ownership if needed
ssh agent0@192.168.10.29 'sudo chown -R agent0:agent0 /mnt/citadel-*'

# Fix permissions if needed
ssh agent0@192.168.10.29 'sudo chmod 755 /mnt/citadel-*'
```

**Storage Not Mounted:**
```bash
# Check available devices
ssh agent0@192.168.10.29 'lsblk -f'

# Check if devices need formatting
ssh agent0@192.168.10.29 'sudo blkid'

# Manual mount attempt
ssh agent0@192.168.10.29 'sudo mount -a'
```

**Insufficient Capacity:**
```bash
# Check disk usage details
ssh agent0@192.168.10.29 'df -h'

# Check block device sizes
ssh agent0@192.168.10.29 'lsblk -b'

# Check partition table
ssh agent0@192.168.10.29 'sudo parted -l'
```

## Post-Task Checklist
- [ ] Model storage mount points verified on both servers
- [ ] Backup storage mount points verified on both servers
- [ ] Storage capacity meets minimum requirements
- [ ] Write permissions functional for agent0 user
- [ ] Block devices properly detected
- [ ] Storage configuration documented

## Result Documentation
Document results in format:
```
Task 0.5 Results:
- hx-llm-server-01: Model Storage [MOUNTED/MISSING], Backup Storage [MOUNTED/MISSING], Capacity [PASS/FAIL], Permissions [PASS/FAIL]
- hx-llm-server-02: Model Storage [MOUNTED/MISSING], Backup Storage [MOUNTED/MISSING], Capacity [PASS/FAIL], Permissions [PASS/FAIL]
- Storage Readiness: [READY/NEEDS_CONFIGURATION]
- Overall: [X/8] checks passed ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Task 1.1: Configuration Management System Deployment

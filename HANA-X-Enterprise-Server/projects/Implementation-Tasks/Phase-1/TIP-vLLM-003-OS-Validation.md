# 🔧 Task 0.3: Operating System Validation

**Objective**: Verify Ubuntu 24.04 LTS installation and configuration  
**Duration**: 20 minutes  
**Dependencies**: Task 0.2 (Hardware Specification Verification)  
**Success Criteria**: OS version confirmed, system updates current, required packages available

## Prerequisites
- [ ] Task 0.2 completed successfully (Hardware verified)
- [ ] SSH access to both servers confirmed
- [ ] Administrative privileges available

## Step 1: OS Version Verification - hx-llm-server-01 (192.168.10.29)
```bash
echo "🔍 Verifying OS version on hx-llm-server-01..."

# Check Ubuntu version
ssh agent0@192.168.10.29 'lsb_release -a'

# Verify Ubuntu 24.04 LTS specifically
OS_VERSION=$(ssh agent0@192.168.10.29 'lsb_release -rs')
if [ "$OS_VERSION" = "24.04" ]; then
    echo "✅ OS Version: PASS (Ubuntu $OS_VERSION LTS)"
else
    echo "❌ OS Version: FAIL (Ubuntu $OS_VERSION, expected 24.04)"
fi

# Check kernel version
ssh agent0@192.168.10.29 'uname -r' && echo "✅ Kernel: DETECTED" || echo "❌ Kernel: FAILED"
```

## Step 2: System Updates Status - hx-llm-server-01
```bash
echo "🔍 Checking system updates on hx-llm-server-01..."

# Check for available updates
ssh agent0@192.168.10.29 'apt list --upgradable 2>/dev/null | wc -l'

# Update package lists
ssh agent0@192.168.10.29 'sudo apt update' && echo "✅ Package Lists: UPDATED" || echo "❌ Package Lists: FAILED"

# Check upgradable packages count
UPGRADABLE=$(ssh agent0@192.168.10.29 'apt list --upgradable 2>/dev/null | tail -n +2 | wc -l')
if [ "$UPGRADABLE" -eq 0 ]; then
    echo "✅ System Updates: PASS (System up to date)"
else
    echo "ℹ️  System Updates: $UPGRADABLE packages available for upgrade"
fi
```

## Step 3: Essential Packages Verification - hx-llm-server-01
```bash
echo "🔍 Verifying essential packages on hx-llm-server-01..."

# Check for required packages
REQUIRED_PACKAGES="curl wget git vim build-essential python3 python3-pip"

for package in $REQUIRED_PACKAGES; do
    if ssh agent0@192.168.10.29 "dpkg -l | grep -q \"^ii  $package \""; then
        echo "✅ Package $package: INSTALLED"
    else
        echo "❌ Package $package: NOT INSTALLED"
    fi
done

# Check Python version
PYTHON_VERSION=$(ssh agent0@192.168.10.29 'python3 --version 2>/dev/null | cut -d" " -f2')
if [[ "$PYTHON_VERSION" == 3.12* ]]; then
    echo "✅ Python Version: PASS ($PYTHON_VERSION)"
else
    echo "ℹ️  Python Version: $PYTHON_VERSION (3.12.x preferred)"
fi
```

## Step 4: User Permissions Verification - hx-llm-server-01
```bash
echo "🔍 Verifying user permissions on hx-llm-server-01..."

# Check if agent0 user exists and has sudo access
ssh agent0@192.168.10.29 'id agent0' && echo "✅ User agent0: EXISTS" || echo "❌ User agent0: NOT FOUND"

# Test sudo access
ssh agent0@192.168.10.29 'sudo -n whoami 2>/dev/null' && echo "✅ Sudo Access: PASS" || echo "ℹ️  Sudo Access: Requires password"

# Check user groups
USER_GROUPS=$(ssh agent0@192.168.10.29 'groups agent0')
echo "ℹ️  User Groups: $USER_GROUPS"

# Verify sudo group membership
if ssh agent0@192.168.10.29 'groups agent0 | grep -q sudo'; then
    echo "✅ Sudo Group: PASS (agent0 in sudo group)"
else
    echo "❌ Sudo Group: FAIL (agent0 not in sudo group)"
fi
```

## Step 5: System Services Status - hx-llm-server-01
```bash
echo "🔍 Checking critical system services on hx-llm-server-01..."

# Check SSH service
ssh agent0@192.168.10.29 'systemctl is-active ssh' && echo "✅ SSH Service: ACTIVE" || echo "❌ SSH Service: INACTIVE"

# Check network service
ssh agent0@192.168.10.29 'systemctl is-active systemd-networkd' && echo "✅ Network Service: ACTIVE" || echo "ℹ️  Network Service: Using alternative"

# Check time synchronization
ssh agent0@192.168.10.29 'timedatectl status | grep "NTP service"' && echo "✅ Time Sync: ACTIVE" || echo "ℹ️  Time Sync: Check status"

# Check disk usage
DISK_USAGE=$(ssh agent0@192.168.10.29 'df / | tail -1 | awk "{print \$(NF-1)}" | sed "s/%//"')
if [ "$DISK_USAGE" -lt 80 ]; then
    echo "✅ Disk Usage: PASS (${DISK_USAGE}% < 80%)"
else
    echo "⚠️  Disk Usage: WARNING (${DISK_USAGE}% ≥ 80%)"
fi
```

## Step 6: Repeat for hx-llm-server-02 (192.168.10.28)
```bash
echo "🔍 Verifying OS configuration on hx-llm-server-02..."

# OS Version verification
OS_VERSION_02=$(ssh agent0@192.168.10.28 'lsb_release -rs')
[ "$OS_VERSION_02" = "24.04" ] && echo "✅ OS Version: PASS (Ubuntu $OS_VERSION_02)" || echo "❌ OS Version: FAIL (Ubuntu $OS_VERSION_02)"

# System updates check
ssh agent0@192.168.10.28 'sudo apt update' && echo "✅ Package Lists: UPDATED" || echo "❌ Package Lists: FAILED"
UPGRADABLE_02=$(ssh agent0@192.168.10.28 'apt list --upgradable 2>/dev/null | tail -n +2 | wc -l')
[ "$UPGRADABLE_02" -eq 0 ] && echo "✅ System Updates: CURRENT" || echo "ℹ️  System Updates: $UPGRADABLE_02 available"

# Essential packages check
for package in curl wget git vim build-essential python3 python3-pip; do
    ssh agent0@192.168.10.28 "dpkg -l | grep -q \"^ii  $package \"" && echo "✅ $package: INSTALLED" || echo "❌ $package: MISSING"
done

# User permissions check
ssh agent0@192.168.10.28 'sudo -n whoami 2>/dev/null' && echo "✅ Sudo Access: PASS" || echo "ℹ️  Sudo Access: Requires password"
ssh agent0@192.168.10.28 'groups agent0 | grep -q sudo' && echo "✅ Sudo Group: PASS" || echo "❌ Sudo Group: FAIL"

# Services check
ssh agent0@192.168.10.28 'systemctl is-active ssh' && echo "✅ SSH Service: ACTIVE" || echo "❌ SSH Service: INACTIVE"
DISK_USAGE_02=$(ssh agent0@192.168.10.28 'df / | tail -1 | awk "{print \$(NF-1)}" | sed "s/%//"')
[ "$DISK_USAGE_02" -lt 80 ] && echo "✅ Disk Usage: PASS (${DISK_USAGE_02}%)" || echo "⚠️  Disk Usage: WARNING (${DISK_USAGE_02}%)"
```

## Step 7: OS Configuration Documentation
```bash
echo "📊 Generating OS configuration report..."

# Create OS inventory
cat > /tmp/os-inventory.md << EOF
# OS Configuration Report - $(date)

## hx-llm-server-01 (192.168.10.29)
- **OS**: $(ssh agent0@192.168.10.29 'lsb_release -ds')
- **Kernel**: $(ssh agent0@192.168.10.29 'uname -r')
- **Uptime**: $(ssh agent0@192.168.10.29 'uptime -p')
- **Python**: $(ssh agent0@192.168.10.29 'python3 --version 2>/dev/null || echo "Not available"')
- **Disk Usage**: ${DISK_USAGE}% root filesystem
- **Updates Available**: $UPGRADABLE packages

## hx-llm-server-02 (192.168.10.28)
- **OS**: $(ssh agent0@192.168.10.28 'lsb_release -ds')
- **Kernel**: $(ssh agent0@192.168.10.28 'uname -r')
- **Uptime**: $(ssh agent0@192.168.10.28 'uptime -p')
- **Python**: $(ssh agent0@192.168.10.28 'python3 --version 2>/dev/null || echo "Not available"')
- **Disk Usage**: ${DISK_USAGE_02}% root filesystem
- **Updates Available**: $UPGRADABLE_02 packages

## System Readiness
- Both servers running Ubuntu 24.04 LTS: $([ "$OS_VERSION" = "24.04" ] && [ "$OS_VERSION_02" = "24.04" ] && echo "✅ YES" || echo "❌ NO")
- Essential packages installed: $(echo "Verify in detailed logs above")
- User permissions configured: $(echo "Verify sudo access above")
- Services operational: $(echo "Check SSH and system services")
EOF

echo "📄 OS inventory saved to: /tmp/os-inventory.md"
cat /tmp/os-inventory.md
```

## Validation
Calculate OS readiness:
- Verify Ubuntu 24.04 LTS on both servers
- Confirm essential packages are installed
- Validate user permissions and sudo access
- Check system services are running
- If all requirements met → Task SUCCESS
- If critical requirements missing → Document gaps and proceed with caution

## Troubleshooting

**Wrong OS Version:**
```bash
# Check detailed version information
ssh agent0@192.168.10.29 'cat /etc/os-release'

# Verify this is actually Ubuntu
ssh agent0@192.168.10.29 'cat /etc/issue'

# Check if upgrade is possible
ssh agent0@192.168.10.29 'sudo do-release-upgrade -c'
```

**Package Installation Issues:**
```bash
# Fix broken packages
ssh agent0@192.168.10.29 'sudo apt --fix-broken install'

# Update package cache
ssh agent0@192.168.10.29 'sudo apt update && sudo apt upgrade'

# Install missing essential packages
ssh agent0@192.168.10.29 'sudo apt install -y curl wget git vim build-essential python3 python3-pip'
```

**User Permission Issues:**
```bash
# Add user to sudo group
ssh agent0@192.168.10.29 'sudo usermod -aG sudo agent0'

# Verify sudoers file
ssh agent0@192.168.10.29 'sudo visudo -c'

# Test sudo access
ssh agent0@192.168.10.29 'sudo whoami'
```

**Service Issues:**
```bash
# Check service status
ssh agent0@192.168.10.29 'sudo systemctl status ssh'

# Start/restart services
ssh agent0@192.168.10.29 'sudo systemctl restart ssh'

# Check service logs
ssh agent0@192.168.10.29 'sudo journalctl -u ssh -n 20'
```

## Post-Task Checklist
- [ ] Ubuntu 24.04 LTS confirmed on both servers
- [ ] System packages updated to latest versions
- [ ] Essential packages installed and verified
- [ ] User permissions configured correctly
- [ ] Critical system services running
- [ ] Disk usage within acceptable limits
- [ ] OS configuration documented

## Result Documentation
Document results in format:
```
Task 0.3 Results:
- hx-llm-server-01: OS [PASS/FAIL], Updates [CURRENT/PENDING], Packages [PASS/FAIL], Permissions [PASS/FAIL]
- hx-llm-server-02: OS [PASS/FAIL], Updates [CURRENT/PENDING], Packages [PASS/FAIL], Permissions [PASS/FAIL]
- System Readiness: [READY/NEEDS_ATTENTION]
- Overall: [X/8] checks passed ([X]%)
- Status: [SUCCESS/FAILED]
```

**Next Step**: If successful, proceed to Task 0.4: NVIDIA Driver Verification

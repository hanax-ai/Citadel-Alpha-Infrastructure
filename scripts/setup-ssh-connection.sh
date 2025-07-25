#!/bin/bash
# SSH Setup Script for HX-Server-02 to Metrics Server Connection
# This script fixes SSH connection issues for monitoring deployment

echo "🔧 SSH Connection Setup for HX-Server-02"
echo "========================================"
echo "Target: 192.168.10.37 (Metrics Server)"
echo "User: agent0"
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "❌ SSH key not found. Generating new key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N "" -C "agent0@hx-server-02"
    echo "✅ SSH key generated successfully"
else
    echo "✅ SSH key already exists"
fi

# Display public key
echo ""
echo "📋 Public Key (copy this to the metrics server):"
echo "================================================"
cat ~/.ssh/id_rsa.pub
echo "================================================"
echo ""

# Check host key
echo "🔍 Checking host key for 192.168.10.37..."
if ssh-keygen -F 192.168.10.37 >/dev/null 2>&1; then
    echo "✅ Host key already in known_hosts"
else
    echo "📝 Adding host key to known_hosts..."
    ssh-keyscan -H 192.168.10.37 >> ~/.ssh/known_hosts
    echo "✅ Host key added"
fi

# Test connection
echo ""
echo "🧪 Testing SSH connection..."
if ssh -o ConnectTimeout=5 -o BatchMode=yes agent0@192.168.10.37 "echo 'SSH connection successful'" 2>/dev/null; then
    echo "✅ SSH connection working!"
    echo ""
    echo "🎯 SSH Setup Complete!"
    echo "The monitoring deployment scripts can now run successfully."
else
    echo "⚠️  SSH connection still failing."
    echo ""
    echo "📋 Manual Steps Required:"
    echo "1. Copy the public key above"
    echo "2. Log into the metrics server (192.168.10.37)"
    echo "3. Run: mkdir -p ~/.ssh && chmod 700 ~/.ssh"
    echo "4. Add the public key to ~/.ssh/authorized_keys"
    echo "5. Run: chmod 600 ~/.ssh/authorized_keys"
    echo ""
    echo "Alternative one-liner (run on metrics server):"
    echo "ssh-copy-id agent0@192.168.10.37"
fi

echo ""
echo "🔧 SSH Setup Script Completed"

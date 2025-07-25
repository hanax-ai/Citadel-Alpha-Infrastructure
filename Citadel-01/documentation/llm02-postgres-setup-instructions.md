#!/bin/bash

# Manual Setup Instructions for LLM-02 PostgreSQL Configuration
# Run these commands on 192.168.10.36 (llm-02)

echo "=== PostgreSQL Configuration Setup for LLM-02 ==="
echo "Run these commands on llm-02 (192.168.10.36):"
echo
echo "1. Create directory structure:"
echo "   sudo mkdir -p /opt/citadel/config/secrets"
echo "   sudo chown -R agent0:agent0 /opt/citadel"
echo
echo "2. Move configuration file:"
echo "   mv ~/database-credentials.yaml /opt/citadel/config/secrets/"
echo "   chmod 600 /opt/citadel/config/secrets/database-credentials.yaml"
echo
echo "3. Test PostgreSQL connection:"
echo '   PGPASSWORD="CitadelLLM#2025\$SecurePass!" psql -h 192.168.10.35 -p 5432 -U citadel_llm_user -d citadel_llm_db -c "SELECT current_database(), current_user;"'
echo
echo "4. Verify configuration:"
echo "   cat /opt/citadel/config/secrets/database-credentials.yaml"
echo
echo "=== Configuration Details ==="
echo "Database Host: 192.168.10.35"
echo "Database Port: 5432 (Direct PostgreSQL - NOT Pgpool-II)"
echo "Database Name: citadel_llm_db"
echo "Username: citadel_llm_user"
echo "Password: CitadelLLM#2025\$SecurePass!"
echo
echo "✅ File already copied to llm-02:~/database-credentials.yaml"
echo "🔧 Complete the manual steps above on llm-02"

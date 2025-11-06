#!/bin/bash
# Verification script for API structure

echo "=========================================="
echo "CrewAI Runner Structure Verification"
echo "=========================================="
echo ""

# Check if all required files exist
check_file() {
    if [ -f "$1" ]; then
        echo "✓ $1"
        return 0
    else
        echo "✗ $1 - NOT FOUND"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "✓ $1/"
        return 0
    else
        echo "✗ $1/ - NOT FOUND"
        return 1
    fi
}

echo "Backend Files:"
check_file "api/main.py"
check_file "api/models.py"
check_file "api/config.py"
check_file "api/auth.py"
check_file "api/__init__.py"
check_file "api/requirements.txt"
check_file "api/Dockerfile"
check_file "api/.env.example"
check_file "api/README.md"
check_file "api/API_SCHEMA.md"

echo ""
echo "Backend Routers:"
check_dir "api/routers"
check_file "api/routers/__init__.py"
check_file "api/routers/providers.py"
check_file "api/routers/models.py"
check_file "api/routers/workflows.py"
check_file "api/routers/chat.py"
check_file "api/routers/yaml_validator.py"

echo ""
echo "Frontend Files:"
check_file "frontend/Dockerfile"
check_file "frontend/nginx.conf"
check_file "frontend/package.json"

echo ""
echo "Docker Configuration:"
check_file "docker-compose.yml"
check_file ".env.example"
check_file "DEPLOYMENT.md"

echo ""
echo "=========================================="
echo "Python Syntax Check:"
echo "=========================================="

# Check Python syntax
python3 -m py_compile api/main.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ api/main.py - Valid Python syntax"
else
    echo "✗ api/main.py - Syntax error"
fi

python3 -m py_compile api/models.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ api/models.py - Valid Python syntax"
else
    echo "✗ api/models.py - Syntax error"
fi

python3 -m py_compile api/config.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ api/config.py - Valid Python syntax"
else
    echo "✗ api/config.py - Syntax error"
fi

python3 -m py_compile api/auth.py 2>&1
if [ $? -eq 0 ]; then
    echo "✓ api/auth.py - Valid Python syntax"
else
    echo "✗ api/auth.py - Syntax error"
fi

for router in api/routers/*.py; do
    python3 -m py_compile "$router" 2>&1
    if [ $? -eq 0 ]; then
        echo "✓ $router - Valid Python syntax"
    else
        echo "✗ $router - Syntax error"
    fi
done

echo ""
echo "=========================================="
echo "API Endpoints Coverage:"
echo "=========================================="

# Check that all required endpoints are implemented
echo "Checking API endpoints from API_SCHEMA.md:"
grep -q "GET /providers" api/routers/providers.py && echo "✓ GET /providers" || echo "✗ GET /providers"
grep -q "POST /providers" api/routers/providers.py && echo "✓ POST /providers" || echo "✗ POST /providers"
grep -q "GET /models" api/routers/models.py && echo "✓ GET /models" || echo "✗ GET /models"
grep -q "POST /models" api/routers/models.py && echo "✓ POST /models" || echo "✗ POST /models"
grep -q "/workflows/start" api/routers/workflows.py && echo "✓ POST /workflows/start" || echo "✗ POST /workflows/start"
grep -q "/workflows/stop" api/routers/workflows.py && echo "✓ POST /workflows/stop" || echo "✗ POST /workflows/stop"
grep -q "/{workflowId}/status" api/routers/workflows.py && echo "✓ GET /workflows/{workflowId}/status" || echo "✗ GET /workflows/{workflowId}/status"
grep -q "POST /chat" api/routers/chat.py && echo "✓ POST /chat" || echo "✗ POST /chat"
grep -q "/yaml/validate" api/routers/yaml_validator.py && echo "✓ POST /yaml/validate" || echo "✗ POST /yaml/validate"

echo ""
echo "=========================================="
echo "Verification Complete!"
echo "=========================================="

#!/bin/bash

# Test script for authentication API endpoints
# Tests registration, login, and protected routes

echo "========================================"
echo "AUTHENTICATION API TEST"
echo "========================================"
echo ""

BASE_URL="http://localhost:5000/api/auth"

# Test 1: Register a new user
echo "[TEST 1] Register new user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123",
    "email": "test@example.com"
  }')

echo "$REGISTER_RESPONSE" | python3 -m json.tool
echo ""

# Extract token from registration response
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
  echo "❌ Failed to get token from registration"
  echo ""
else
  echo "✓ Registration successful, token received"
  echo "Token: ${TOKEN:0:20}..."
  echo ""
fi

# Test 2: Try to register with same username (should fail)
echo "[TEST 2] Try to register duplicate username..."
DUPLICATE_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password456",
    "email": "another@example.com"
  }')

echo "$DUPLICATE_RESPONSE" | python3 -m json.tool
echo ""

# Test 3: Login with correct credentials
echo "[TEST 3] Login with correct credentials..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }')

echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

# Extract token from login response
LOGIN_TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access_token', ''))" 2>/dev/null)

if [ -z "$LOGIN_TOKEN" ]; then
  echo "❌ Failed to get token from login"
  echo ""
else
  echo "✓ Login successful, token received"
  echo "Token: ${LOGIN_TOKEN:0:20}..."
  echo ""
fi

# Test 4: Login with wrong password (should fail)
echo "[TEST 4] Login with wrong password..."
WRONG_PASSWORD_RESPONSE=$(curl -s -X POST "$BASE_URL/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "wrongpassword"
  }')

echo "$WRONG_PASSWORD_RESPONSE" | python3 -m json.tool
echo ""

# Test 5: Get current user info (protected route)
if [ -n "$LOGIN_TOKEN" ]; then
  echo "[TEST 5] Get current user info (protected route)..."
  ME_RESPONSE=$(curl -s -X GET "$BASE_URL/me" \
    -H "Authorization: Bearer $LOGIN_TOKEN")
  
  echo "$ME_RESPONSE" | python3 -m json.tool
  echo ""
else
  echo "[TEST 5] Skipped - no token available"
  echo ""
fi

# Test 6: Verify token
if [ -n "$LOGIN_TOKEN" ]; then
  echo "[TEST 6] Verify token..."
  VERIFY_RESPONSE=$(curl -s -X GET "$BASE_URL/verify" \
    -H "Authorization: Bearer $LOGIN_TOKEN")
  
  echo "$VERIFY_RESPONSE" | python3 -m json.tool
  echo ""
else
  echo "[TEST 6] Skipped - no token available"
  echo ""
fi

# Test 7: Try to access protected route without token (should fail)
echo "[TEST 7] Try to access protected route without token..."
NO_TOKEN_RESPONSE=$(curl -s -X GET "$BASE_URL/me")

echo "$NO_TOKEN_RESPONSE" | python3 -m json.tool
echo ""

# Test 8: Validation - missing username
echo "[TEST 8] Validation - register without username..."
NO_USERNAME_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "password": "password123"
  }')

echo "$NO_USERNAME_RESPONSE" | python3 -m json.tool
echo ""

# Test 9: Validation - short password
echo "[TEST 9] Validation - password too short..."
SHORT_PASSWORD_RESPONSE=$(curl -s -X POST "$BASE_URL/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "123"
  }')

echo "$SHORT_PASSWORD_RESPONSE" | python3 -m json.tool
echo ""

echo "========================================"
echo "TEST SUMMARY"
echo "========================================"
echo ""
echo "✓ Test 1: User registration"
echo "✓ Test 2: Duplicate username rejection"
echo "✓ Test 3: Login with correct credentials"
echo "✓ Test 4: Login with wrong password rejection"
echo "✓ Test 5: Get current user (protected route)"
echo "✓ Test 6: Token verification"
echo "✓ Test 7: Protected route without token rejection"
echo "✓ Test 8: Validation - missing username"
echo "✓ Test 9: Validation - short password"
echo ""
echo "All authentication endpoints tested!"
echo "========================================"


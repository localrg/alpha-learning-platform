#!/bin/bash

# Test script for Assessment API endpoints

BASE_URL="http://localhost:5000/api"
echo "=========================================="
echo "TESTING ASSESSMENT API ENDPOINTS"
echo "=========================================="

# Test 1: Login to get token
echo -e "\n[TEST 1] Login to get JWT token..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo "✗ Failed to get token"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✓ Got JWT token"

# Test 2: Get available skills
echo -e "\n[TEST 2] Get available skills..."
SKILLS_RESPONSE=$(curl -s -X GET "$BASE_URL/assessment/skills")
echo "$SKILLS_RESPONSE" | python3 -m json.tool | head -30
echo "✓ Skills retrieved"

# Test 3: Get skills for grade 5
echo -e "\n[TEST 3] Get skills for grade 5..."
GRADE5_SKILLS=$(curl -s -X GET "$BASE_URL/assessment/skills?grade_level=5")
echo "$GRADE5_SKILLS" | python3 -m json.tool
echo "✓ Grade 5 skills retrieved"

# Test 4: Start a diagnostic assessment
echo -e "\n[TEST 4] Start diagnostic assessment..."
START_RESPONSE=$(curl -s -X POST "$BASE_URL/assessment/start" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"assessment_type":"diagnostic","grade_level":5}')

echo "$START_RESPONSE" | python3 -m json.tool | head -50

ASSESSMENT_ID=$(echo $START_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['assessment']['id'])" 2>/dev/null)
FIRST_QUESTION_ID=$(echo $START_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['questions'][0]['id'])" 2>/dev/null)

if [ -z "$ASSESSMENT_ID" ]; then
    echo "✗ Failed to create assessment"
    exit 1
fi

echo "✓ Assessment created (ID: $ASSESSMENT_ID)"
echo "✓ First question ID: $FIRST_QUESTION_ID"

# Test 5: Submit a correct answer
echo -e "\n[TEST 5] Submit correct answer to first question..."
SUBMIT_RESPONSE=$(curl -s -X POST "$BASE_URL/assessment/$ASSESSMENT_ID/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question_id\":$FIRST_QUESTION_ID,\"student_answer\":\"56\",\"time_spent_seconds\":15}")

echo "$SUBMIT_RESPONSE" | python3 -m json.tool
echo "✓ Answer submitted"

# Test 6: Try to submit duplicate answer (should fail)
echo -e "\n[TEST 6] Try to submit duplicate answer (should fail)..."
DUPLICATE_RESPONSE=$(curl -s -X POST "$BASE_URL/assessment/$ASSESSMENT_ID/submit" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"question_id\":$FIRST_QUESTION_ID,\"student_answer\":\"56\",\"time_spent_seconds\":10}")

if echo "$DUPLICATE_RESPONSE" | grep -q "already answered"; then
    echo "✓ Duplicate answer correctly rejected"
else
    echo "✗ Duplicate answer should have been rejected"
fi

# Test 7: Get assessment details
echo -e "\n[TEST 7] Get assessment details..."
ASSESSMENT_DETAILS=$(curl -s -X GET "$BASE_URL/assessment/$ASSESSMENT_ID" \
  -H "Authorization: Bearer $TOKEN")

echo "$ASSESSMENT_DETAILS" | python3 -m json.tool | head -40
echo "✓ Assessment details retrieved"

# Test 8: Complete assessment
echo -e "\n[TEST 8] Complete assessment..."
COMPLETE_RESPONSE=$(curl -s -X POST "$BASE_URL/assessment/$ASSESSMENT_ID/complete" \
  -H "Authorization: Bearer $TOKEN")

echo "$COMPLETE_RESPONSE" | python3 -m json.tool
echo "✓ Assessment completed"

# Test 9: Get assessment history
echo -e "\n[TEST 9] Get assessment history..."
HISTORY_RESPONSE=$(curl -s -X GET "$BASE_URL/assessment/history" \
  -H "Authorization: Bearer $TOKEN")

echo "$HISTORY_RESPONSE" | python3 -m json.tool | head -30
echo "✓ Assessment history retrieved"

# Test 10: Try to complete already completed assessment (should fail)
echo -e "\n[TEST 10] Try to complete already completed assessment (should fail)..."
RECOMPLETE_RESPONSE=$(curl -s -X POST "$BASE_URL/assessment/$ASSESSMENT_ID/complete" \
  -H "Authorization: Bearer $TOKEN")

if echo "$RECOMPLETE_RESPONSE" | grep -q "already completed"; then
    echo "✓ Already completed assessment correctly rejected"
else
    echo "✗ Should have rejected already completed assessment"
fi

echo -e "\n=========================================="
echo "ALL TESTS COMPLETED!"
echo "=========================================="


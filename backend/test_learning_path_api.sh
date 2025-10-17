#!/bin/bash

echo "=== Testing Learning Path API ==="
echo ""

# Login and get token
echo "[TEST 1] Login and get JWT token..."
LOGIN_RESPONSE=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"password123"}')

TOKEN=$(echo $LOGIN_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
echo "✓ Token received"
echo ""

# Start a new assessment
echo "[TEST 2] Start diagnostic assessment..."
ASSESSMENT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/assessment/start \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"assessment_type":"diagnostic"}')

ASSESSMENT_ID=$(echo $ASSESSMENT_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['assessment']['id'])")
echo "✓ Assessment started (ID: $ASSESSMENT_ID)"
echo ""

# Submit some answers (mix of correct and incorrect)
echo "[TEST 3] Submitting assessment answers..."
QUESTIONS=$(echo $ASSESSMENT_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); [print(q['id']) for q in data['questions']]")

# Submit answers for first 5 questions (simulate some wrong answers)
QUESTION_IDS=($QUESTIONS)
for i in {0..4}; do
    QID=${QUESTION_IDS[$i]}
    # Alternate between correct and incorrect
    if [ $((i % 2)) -eq 0 ]; then
        ANSWER="wrong_answer"
    else
        ANSWER=$(echo $ASSESSMENT_RESPONSE | python3 -c "import sys, json; data=json.load(sys.stdin); q=[q for q in data['questions'] if q['id']==$QID][0]; print(q['options'][0])")
    fi
    
    curl -s -X POST http://localhost:5000/api/assessment/$ASSESSMENT_ID/submit \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $TOKEN" \
      -d "{\"question_id\":$QID,\"student_answer\":\"$ANSWER\",\"time_spent_seconds\":10}" > /dev/null
done
echo "✓ Submitted 5 answers"
echo ""

# Complete the assessment
echo "[TEST 4] Completing assessment..."
COMPLETE_RESPONSE=$(curl -s -X POST http://localhost:5000/api/assessment/$ASSESSMENT_ID/complete \
  -H "Authorization: Bearer $TOKEN")
echo "✓ Assessment completed"
echo "Score: $(echo $COMPLETE_RESPONSE | python3 -c "import sys, json; print(json.load(sys.stdin)['assessment']['score_percentage'])")%"
echo ""

# Generate learning path
echo "[TEST 5] Generating learning path from assessment..."
LEARNING_PATH_RESPONSE=$(curl -s -X POST http://localhost:5000/api/learning-path/generate/$ASSESSMENT_ID \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Learning path generated"
echo "$LEARNING_PATH_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Student: {data['student_name']}\")
print(f\"Assessment Score: {data['assessment_score']}%\")
print(f\"Skills to Master: {data['total_skills_to_master']}\")
print(f\"\nLearning Path:\")
for item in data['learning_path']:
    print(f\"  - {item['skill_name']} (Accuracy: {item['current_accuracy']}%)\")
print(f\"\nRecommendations:\")
for rec in data['recommendations']:
    print(f\"  - {rec['message']}\")
"
echo ""

# Get current learning path
echo "[TEST 6] Getting current learning path..."
CURRENT_PATH=$(curl -s -X GET http://localhost:5000/api/learning-path/current \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Current learning path retrieved"
echo "$CURRENT_PATH" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print(f\"Total Skills: {data['total_skills']}\")
print(f\"Mastered: {data['mastered']}\")
print(f\"In Progress: {data['in_progress']}\")
print(f\"Not Started: {data['not_started']}\")
"
echo ""

# Get next skill
echo "[TEST 7] Getting next skill to work on..."
NEXT_SKILL=$(curl -s -X GET http://localhost:5000/api/learning-path/next-skill \
  -H "Authorization: Bearer $TOKEN")

echo "✓ Next skill retrieved"
echo "$NEXT_SKILL" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if 'skill_name' in data:
    print(f\"Next Skill: {data['skill_name']}\")
    print(f\"Status: {data['status']}\")
    print(f\"Current Accuracy: {data['current_accuracy']}%\")
else:
    print(data.get('message', 'No data'))
"
echo ""

echo "=== All Tests Completed Successfully! ==="


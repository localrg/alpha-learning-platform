#!/bin/bash

echo "🧪 Testing Alpha Learning Platform Connection..."

echo ""
echo "1. Testing Backend Health..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/auth/login -X POST -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}')
if [ "$BACKEND_STATUS" = "200" ]; then
    echo "✅ Backend is responding correctly"
else
    echo "❌ Backend is not responding (Status: $BACKEND_STATUS)"
fi

echo ""
echo "2. Testing Frontend Health..."
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173)
if [ "$FRONTEND_STATUS" = "200" ]; then
    echo "✅ Frontend is responding correctly"
else
    echo "❌ Frontend is not responding (Status: $FRONTEND_STATUS)"
fi

echo ""
echo "3. Testing CORS Configuration..."
CORS_TEST=$(curl -s -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -H "Origin: http://localhost:5173" -d '{"username":"admin","password":"admin123"}' -I | grep -i "access-control-allow-origin")
if [ -n "$CORS_TEST" ]; then
    echo "✅ CORS is properly configured"
else
    echo "❌ CORS configuration issue"
fi

echo ""
echo "4. Testing Registration Endpoint..."
REG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/auth/register -X POST -H "Content-Type: application/json" -d '{"username":"testuser","password":"testpass123","email":"test@example.com"}')
if [ "$REG_STATUS" = "201" ]; then
    echo "✅ Registration endpoint is working"
else
    echo "❌ Registration endpoint issue (Status: $REG_STATUS)"
fi

echo ""
echo "🎉 Connection test completed!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:5173"
echo "   Backend API: http://localhost:5000/api"
echo ""
echo "👤 Test credentials:"
echo "   Username: admin"
echo "   Password: admin123"


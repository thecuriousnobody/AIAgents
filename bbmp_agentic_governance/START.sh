#!/bin/bash

echo "======================================================================"
echo "  BBMP AGENTIC GOVERNANCE SYSTEM - BRUTALIST INTERFACE"
echo "======================================================================"
echo ""
echo "  🏛️  Automating Transparent Governance with AI Agents"
echo ""
echo "  Starting servers..."
echo ""

# Install backend dependencies if needed
cd backend
pip install -q -r requirements.txt 2>/dev/null

# Start Flask API in background
echo "  ▸ Starting Flask API on port 5000..."
python api.py > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

# Install frontend dependencies if needed
cd frontend
if [ ! -d "node_modules" ]; then
    echo "  ▸ Installing frontend dependencies..."
    npm install --silent
fi

# Start React frontend
echo "  ▸ Starting React frontend on port 3000..."
echo ""
echo "======================================================================"
echo "  🚀 SYSTEM READY!"
echo "======================================================================"
echo ""
echo "  Frontend: http://localhost:3000"
echo "  Backend API: http://localhost:5000"
echo ""
echo "  Press Ctrl+C to stop all servers"
echo ""
echo "======================================================================"
echo ""

# Start frontend (this will block)
npm run dev

# Cleanup on exit
echo ""
echo "Shutting down servers..."
kill $BACKEND_PID 2>/dev/null
echo "Done!"

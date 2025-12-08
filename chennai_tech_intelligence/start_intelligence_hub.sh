#!/bin/bash

# Chennai Tech Intelligence Hub - Startup Script
# ==============================================
# 
# Impressive multi-agent AI system startup script

echo "🚀 Starting Chennai Tech Intelligence Hub"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Please run this script from the chennai_tech_intelligence directory${NC}"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}🔧 Starting AI Agent Backend (Port 8000)${NC}"
    echo "   - Multi-agent orchestration"
    echo "   - Real-time intelligence gathering"
    echo "   - WebSocket streaming"
    echo ""
    
    cd backend
    
    # Install Python dependencies if needed
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}🔨 Creating Python virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
    
    # Install dependencies
    echo -e "${YELLOW}📦 Installing backend dependencies...${NC}"
    pip install fastapi uvicorn websockets crewai crewai-tools python-dotenv > /dev/null 2>&1
    
    # Check backend port
    if ! check_port 8000; then
        echo -e "${RED}❌ Backend port 8000 is busy. Please free it and try again.${NC}"
        exit 1
    fi
    
    # Start backend server
    echo -e "${GREEN}✅ Starting FastAPI backend server...${NC}"
    python main.py &
    BACKEND_PID=$!
    
    cd ..
    
    # Wait a moment for backend to start
    sleep 3
    echo -e "${GREEN}✅ Backend is running on http://localhost:8000${NC}"
    echo ""
}

# Function to start frontend
start_frontend() {
    echo -e "${PURPLE}🎨 Starting React Dashboard (Port 3000)${NC}"
    echo "   - Real-time data visualization"
    echo "   - Professional UI/UX"
    echo "   - WebSocket live updates"
    echo ""
    
    cd frontend
    
    # Install Node dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
        npm install > /dev/null 2>&1
    fi
    
    # Check frontend port
    if ! check_port 3000; then
        echo -e "${RED}❌ Frontend port 3000 is busy. Please free it and try again.${NC}"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    
    # Start frontend server
    echo -e "${GREEN}✅ Starting React development server...${NC}"
    npm start &
    FRONTEND_PID=$!
    
    cd ..
    
    # Wait for frontend to compile
    sleep 5
    echo -e "${GREEN}✅ Frontend is running on http://localhost:3000${NC}"
    echo ""
}

# Function to display system status
show_system_status() {
    echo -e "${CYAN}🌟 CHENNAI TECH INTELLIGENCE HUB STARTED!${NC}"
    echo "=============================================="
    echo ""
    echo -e "${GREEN}🚀 Frontend Dashboard: ${CYAN}http://localhost:3000${NC}"
    echo -e "${GREEN}🔧 Backend API:       ${CYAN}http://localhost:8000${NC}" 
    echo -e "${GREEN}📚 API Documentation: ${CYAN}http://localhost:8000/api/docs${NC}"
    echo ""
    echo -e "${BLUE}🤖 Active AI Agents:${NC}"
    echo "   • Job Market Scout      - Real-time job posting analysis"
    echo "   • Salary Intelligence   - Compensation trend monitoring"  
    echo "   • Tech Stack Monitor    - Technology adoption tracking"
    echo "   • Startup Tracker       - Ecosystem growth analysis"
    echo "   • Community Pulse       - Developer events & engagement"
    echo ""
    echo -e "${PURPLE}✨ Features Demonstrated:${NC}"
    echo "   • Multi-agent AI coordination"
    echo "   • Real-time data streaming via WebSocket"
    echo "   • Professional React dashboard with charts"
    echo "   • FastAPI backend with async processing"  
    echo "   • Modern UI/UX with glassmorphism design"
    echo "   • Responsive data visualization"
    echo ""
    echo -e "${YELLOW}📊 Demo Data:${NC}"
    echo "   The system shows live Chennai IT market intelligence with:"
    echo "   - Job posting trends and salary analysis"
    echo "   - Technology stack adoption metrics"
    echo "   - Startup ecosystem activity tracking"
    echo "   - Community event and engagement data"
    echo ""
    echo -e "${GREEN}🎯 Perfect for demonstrating:${NC}"
    echo "   • Full-stack development capabilities"
    echo "   • AI agent system architecture"
    echo "   • Real-time data processing and visualization"
    echo "   • Professional software engineering practices"
    echo ""
    echo -e "${CYAN}Press Ctrl+C to stop the system${NC}"
    echo ""
}

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}🔄 Shutting down Chennai Tech Intelligence Hub...${NC}"
    
    # Kill background processes
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Backend stopped${NC}"
    fi
    
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ Frontend stopped${NC}"
    fi
    
    # Kill any remaining processes on our ports
    lsof -ti:3000 | xargs kill -9 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    
    echo -e "${BLUE}👋 Chennai Tech Intelligence Hub stopped${NC}"
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Main execution
echo -e "${PURPLE}🏗️  Initializing Chennai Tech Intelligence Hub...${NC}"
echo ""

# Check for required commands
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not installed${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ Node.js and npm are required but not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
echo ""

# Start services
start_backend
start_frontend
show_system_status

# Keep script running
while true; do
    sleep 1
done
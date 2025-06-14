#!/bin/bash

# Script to run the CSV to Anki Converter app (both frontend and backend)

# Deecho -e "${GREEN}All servers are running!${NC}"
echo -e "${YELLOW}---------------------------------------------${NC}"
echo -e "${GREEN}Backend API:${NC} http://localhost:8080"
echo -e "${GREEN}Frontend:${NC}   http://localhost:3000"
echo -e "${YELLOW}---------------------------------------------${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers.${NC}"olors for output
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}   Japanese Vocabulary Anki Deck Generator${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "${YELLOW}Starting services with enhanced features:${NC}"
echo -e "${GREEN}- Automatic translations for Japanese words${NC}"
echo -e "${GREEN}- Audio pronunciation for vocabulary${NC}" 
echo -e "${GREEN}- Example sentences for contextual learning${NC}"
echo -e "${BLUE}==============================================${NC}"
echo ""

# Check if Node.js and Python are installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Node.js is not installed. Please install Node.js to run the frontend.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 to run the backend.${NC}"
    exit 1
fi

# Function to start the backend server
start_backend() {
    echo -e "${BLUE}Starting backend server...${NC}"
    cd backend
    
    # Check if requirements are installed
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        echo -e "${YELLOW}Installing dependencies...${NC}"
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start the backend server
    echo -e "${GREEN}Starting FastAPI server...${NC}"
    uvicorn app.main:app --reload --port 8080 &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend server started at http://localhost:8080${NC}"
    cd ..
}

# Function to start the frontend server
start_frontend() {
    echo -e "${BLUE}Starting frontend server...${NC}"
    cd frontend
    
    # Check if node_modules exists, if not, install dependencies
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing frontend dependencies...${NC}"
        npm install
    fi
    
    # Start the frontend server
    echo -e "${GREEN}Starting React development server...${NC}"
    npm start &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend server started at http://localhost:3000${NC}"
    cd ..
}

# Function to handle script termination
cleanup() {
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}All servers shut down.${NC}"
    exit 0
}

# Register the cleanup function to run on script termination
trap cleanup SIGINT SIGTERM

# Start both servers
start_backend
start_frontend

echo ""
echo -e "${GREEN}All servers are running!${NC}"
echo -e "${BLUE}---------------------------------------------${NC}"
echo -e "${GREEN}Backend API:${NC} http://localhost:8000"
echo -e "${GREEN}Frontend:${NC}   http://localhost:3000"
echo -e "${BLUE}---------------------------------------------${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop all servers.${NC}"

# Keep the script running to maintain the servers
wait

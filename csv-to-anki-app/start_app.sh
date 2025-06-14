#!/bin/bash

# CSV to Anki App Runner
# This script starts both the backend and frontend servers

# Define colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

APP_DIR=$(cd "$(dirname "$0")" && pwd) # Get absolute path
BACKEND_DIR="$APP_DIR/backend"
FRONTEND_DIR="$APP_DIR/frontend"

# Function to check if a port is in use
is_port_in_use() {
  lsof -i:"$1" >/dev/null 2>&1
  return $?
}

# Error handler
handle_error() {
  echo -e "${RED}$1${NC}"
  exit 1
}

# Check if Python and Node.js are installed
command -v python3 >/dev/null 2>&1 || handle_error "Python 3 is not installed. Please install it to run the backend server."
command -v node >/dev/null 2>&1 || handle_error "Node.js is not installed. Please install it to run the frontend server."

# Start backend server
start_backend() {
  echo -e "${YELLOW}Starting backend server...${NC}"
  cd "$BACKEND_DIR" || handle_error "Failed to change to backend directory"
  
  # Check if required Python packages are installed
  if [ ! -f "requirements.txt" ]; then
    handle_error "Requirements file not found in $BACKEND_DIR"
  fi
  
  # Check if port 8000 is available
  if is_port_in_use 8000; then
    handle_error "Port 8000 is already in use. Please close the application using this port and try again."
  fi
  
  # Start the backend server
  python3 start_server.py &
  BACKEND_PID=$!
  echo -e "${GREEN}Backend server started with PID: $BACKEND_PID${NC}"
  
  # Give the backend time to start up
  sleep 2
}

# Start frontend server
start_frontend() {
  echo -e "${YELLOW}Starting frontend server...${NC}"
  
  # Check if frontend directory exists
  if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}Frontend directory not found at: $FRONTEND_DIR${NC}"
    echo -e "${YELLOW}Skipping frontend start...${NC}"
    return 1
  fi
  
  cd "$FRONTEND_DIR" || handle_error "Failed to change to frontend directory"
  
  # Check if node modules are installed
  if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install || handle_error "Failed to install frontend dependencies"
  fi
  
  # Start the frontend development server
  # Try port 3000 first, fall back to 3001 if necessary
  PORT=3000
  if is_port_in_use 3000; then
    echo -e "${YELLOW}Port 3000 is in use, trying port 3001...${NC}"
    PORT=3001
    if is_port_in_use 3001; then
      handle_error "Both ports 3000 and 3001 are in use. Please free up one of these ports and try again."
    fi
  fi
  
  PORT=$PORT npm start &
  FRONTEND_PID=$!
  echo -e "${GREEN}Frontend server started with PID: $FRONTEND_PID on port $PORT${NC}"
}

# Cleanup function to kill processes when the script is terminated
cleanup() {
  echo -e "${YELLOW}Shutting down servers...${NC}"
  [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
  [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
  echo -e "${GREEN}Servers shut down successfully${NC}"
  exit 0
}

# Set up trap to catch script termination
trap cleanup SIGINT SIGTERM

# Main execution
echo -e "${GREEN}Starting CSV to Anki App...${NC}"

# Start servers
start_backend
if start_frontend; then
  FRONTEND_RUNNING=true
else
  FRONTEND_RUNNING=false
fi

if [ "$FRONTEND_RUNNING" = true ]; then
  echo -e "${GREEN}Both servers are now running${NC}"
else
  echo -e "${GREEN}Backend server is now running${NC}"
  echo -e "${YELLOW}Frontend server was not started${NC}"
fi
echo "Backend: http://localhost:8080"
echo "Frontend: http://localhost:$PORT"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"

# Keep the script running to maintain the child processes
wait

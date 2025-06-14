#!/usr/bin/env python3
"""
Script to start the FastAPI backend server with proper imports.
This ensures the app module can be found correctly.
"""
import os
import sys
import uvicorn

# Add the parent directory to the Python path to find the app module
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)  # Backend directory

if __name__ == "__main__":
    try:
        print("Starting CSV to Anki backend server...")
        print(f"Server will be available at http://localhost:8000")
        print(f"Python path includes: {sys.path[:3]}")
        print("Press Ctrl+C to stop the server")
        
        # Start the server with the correct app import path
        uvicorn.run("app.main:app", 
                    host="0.0.0.0", 
                    port=8000, 
                    reload=True,
                    log_level="info")
    except ModuleNotFoundError as e:
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")
        print("- Make sure you're running this script from the backend directory")
        print("- If using a virtual environment, make sure it's activated")
        print("- Check that all required dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
Field Mapping Validation CLI Tool

This script is used to test the field mapping validation endpoint.
It can be run from the command line to validate field mappings directly.
"""
import json
import sys
import requests
import argparse
from pprint import pprint

def validate_field_mapping(session_id, mapping):
    """Validate a field mapping against the API"""
    try:
        print("Sending validation request to server...")
        
        # Make request to validation API
        response = requests.post(
            "http://localhost:8080/api/mapping/validate",
            json={
                "session_id": session_id,
                "mapping": mapping
            }
        )
        
        # Check if request was successful
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            print(f"Error: {response.status_code} - Session not found or expired")
            print("Try uploading your CSV file again to get a new session ID")
            return None
        else:
            print(f"Error: HTTP {response.status_code}")
            try:
                error_detail = response.json().get('detail', response.text)
                print(f"Server response: {error_detail}")
            except:
                print(f"Server response: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Connection Error: Could not connect to the backend server")
        print("Make sure the backend server is running (try ./start_app.sh)")
        return None
    except Exception as e:
        print(f"Exception: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Test field mapping validation')
    parser.add_argument('session_id', help='Session ID from a previous file upload')
    parser.add_argument('--mapping', '-m', help='JSON string of field mapping', required=False)
    parser.add_argument('--file', '-f', help='JSON file containing field mapping', required=False)
    
    args = parser.parse_args()
    
    # Get mapping from either command line or file
    if args.mapping:
        mapping = json.loads(args.mapping)
    elif args.file:
        with open(args.file, 'r') as f:
            mapping = json.load(f)
    else:
        # Default test mapping
        mapping = {
            "japanese": "Japanese",
            "english": "English",
            "reading": "Reading",
            "example": "Example",
            "tags": "Tags"
        }
    
    # Print the session and mapping being used
    print(f"Testing validation for session: {args.session_id}")
    print("Using mapping:")
    pprint(mapping)
    print("-" * 50)
    
    # Make the validation request
    result = validate_field_mapping(args.session_id, mapping)
    
    if result:
        print("Validation Result:")
        pprint(result)
        
        # Print a summary
        if result.get('valid'):
            print("\n✅ Mapping is valid")
        else:
            print("\n❌ Mapping is invalid:")
            for field, error in result.get('errors', {}).items():
                print(f"  - {field}: {error}")
    else:
        print("Validation failed to return a result")

if __name__ == "__main__":
    main()

"""
Field Mapping Router

This router handles API endpoints for analyzing CSV files and providing field mapping suggestions
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from ..services.field_mapping_service import FieldMappingService

router = APIRouter(prefix="/api/mapping", tags=["mapping"])
field_mapping_service = FieldMappingService()

@router.post("/analyze")
async def analyze_csv_file(file: UploadFile = File(...)):
    """
    Analyze a CSV file and suggest field mappings
    
    Args:
        file: The CSV file to analyze
        
    Returns:
        A dictionary containing headers, sample data, and suggested mappings
    """
    if not file.filename.endswith(('.csv', '.txt')):
        raise HTTPException(status_code=400, detail="Only .csv or .txt files are allowed")
    
    try:
        # Read content
        content = await file.read()
        text_content = content.decode('utf-8')
        
        # Analyze the CSV content
        headers, sample_data, suggested_mapping = field_mapping_service.analyze_csv_content(text_content)
        
        return JSONResponse(
            content={
                "headers": headers,
                "sample_data": sample_data,
                "suggested_mapping": suggested_mapping
            },
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing CSV file: {str(e)}")

@router.post("/apply")
async def apply_field_mapping(
    session_id: str = Form(...),
    mapping: str = Form(...),  # JSON string of the mapping
):
    """
    Apply a field mapping to a specific CSV file session
    
    Args:
        session_id: The ID of the CSV upload session
        mapping: JSON string of field mapping {anki_field: csv_header}
        
    Returns:
        Success message
    """
    try:
        import json
        mapping_dict = json.loads(mapping)
        
        # Store the mapping in the session data for later use
        from ..routers.deck_router import temp_storage
        
        if session_id not in temp_storage:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
        # Add mapping to session data
        temp_storage[session_id]["mapping"] = mapping_dict
        
        return {"message": "Field mapping applied successfully", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error applying field mapping: {str(e)}")

@router.post("/analyze-session")
async def analyze_session_csv(session_data: dict):
    """
    Analyze a previously uploaded CSV file using its session ID
    
    Args:
        session_data: Dictionary containing session_id
        
    Returns:
        A dictionary containing headers, sample data, and suggested mappings
    """
    try:
        # Import from deck_router to access the temp storage
        from ..routers.deck_router import temp_storage
        
        # Extract session_id
        session_id = session_data.get("session_id")
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
            
        # Get session data
        if session_id not in temp_storage:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
        # Get CSV content from session
        csv_content = temp_storage[session_id].get("content")
        if not csv_content:
            raise HTTPException(status_code=404, detail=f"No CSV content found for session {session_id}")
            
        # Analyze the CSV content
        headers, sample_data, suggested_mapping = field_mapping_service.analyze_csv_content(csv_content)
        
        return JSONResponse(
            content={
                "headers": headers,
                "sample_data": sample_data,
                "suggested_mapping": suggested_mapping
            },
            status_code=200
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing CSV from session: {str(e)}")

@router.post("/validate")
async def validate_field_mapping(request: dict):
    """
    Validate a field mapping against the specific CSV file structure
    
    Args:
        session_id: The ID of the CSV upload session
        mapping: Dict of field mapping {anki_field: csv_header}
        
    Returns:
        Validation result with any errors
    """
    try:
        # Extract data from request - handle both JSON and form data
        session_id = request.get("session_id")
        mapping = request.get("mapping")
        
        # Debug the incoming data
        print(f"Validation request: session_id={session_id}, mapping type={type(mapping)}")
        
        # If mapping is a string, try to parse it as JSON
        if isinstance(mapping, str):
            import json
            try:
                mapping = json.loads(mapping)
                print("Parsed mapping from JSON string")
            except json.JSONDecodeError:
                print("Failed to parse mapping as JSON string")
                raise HTTPException(status_code=400, detail="Invalid mapping format: not valid JSON")
        
        if not session_id:
            raise HTTPException(status_code=400, detail="session_id is required")
            
        if not mapping:
            raise HTTPException(status_code=400, detail="mapping is required")
        
        # Import from deck_router to access the temp storage
        from ..routers.deck_router import temp_storage
        
        # Get session data
        if session_id not in temp_storage:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
        # Get CSV content from session
        csv_content = temp_storage[session_id].get("content")
        if not csv_content:
            raise HTTPException(status_code=404, detail=f"No CSV content found for session {session_id}")
        
        # Validate the mapping against CSV headers
        headers, _, _ = field_mapping_service.analyze_csv_content(csv_content)
        
        # Check if all mapped fields exist in CSV headers
        validation_errors = {}
        for anki_field, csv_header in mapping.items():
            if csv_header and csv_header not in headers:
                validation_errors[anki_field] = f"CSV column '{csv_header}' not found in headers"
        
        # Check if required fields are mapped
        required_fields = ["japanese"]  # Only Japanese is required, English can be looked up if missing
        for field in required_fields:
            if field not in mapping or not mapping[field]:
                validation_errors[field] = f"Required field '{field}' is not mapped"
        
        return {
            "valid": len(validation_errors) == 0,
            "errors": validation_errors,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating field mapping: {str(e)}")

@router.get("/status/{session_id}")
async def get_field_mapping_status(session_id: str):
    """
    Get the current field mapping status for a session
    
    Args:
        session_id: The ID of the CSV upload session
        
    Returns:
        Status information about field mapping
    """
    try:
        # Import from deck_router to access the temp storage
        from ..routers.deck_router import temp_storage
        
        if session_id not in temp_storage:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get mapping if exists
        mapping = temp_storage[session_id].get("mapping", {})
        has_custom_mapping = bool(mapping)
        
        return {
            "has_mapping": has_custom_mapping,
            "mapping": mapping
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting field mapping status: {str(e)}")

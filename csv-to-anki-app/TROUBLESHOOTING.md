# Field Mapping Troubleshooting Guide

## Common Issues and Solutions

### Error: "No module named 'app'"

This error occurs when starting the backend server if the Python path isn't correctly set up.

**Solution:**
1. Use the provided `start_server.py` script instead of running uvicorn directly:
   ```bash
   cd /path/to/csv-to-anki-app/backend
   python start_server.py
   ```

2. Alternatively, use the `start_app.sh` script in the root directory to start both the backend and frontend:
   ```bash
   cd /path/to/csv-to-anki-app
   ./start_app.sh
   ```

### Field Mapping Validation Errors

If you're encountering errors with field mapping validation:

1. **Required Fields:** Make sure both "Japanese Word" and "English Meaning" fields are mapped. These are essential for creating Anki cards.

2. **Duplicate Mappings:** Each CSV column should only be mapped to one Anki field. The system prevents using the same column for multiple fields to avoid confusion.

3. **Column Existence:** Ensure the CSV columns you're mapping to actually exist in your CSV file. Double-check the column headers in your CSV file.

4. **Case Sensitivity:** Column names are case-sensitive. "Japanese" is not the same as "japanese" in the mapping.

5. **UI Indicators:**
   - 🟢 Green checkmark: Field is mapped correctly
   - 🔶 Orange warning: Field has a validation issue
   - 🔴 Red warning: Required field is missing

6. **Server Validation:** Sometimes client-side validation passes but server validation fails. This can happen if the CSV file structure on the server differs from what the client expects.

### Testing Field Mapping Validation

You can use the `test_validation.py` script to test field mapping validation:

```bash
cd /path/to/csv-to-anki-app/backend
python test_validation.py YOUR_SESSION_ID
```

Or specify a custom mapping:
```bash
python test_validation.py YOUR_SESSION_ID -m '{"japanese": "Column1", "english": "Column2"}'
```

### Backend Communication Issues

If the frontend can't communicate with the backend:

1. Make sure the backend server is running on port 8000
2. Check that the CORS settings in `main.py` include your frontend URL
3. Verify network requests in the browser's developer tools

## Advanced Troubleshooting

### Manual Field Mapping

You can directly apply field mapping through the API:

```bash
curl -X POST http://localhost:8000/api/mapping/apply \
  -F 'session_id=YOUR_SESSION_ID' \
  -F 'mapping={"japanese": "Column1", "english": "Column2"}'
```

### Debugging Backend Errors

To see detailed backend errors:

1. Run the server with debug logging:
   ```bash
   cd /path/to/csv-to-anki-app/backend
   python -m uvicorn app.main:app --reload --log-level debug
   ```

2. Check the terminal output for specific error messages

### Recovering from Errors

If you encounter persistent errors:

1. Clear your browser cache and local storage
2. Restart both the frontend and backend servers
3. Upload your CSV file again to get a fresh session ID

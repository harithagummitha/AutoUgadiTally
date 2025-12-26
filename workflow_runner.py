"""
Workflow Runner Script
Designed to be run in GitHub Actions or other CI/CD environments
"""

import os
import sys
import json
from workflow import Workflow


def main():
    """Main entry point for workflow execution"""
    
    # Get credentials
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
    
    # Check if credentials file exists
    if not os.path.exists(credentials_path):
        # Try to create from environment variable
        creds_json = os.getenv('GOOGLE_CREDENTIALS_JSON')
        if creds_json:
            try:
                creds_data = json.loads(creds_json)
                workflow = Workflow(credentials_json=creds_data)
            except json.JSONDecodeError:
                print("Error: GOOGLE_CREDENTIALS_JSON is not valid JSON")
                sys.exit(1)
        else:
            print(f"Error: Credentials file not found at {credentials_path}")
            print("Set GOOGLE_APPLICATION_CREDENTIALS or GOOGLE_CREDENTIALS_JSON environment variable")
            sys.exit(1)
    else:
        workflow = Workflow(credentials_path=credentials_path)
    
    # Get operation from environment variable
    operation = os.getenv('OPERATION', 'custom')
    spreadsheet_id = os.getenv('SPREADSHEET_ID', '')
    drive_folder_id = os.getenv('DRIVE_FOLDER_ID', '')
    file_id = os.getenv('DRIVE_FILE_ID', '')
    
    print(f"Running operation: {operation}")
    print(f"Spreadsheet ID: {spreadsheet_id if spreadsheet_id else 'Not provided'}")
    print(f"Drive Folder ID: {drive_folder_id if drive_folder_id else 'Not provided'}")
    
    try:
        if operation == 'read_sheets':
            if not spreadsheet_id:
                print("Error: SPREADSHEET_ID is required for read_sheets operation")
                sys.exit(1)
            
            sheet_name = os.getenv('SHEET_NAME', None)
            range_name = os.getenv('RANGE_NAME', None)
            
            print(f"Reading from Google Sheets...")
            if range_name:
                data = workflow.sheets_handler.read_range(spreadsheet_id, range_name)
            else:
                data = workflow.read_data_from_sheets(spreadsheet_id, sheet_name=sheet_name)
            
            print(f"Successfully read {len(data)} rows")
            if data:
                print("First few rows:")
                for i, row in enumerate(data[:5], 1):
                    print(f"  Row {i}: {row}")
            
        elif operation == 'write_sheets':
            if not spreadsheet_id:
                print("Error: SPREADSHEET_ID is required for write_sheets operation")
                sys.exit(1)
            
            # Get data from environment variable or use sample
            data_json = os.getenv('SHEETS_DATA')
            if data_json:
                try:
                    data = json.loads(data_json)
                except json.JSONDecodeError:
                    print("Error: SHEETS_DATA is not valid JSON")
                    sys.exit(1)
            else:
                # Default sample data
                from datetime import datetime
                data = [
                    ['Timestamp', 'Status', 'Message'],
                    [datetime.now().isoformat(), 'Success', 'Workflow executed successfully']
                ]
            
            range_name = os.getenv('RANGE_NAME', 'Sheet1!A1')
            append = os.getenv('APPEND', 'false').lower() == 'true'
            
            print(f"Writing to Google Sheets...")
            success = workflow.write_data_to_sheets(
                spreadsheet_id,
                data,
                range_name=range_name,
                append=append
            )
            
            if success:
                print("Data written successfully")
            else:
                print("Failed to write data")
                sys.exit(1)
            
        elif operation == 'drive_to_sheets':
            if not file_id and not os.getenv('DRIVE_FILENAME'):
                print("Error: DRIVE_FILE_ID or DRIVE_FILENAME is required for drive_to_sheets operation")
                sys.exit(1)
            
            if not spreadsheet_id:
                print("Error: SPREADSHEET_ID is required for drive_to_sheets operation")
                sys.exit(1)
            
            print(f"Processing Drive file to Sheets...")
            
            # Custom processing function if provided
            process_func = None
            process_func_code = os.getenv('PROCESS_FUNCTION')
            if process_func_code:
                # Note: This is a security risk in production - use with caution
                exec(process_func_code, globals())
                process_func = globals().get('process_file')
            
            if file_id:
                success = workflow.process_drive_to_sheets(
                    file_id,
                    spreadsheet_id,
                    range_name=os.getenv('RANGE_NAME', 'Sheet1!A1'),
                    process_func=process_func
                )
            else:
                filename = os.getenv('DRIVE_FILENAME')
                file_info = workflow.drive_handler.get_file_by_name(filename)
                if not file_info:
                    print(f"Error: File '{filename}' not found in Drive")
                    sys.exit(1)
                success = workflow.process_drive_to_sheets(
                    file_info['id'],
                    spreadsheet_id,
                    range_name=os.getenv('RANGE_NAME', 'Sheet1!A1'),
                    process_func=process_func
                )
            
            if success:
                print("Successfully processed Drive file to Sheets")
            else:
                print("Failed to process Drive file to Sheets")
                sys.exit(1)
            
        elif operation == 'sheets_to_drive':
            if not spreadsheet_id:
                print("Error: SPREADSHEET_ID is required for sheets_to_drive operation")
                sys.exit(1)
            
            output_filename = os.getenv('OUTPUT_FILENAME', 'export.csv')
            range_name = os.getenv('RANGE_NAME')
            sheet_name = os.getenv('SHEET_NAME')
            
            print(f"Processing Sheets to Drive...")
            file_id = workflow.process_sheets_to_drive(
                spreadsheet_id,
                output_filename,
                range_name=range_name,
                sheet_name=sheet_name,
                drive_folder_id=drive_folder_id
            )
            
            if file_id:
                print(f"Successfully exported to Drive. File ID: {file_id}")
            else:
                print("Failed to export Sheets to Drive")
                sys.exit(1)
            
        elif operation == 'list_drive_files':
            folder_id = drive_folder_id or os.getenv('DRIVE_FOLDER_ID')
            query = os.getenv('DRIVE_QUERY')
            
            print("Listing files in Google Drive...")
            files = workflow.drive_handler.list_files(folder_id=folder_id, query=query)
            print(f"Found {len(files)} files")
            for file in files[:10]:  # Show first 10
                print(f"  - {file.get('name')} (ID: {file.get('id')})")
            
        else:
            print(f"Unknown operation: {operation}")
            print("Available operations:")
            print("  - read_sheets: Read data from Google Sheets")
            print("  - write_sheets: Write data to Google Sheets")
            print("  - drive_to_sheets: Process Drive file to Sheets")
            print("  - sheets_to_drive: Export Sheets data to Drive")
            print("  - list_drive_files: List files in Google Drive")
            sys.exit(1)
        
        print("Workflow completed successfully!")
        
    except Exception as e:
        print(f"Error during workflow execution: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


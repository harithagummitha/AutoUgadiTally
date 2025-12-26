"""
Example usage of Google Drive and Sheets workflow
"""

from workflow import Workflow
import os


def example_workflow():
    """Example workflow demonstrating various operations"""
    
    # Initialize workflow
    # Make sure to set GOOGLE_APPLICATION_CREDENTIALS environment variable
    # or pass credentials_path parameter
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not credentials_path:
        print("Please set GOOGLE_APPLICATION_CREDENTIALS environment variable")
        print("or modify this script to pass credentials_path to Workflow()")
        return
    
    workflow = Workflow(credentials_path=credentials_path)
    
    # Example 1: List files in Google Drive
    print("Example 1: Listing files in Google Drive")
    drive_handler = workflow.drive_handler
    files = drive_handler.list_files()
    print(f"Found {len(files)} files")
    for file in files[:5]:  # Show first 5
        print(f"  - {file.get('name')} (ID: {file.get('id')})")
    
    # Example 2: Read data from Google Sheets
    print("\nExample 2: Reading from Google Sheets")
    spreadsheet_id = input("Enter spreadsheet ID (or press Enter to skip): ").strip()
    if spreadsheet_id:
        data = workflow.read_data_from_sheets(spreadsheet_id, sheet_name='Sheet1')
        print(f"Read {len(data)} rows from sheet")
        if data:
            print("First row:", data[0])
    
    # Example 3: Write data to Google Sheets
    print("\nExample 3: Writing to Google Sheets")
    if spreadsheet_id:
        sample_data = [
            ['Name', 'Age', 'City'],
            ['John Doe', '30', 'New York'],
            ['Jane Smith', '25', 'Los Angeles']
        ]
        success = workflow.write_data_to_sheets(
            spreadsheet_id, 
            sample_data, 
            range_name='Sheet1!A1',
            append=False
        )
        if success:
            print("Data written successfully!")
    
    # Example 4: Upload a file to Google Drive
    print("\nExample 4: Uploading file to Google Drive")
    local_file = input("Enter path to local file to upload (or press Enter to skip): ").strip()
    if local_file and os.path.exists(local_file):
        file_id = workflow.write_file_to_drive(local_file)
        if file_id:
            print(f"File uploaded! File ID: {file_id}")
    
    # Example 5: Download a file from Google Drive
    print("\nExample 5: Downloading file from Google Drive")
    file_id = input("Enter file ID to download (or press Enter to skip): ").strip()
    if file_id:
        output_path = "downloaded_file.txt"
        success = workflow.read_file_from_drive(file_id=file_id, output_path=output_path)
        if success:
            print(f"File downloaded to {output_path}")
    
    print("\nWorkflow examples completed!")


if __name__ == "__main__":
    example_workflow()


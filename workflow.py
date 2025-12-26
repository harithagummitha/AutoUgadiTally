"""
Main Workflow Script
Orchestrates Google Drive and Google Sheets operations
"""

import os
import json
from typing import Optional, Dict, List, Any
from google_drive_handler import GoogleDriveHandler
from google_sheets_handler import GoogleSheetsHandler


class Workflow:
    """Main workflow class to orchestrate operations"""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_json: Optional[Dict] = None):
        """
        Initialize workflow with Google Drive and Sheets handlers
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account credentials as dict
        """
        self.drive_handler = GoogleDriveHandler(credentials_path, credentials_json)
        self.sheets_handler = GoogleSheetsHandler(credentials_path, credentials_json)
    
    def read_file_from_drive(self, file_id: Optional[str] = None, filename: Optional[str] = None, 
                            folder_id: Optional[str] = None, output_path: str = "downloaded_file") -> bool:
        """
        Read/download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID (if known)
            filename: Name of the file to find
            folder_id: Optional folder ID to search in
            output_path: Local path to save the file
        
        Returns:
            True if successful, False otherwise
        """
        if not file_id and filename:
            file_info = self.drive_handler.get_file_by_name(filename, folder_id)
            if not file_info:
                print(f"File '{filename}' not found in Google Drive")
                return False
            file_id = file_info['id']
        
        if not file_id:
            print("Either file_id or filename must be provided")
            return False
        
        return self.drive_handler.download_file(file_id, output_path)
    
    def write_file_to_drive(self, local_path: str, drive_folder_id: Optional[str] = None,
                           drive_filename: Optional[str] = None) -> Optional[str]:
        """
        Write/upload a file to Google Drive
        
        Args:
            local_path: Path to local file to upload
            drive_folder_id: Optional folder ID to upload to
            drive_filename: Optional name for the file in Drive
        
        Returns:
            Google Drive file ID if successful, None otherwise
        """
        return self.drive_handler.upload_file(local_path, drive_folder_id, drive_filename)
    
    def read_data_from_sheets(self, spreadsheet_id: str, range_name: Optional[str] = None,
                             sheet_name: Optional[str] = None) -> List[List[Any]]:
        """
        Read data from Google Sheets
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Optional range in A1 notation
            sheet_name: Optional sheet name
        
        Returns:
            List of rows with cell values
        """
        if range_name:
            return self.sheets_handler.read_range(spreadsheet_id, range_name)
        else:
            return self.sheets_handler.read_sheet(spreadsheet_id, sheet_name)
    
    def write_data_to_sheets(self, spreadsheet_id: str, data: List[List[Any]], 
                            range_name: str = "Sheet1!A1", append: bool = False) -> bool:
        """
        Write data to Google Sheets
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            data: List of rows to write
            range_name: Range in A1 notation
            append: If True, append data instead of overwriting
        
        Returns:
            True if successful, False otherwise
        """
        if append:
            return self.sheets_handler.append_rows(spreadsheet_id, range_name, data)
        else:
            return self.sheets_handler.write_range(spreadsheet_id, range_name, data)
    
    def process_drive_to_sheets(self, file_id: str, spreadsheet_id: str, 
                               range_name: str = "Sheet1!A1", process_func: Optional[callable] = None) -> bool:
        """
        Process a file from Drive and write results to Sheets
        
        Args:
            file_id: Google Drive file ID
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range in A1 notation to write to
            process_func: Optional function to process file content
        
        Returns:
            True if successful, False otherwise
        """
        # Download file
        temp_path = "temp_downloaded_file"
        if not self.drive_handler.download_file(file_id, temp_path):
            return False
        
        # Process file if function provided
        if process_func:
            data = process_func(temp_path)
        else:
            # Default: read as text and split into rows
            with open(temp_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                data = [[line.strip()] for line in lines]
        
        # Write to sheets
        result = self.sheets_handler.write_range(spreadsheet_id, range_name, data)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return result
    
    def process_sheets_to_drive(self, spreadsheet_id: str, output_filename: str,
                               range_name: Optional[str] = None, sheet_name: Optional[str] = None,
                               drive_folder_id: Optional[str] = None, format: str = 'csv') -> Optional[str]:
        """
        Read data from Sheets and save as file to Drive
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            output_filename: Name for the output file
            range_name: Optional range to read
            sheet_name: Optional sheet name
            drive_folder_id: Optional folder ID to upload to
            format: Output format ('csv', 'txt')
        
        Returns:
            Google Drive file ID if successful, None otherwise
        """
        # Read from sheets
        if range_name:
            data = self.sheets_handler.read_range(spreadsheet_id, range_name)
        else:
            data = self.sheets_handler.read_sheet(spreadsheet_id, sheet_name)
        
        # Write to local file
        temp_path = f"temp_{output_filename}"
        with open(temp_path, 'w', encoding='utf-8') as f:
            for row in data:
                if format == 'csv':
                    import csv
                    csv.writer(f).writerow(row)
                else:
                    f.write('\t'.join(str(cell) for cell in row) + '\n')
        
        # Upload to drive
        file_id = self.drive_handler.upload_file(temp_path, drive_folder_id, output_filename)
        
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        return file_id


def main():
    """Example workflow execution"""
    # Initialize workflow
    # Option 1: Use credentials file path
    # workflow = Workflow(credentials_path='path/to/credentials.json')
    
    # Option 2: Use environment variable
    # workflow = Workflow()
    
    # Option 3: Use credentials dict
    # with open('credentials.json', 'r') as f:
    #     creds = json.load(f)
    # workflow = Workflow(credentials_json=creds)
    
    print("Workflow initialized. Use the Workflow class methods to perform operations.")
    print("\nExample operations:")
    print("1. workflow.read_file_from_drive(file_id='...', output_path='output.txt')")
    print("2. workflow.write_file_to_drive('local_file.txt', drive_folder_id='...')")
    print("3. workflow.read_data_from_sheets(spreadsheet_id='...', sheet_name='Sheet1')")
    print("4. workflow.write_data_to_sheets(spreadsheet_id='...', data=[['Header1', 'Header2'], ['Value1', 'Value2']])")


if __name__ == "__main__":
    main()


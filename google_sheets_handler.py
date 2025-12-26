"""
Google Sheets Handler
Handles reading and writing data from Google Sheets
"""

import os
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleSheetsHandler:
    """Handler for Google Sheets operations"""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_json: Optional[Dict] = None):
        """
        Initialize Google Sheets handler
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account credentials as dict (alternative to file path)
        """
        if credentials_path:
            self.creds = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        elif credentials_json:
            self.creds = service_account.Credentials.from_service_account_info(
                credentials_json,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
        else:
            # Try to get from environment variable
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if creds_path:
                self.creds = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=['https://www.googleapis.com/auth/spreadsheets']
                )
            else:
                raise ValueError("Either credentials_path, credentials_json, or GOOGLE_APPLICATION_CREDENTIALS must be provided")
        
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def read_range(self, spreadsheet_id: str, range_name: str) -> List[List[Any]]:
        """
        Read data from a specific range in Google Sheets
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range in A1 notation (e.g., 'Sheet1!A1:C10')
        
        Returns:
            List of rows, where each row is a list of cell values
        """
        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            values = result.get('values', [])
            return values
        except HttpError as error:
            print(f"An error occurred while reading from sheet: {error}")
            return []
    
    def read_sheet(self, spreadsheet_id: str, sheet_name: Optional[str] = None) -> List[List[Any]]:
        """
        Read entire sheet or specific sheet
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Optional sheet name (reads first sheet if not provided)
        
        Returns:
            List of rows, where each row is a list of cell values
        """
        if sheet_name:
            range_name = f"{sheet_name}!A:Z"
        else:
            # Get first sheet name
            sheet_metadata = self.get_sheet_metadata(spreadsheet_id)
            if sheet_metadata:
                sheet_name = sheet_metadata[0].get('properties', {}).get('title', 'Sheet1')
                range_name = f"{sheet_name}!A:Z"
            else:
                range_name = "Sheet1!A:Z"
        
        return self.read_range(spreadsheet_id, range_name)
    
    def write_range(self, spreadsheet_id: str, range_name: str, values: List[List[Any]], 
                   value_input_option: str = 'RAW') -> bool:
        """
        Write data to a specific range in Google Sheets
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range in A1 notation (e.g., 'Sheet1!A1')
            values: List of rows, where each row is a list of cell values
            value_input_option: 'RAW' or 'USER_ENTERED' (for formulas)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()
            
            print(f"Updated {result.get('updatedCells')} cells")
            return True
        except HttpError as error:
            print(f"An error occurred while writing to sheet: {error}")
            return False
    
    def append_rows(self, spreadsheet_id: str, range_name: str, values: List[List[Any]], 
                   value_input_option: str = 'RAW') -> bool:
        """
        Append rows to a sheet
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range in A1 notation (e.g., 'Sheet1!A1')
            values: List of rows to append
            value_input_option: 'RAW' or 'USER_ENTERED'
        
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {
                'values': values
            }
            
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption=value_input_option,
                body=body
            ).execute()
            
            print(f"Appended {result.get('updates', {}).get('updatedCells', 0)} cells")
            return True
        except HttpError as error:
            print(f"An error occurred while appending to sheet: {error}")
            return False
    
    def clear_range(self, spreadsheet_id: str, range_name: str) -> bool:
        """
        Clear data from a specific range
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            range_name: Range in A1 notation
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            
            print(f"Cleared range: {range_name}")
            return True
        except HttpError as error:
            print(f"An error occurred while clearing range: {error}")
            return False
    
    def get_sheet_metadata(self, spreadsheet_id: str) -> List[Dict]:
        """
        Get metadata about all sheets in the spreadsheet
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
        
        Returns:
            List of sheet metadata dictionaries
        """
        try:
            spreadsheet = self.service.spreadsheets().get(
                spreadsheetId=spreadsheet_id
            ).execute()
            
            return spreadsheet.get('sheets', [])
        except HttpError as error:
            print(f"An error occurred while getting sheet metadata: {error}")
            return []
    
    def create_sheet(self, spreadsheet_id: str, sheet_name: str) -> bool:
        """
        Create a new sheet in the spreadsheet
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_name: Name of the new sheet
        
        Returns:
            True if successful, False otherwise
        """
        try:
            request_body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            print(f"Sheet '{sheet_name}' created successfully")
            return True
        except HttpError as error:
            print(f"An error occurred while creating sheet: {error}")
            return False
    
    def delete_sheet(self, spreadsheet_id: str, sheet_id: int) -> bool:
        """
        Delete a sheet from the spreadsheet
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            sheet_id: ID of the sheet to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            request_body = {
                'requests': [{
                    'deleteSheet': {
                        'sheetId': sheet_id
                    }
                }]
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=request_body
            ).execute()
            
            print(f"Sheet deleted successfully")
            return True
        except HttpError as error:
            print(f"An error occurred while deleting sheet: {error}")
            return False
    
    def batch_update(self, spreadsheet_id: str, requests: List[Dict]) -> bool:
        """
        Perform batch update operations
        
        Args:
            spreadsheet_id: Google Sheets spreadsheet ID
            requests: List of request dictionaries
        
        Returns:
            True if successful, False otherwise
        """
        try:
            body = {
                'requests': requests
            }
            
            self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body
            ).execute()
            
            print("Batch update completed successfully")
            return True
        except HttpError as error:
            print(f"An error occurred during batch update: {error}")
            return False


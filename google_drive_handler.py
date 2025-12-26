"""
Google Drive Handler
Handles reading and writing files from Google Drive
"""

import os
from typing import Optional, List, Dict
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.errors import HttpError
import io


class GoogleDriveHandler:
    """Handler for Google Drive operations"""
    
    def __init__(self, credentials_path: Optional[str] = None, credentials_json: Optional[Dict] = None):
        """
        Initialize Google Drive handler
        
        Args:
            credentials_path: Path to service account JSON file
            credentials_json: Service account credentials as dict (alternative to file path)
        """
        if credentials_path:
            self.creds = service_account.Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/drive']
            )
        elif credentials_json:
            self.creds = service_account.Credentials.from_service_account_info(
                credentials_json,
                scopes=['https://www.googleapis.com/auth/drive']
            )
        else:
            # Try to get from environment variable
            creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            if creds_path:
                self.creds = service_account.Credentials.from_service_account_file(
                    creds_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
            else:
                raise ValueError("Either credentials_path, credentials_json, or GOOGLE_APPLICATION_CREDENTIALS must be provided")
        
        self.service = build('drive', 'v3', credentials=self.creds)
    
    def list_files(self, folder_id: Optional[str] = None, query: Optional[str] = None) -> List[Dict]:
        """
        List files in Google Drive
        
        Args:
            folder_id: Optional folder ID to list files from
            query: Optional query string for filtering files
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            query_parts = []
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            if query:
                query_parts.append(query)
            
            query_string = " and ".join(query_parts) if query_parts else None
            
            results = self.service.files().list(
                q=query_string,
                pageSize=100,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime)"
            ).execute()
            
            return results.get('files', [])
        except HttpError as error:
            print(f"An error occurred while listing files: {error}")
            return []
    
    def get_file_by_name(self, filename: str, folder_id: Optional[str] = None) -> Optional[Dict]:
        """
        Get file metadata by name
        
        Args:
            filename: Name of the file to find
            folder_id: Optional folder ID to search in
        
        Returns:
            File metadata dictionary or None if not found
        """
        query = f"name='{filename}'"
        if folder_id:
            query += f" and '{folder_id}' in parents"
        
        files = self.list_files(query=query)
        return files[0] if files else None
    
    def download_file(self, file_id: str, output_path: str) -> bool:
        """
        Download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            output_path: Local path to save the file
        
        Returns:
            True if successful, False otherwise
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            file_content = io.BytesIO()
            downloader = MediaIoBaseDownload(file_content, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
            
            file_content.seek(0)
            with open(output_path, 'wb') as f:
                f.write(file_content.read())
            
            print(f"File downloaded successfully to {output_path}")
            return True
        except HttpError as error:
            print(f"An error occurred while downloading file: {error}")
            return False
    
    def upload_file(self, local_path: str, drive_folder_id: Optional[str] = None, 
                   drive_filename: Optional[str] = None, mime_type: Optional[str] = None) -> Optional[str]:
        """
        Upload a file to Google Drive
        
        Args:
            local_path: Path to local file to upload
            drive_folder_id: Optional folder ID to upload to
            drive_filename: Optional name for the file in Drive (defaults to local filename)
            mime_type: Optional MIME type (auto-detected if not provided)
        
        Returns:
            Google Drive file ID if successful, None otherwise
        """
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            
            filename = drive_filename or os.path.basename(local_path)
            
            file_metadata = {'name': filename}
            if drive_folder_id:
                file_metadata['parents'] = [drive_folder_id]
            
            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            print(f"File uploaded successfully. File ID: {file.get('id')}")
            return file.get('id')
        except HttpError as error:
            print(f"An error occurred while uploading file: {error}")
            return None
    
    def update_file(self, file_id: str, local_path: str, mime_type: Optional[str] = None) -> bool:
        """
        Update an existing file in Google Drive
        
        Args:
            file_id: Google Drive file ID to update
            local_path: Path to local file with new content
            mime_type: Optional MIME type
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"Local file not found: {local_path}")
            
            media = MediaFileUpload(local_path, mimetype=mime_type, resumable=True)
            
            self.service.files().update(
                fileId=file_id,
                media_body=media
            ).execute()
            
            print(f"File updated successfully. File ID: {file_id}")
            return True
        except HttpError as error:
            print(f"An error occurred while updating file: {error}")
            return False
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from Google Drive
        
        Args:
            file_id: Google Drive file ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
            print(f"File deleted successfully. File ID: {file_id}")
            return True
        except HttpError as error:
            print(f"An error occurred while deleting file: {error}")
            return False
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """
        Create a folder in Google Drive
        
        Args:
            folder_name: Name of the folder to create
            parent_folder_id: Optional parent folder ID
        
        Returns:
            Google Drive folder ID if successful, None otherwise
        """
        try:
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            if parent_folder_id:
                file_metadata['parents'] = [parent_folder_id]
            
            folder = self.service.files().create(
                body=file_metadata,
                fields='id'
            ).execute()
            
            print(f"Folder created successfully. Folder ID: {folder.get('id')}")
            return folder.get('id')
        except HttpError as error:
            print(f"An error occurred while creating folder: {error}")
            return None


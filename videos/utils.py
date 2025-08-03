import os
import io
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from django.conf import settings

class GoogleDriveStorage:
    def __init__(self):
        if settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE:
            credentials = service_account.Credentials.from_service_account_file(
                settings.GOOGLE_DRIVE_STORAGE_JSON_KEY_FILE,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=credentials)
        else:
            self.service = None

    def upload_file(self, file_path, file_name, folder_id=None):
        """Upload file to Google Drive"""
        if not self.service:
            return None

        file_metadata = {'name': file_name}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaFileUpload(file_path, resumable=True)
        
        try:
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            # Make file publicly accessible
            self.service.permissions().create(
                fileId=file.get('id'),
                body={'role': 'reader', 'type': 'anyone'}
            ).execute()
            
            return f"https://drive.google.com/file/d/{file.get('id')}/view"
        except Exception as e:
            print(f"Error uploading to Google Drive: {e}")
            return None

    def delete_file(self, file_id):
        """Delete file from Google Drive"""
        if not self.service:
            return False

        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting from Google Drive: {e}")
            return False

    def get_file_url(self, file_id):
        """Get public URL for a file"""
        return f"https://drive.google.com/file/d/{file_id}/view"

    def get_file_info(self, file_id):
        """Get file information"""
        if not self.service:
            return None

        try:
            file_info = self.service.files().get(fileId=file_id).execute()
            return file_info
        except Exception as e:
            print(f"Error getting file info: {e}")
            return None

# AutoUgadiTally - Google Drive & Sheets Workflow

Python scripts for reading and writing files from Google Drive and Google Sheets, with workflow orchestration capabilities.

## Features

- **Google Drive Operations**: Upload, download, update, delete files and folders
- **Google Sheets Operations**: Read, write, append, clear data in spreadsheets
- **Workflow Orchestration**: Chain operations between Drive and Sheets
- **Flexible Authentication**: Support for service account credentials via file or environment variable

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Drive API
   - Google Sheets API
4. Create a Service Account:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name and description
   - Click "Create and Continue"
   - Grant necessary roles (or skip for now)
   - Click "Done"
5. Create and download credentials:
   - Click on the created service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file

### 3. Share Resources with Service Account

- **For Google Drive**: Share the folder/file with the service account email (found in the JSON file)
- **For Google Sheets**: Share the spreadsheet with the service account email

### 4. Configure Credentials

**Option 1: Environment Variable**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

**Option 2: Pass in Code**
```python
workflow = Workflow(credentials_path='path/to/credentials.json')
```

## Usage

### Basic Google Drive Operations

```python
from google_drive_handler import GoogleDriveHandler

# Initialize handler
drive = GoogleDriveHandler(credentials_path='credentials.json')

# List files
files = drive.list_files(folder_id='your-folder-id')

# Download file
drive.download_file(file_id='file-id', output_path='local_file.txt')

# Upload file
file_id = drive.upload_file('local_file.txt', drive_folder_id='folder-id')

# Get file by name
file_info = drive.get_file_by_name('filename.txt', folder_id='folder-id')
```

### Basic Google Sheets Operations

```python
from google_sheets_handler import GoogleSheetsHandler

# Initialize handler
sheets = GoogleSheetsHandler(credentials_path='credentials.json')

# Read data
data = sheets.read_range('spreadsheet-id', 'Sheet1!A1:C10')

# Write data
sheets.write_range('spreadsheet-id', 'Sheet1!A1', [['Header1', 'Header2'], ['Value1', 'Value2']])

# Append data
sheets.append_rows('spreadsheet-id', 'Sheet1!A1', [['New', 'Row']])
```

### Workflow Operations

```python
from workflow import Workflow

# Initialize workflow
workflow = Workflow(credentials_path='credentials.json')

# Read file from Drive
workflow.read_file_from_drive(filename='data.txt', output_path='downloaded.txt')

# Write file to Drive
file_id = workflow.write_file_to_drive('local_file.txt', drive_folder_id='folder-id')

# Read data from Sheets
data = workflow.read_data_from_sheets('spreadsheet-id', sheet_name='Sheet1')

# Write data to Sheets
workflow.write_data_to_sheets('spreadsheet-id', [['Name', 'Age'], ['John', '30']])

# Process Drive file and write to Sheets
def process_file(file_path):
    # Your custom processing logic
    with open(file_path, 'r') as f:
        lines = f.readlines()
    return [[line.strip()] for line in lines]

workflow.process_drive_to_sheets('file-id', 'spreadsheet-id', process_func=process_file)

# Process Sheets data and save to Drive
file_id = workflow.process_sheets_to_drive('spreadsheet-id', 'output.csv', drive_folder_id='folder-id')
```

## GitHub Actions Workflow

This project includes GitHub Actions workflows for automated execution:

### Setup GitHub Secrets

1. Go to your repository **Settings** > **Secrets and variables** > **Actions**
2. Add the following secret:
   - `GOOGLE_APPLICATION_CREDENTIALS`: Paste the entire contents of your service account JSON file
3. Optionally add default values:
   - `DEFAULT_SPREADSHEET_ID`
   - `DEFAULT_DRIVE_FOLDER_ID`
   - `DEFAULT_DRIVE_FILE_ID`

### Run Workflow

**Automated:**
- Runs on schedule (daily at 2 AM UTC by default)
- Runs on push to main/master branch

**Manual:**
1. Go to **Actions** tab
2. Select **Google Drive & Sheets Workflow**
3. Click **Run workflow**
4. Choose operation and provide IDs

See [`.github/workflows/README.md`](.github/workflows/README.md) for detailed documentation.

## File Structure

```
AutoUgadiTally/
├── google_drive_handler.py    # Google Drive operations
├── google_sheets_handler.py    # Google Sheets operations
├── workflow.py                 # Main workflow orchestration
├── workflow_runner.py          # CLI runner for workflows
├── example_usage.py            # Example usage script
├── requirements.txt            # Python dependencies
├── config.example.json         # Example configuration
├── .github/
│   └── workflows/
│       ├── run_workflow.yml    # Main GitHub Actions workflow
│       ├── test_workflow.yml   # Testing workflow
│       └── README.md           # Workflow documentation
└── README.md                   # This file
```

## Error Handling

All methods include error handling and will print error messages if operations fail. Methods return:
- `True/False` for boolean operations
- `Optional[str]` for operations that return file IDs
- `List` for read operations (empty list on error)

## Security Notes

- Never commit your `credentials.json` file to version control
- Add `credentials.json` to `.gitignore`
- Use environment variables for credentials in production
- Regularly rotate service account keys

## License

This project is for internal use.


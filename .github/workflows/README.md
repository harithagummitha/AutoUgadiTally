# GitHub Workflows

This directory contains GitHub Actions workflows for automating Google Drive and Sheets operations.

## Workflows

### 1. `run_workflow.yml`
Main workflow for running Google Drive and Sheets operations.

**Triggers:**
- Scheduled (daily at 2 AM UTC by default)
- Manual trigger via workflow_dispatch
- Push to main/master branch
- Pull requests

**Required Secrets:**
- `GOOGLE_APPLICATION_CREDENTIALS`: JSON content of your Google service account credentials file

**Optional Secrets:**
- `DEFAULT_SPREADSHEET_ID`: Default Google Sheets spreadsheet ID
- `DEFAULT_DRIVE_FOLDER_ID`: Default Google Drive folder ID
- `DEFAULT_DRIVE_FILE_ID`: Default Google Drive file ID
- `DEFAULT_RANGE_NAME`: Default range for Sheets operations (e.g., 'Sheet1!A1')
- `DEFAULT_SHEET_NAME`: Default sheet name
- `DEFAULT_OUTPUT_FILENAME`: Default output filename for exports

**Manual Inputs (when triggering manually):**
- `operation` (required): Operation to perform
  - `read_sheets`: Read data from Google Sheets
  - `write_sheets`: Write data to Google Sheets
  - `drive_to_sheets`: Process Drive file to Sheets
  - `sheets_to_drive`: Export Sheets data to Drive
  - `list_drive_files`: List files in Google Drive
  - `custom`: Custom operation
- `spreadsheet_id`: Google Sheets Spreadsheet ID (required for sheet operations)
- `drive_folder_id`: Google Drive Folder ID (optional)
- `drive_file_id`: Google Drive File ID (for drive_to_sheets operation)
- `sheet_name`: Sheet name (optional, defaults to first sheet)
- `range_name`: Range in A1 notation (e.g., Sheet1!A1:C10)
- `output_filename`: Output filename for exports (default: export.csv)

### 2. `test_workflow.yml`
Testing workflow that validates code syntax and imports without requiring credentials.

**Triggers:**
- Push to main/master branch
- Pull requests
- Manual trigger

## Setup Instructions

### 1. Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add the following secrets:

   **Required:**
   - Name: `GOOGLE_APPLICATION_CREDENTIALS`
   - Value: Copy the entire contents of your service account JSON file

   **Optional (for default values):**
   - `DEFAULT_SPREADSHEET_ID`
   - `DEFAULT_DRIVE_FOLDER_ID`
   - `DEFAULT_DRIVE_FILE_ID`
   - `DEFAULT_RANGE_NAME`
   - `DEFAULT_SHEET_NAME`
   - `DEFAULT_OUTPUT_FILENAME`

### 2. Configure Schedule (Optional)

Edit `.github/workflows/run_workflow.yml` to change the schedule:

```yaml
schedule:
  - cron: '0 2 * * *'  # Daily at 2 AM UTC
```

Cron format: `minute hour day month day-of-week`
- `0 2 * * *` = Daily at 2 AM UTC
- `0 */6 * * *` = Every 6 hours
- `0 0 * * 1` = Every Monday at midnight

### 3. Run Workflow Manually

**Manual triggering is enabled and ready to use!**

1. Go to **Actions** tab in your repository
2. Select **Google Drive & Sheets Workflow** from the left sidebar
3. Click **Run workflow** button on the right
4. Choose:
   - **Branch**: Select the branch to run from (usually `main`)
   - **Operation**: Select the operation to perform (required)
   - **Spreadsheet ID**: Enter if needed for sheet operations
   - **Drive Folder ID**: Enter if needed for Drive operations
   - **Drive File ID**: Enter if processing a specific Drive file
   - **Sheet Name**: Optional sheet name
   - **Range Name**: Optional range in A1 notation
   - **Output Filename**: Optional output filename for exports
5. Click the green **Run workflow** button

The workflow will start immediately and you can monitor its progress in real-time.

## Available Operations

### read_sheets
Read data from Google Sheets and display it.

**Required:**
- `SPREADSHEET_ID` (via secret or input)

**Optional:**
- `SHEET_NAME`: Specific sheet name
- `RANGE_NAME`: Specific range (e.g., 'Sheet1!A1:C10')

### write_sheets
Write data to Google Sheets.

**Required:**
- `SPREADSHEET_ID`

**Optional:**
- `RANGE_NAME`: Where to write (default: 'Sheet1!A1')
- `SHEETS_DATA`: JSON array of rows (default: timestamp entry)
- `APPEND`: 'true' to append instead of overwrite

### drive_to_sheets
Process a file from Google Drive and write to Sheets.

**Required:**
- `SPREADSHEET_ID`
- `DRIVE_FILE_ID` or `DRIVE_FILENAME`

**Optional:**
- `RANGE_NAME`: Where to write in Sheets
- `PROCESS_FUNCTION`: Custom processing function code

### sheets_to_drive
Export Google Sheets data to a file in Google Drive.

**Required:**
- `SPREADSHEET_ID`

**Optional:**
- `DRIVE_FOLDER_ID`: Where to save the file
- `OUTPUT_FILENAME`: Name of output file
- `RANGE_NAME`: Specific range to export
- `SHEET_NAME`: Specific sheet to export

### list_drive_files
List files in Google Drive.

**Optional:**
- `DRIVE_FOLDER_ID`: Folder to list files from
- `DRIVE_QUERY`: Query string for filtering

## Environment Variables

The workflow uses environment variables that can be set via:
1. GitHub Secrets (for sensitive/default values)
2. Workflow inputs (for manual overrides)
3. Environment variables in the workflow file

## Troubleshooting

### Workflow fails with "credentials not found"
- Ensure `GOOGLE_APPLICATION_CREDENTIALS` secret is set
- Verify the JSON content is valid

### Workflow fails with "permission denied"
- Share your Google Drive folder/file with the service account email
- Share your Google Sheets spreadsheet with the service account email
- Verify the service account has necessary permissions

### Workflow runs but doesn't perform expected operation
- Check the `OPERATION` environment variable
- Verify required IDs (spreadsheet_id, file_id, etc.) are provided
- Check workflow logs for detailed error messages

## Security Best Practices

1. **Never commit credentials**: Always use GitHub Secrets
2. **Use service accounts**: Don't use personal Google accounts
3. **Limit permissions**: Grant only necessary permissions to service account
4. **Rotate keys**: Regularly rotate service account keys
5. **Review logs**: Check workflow logs for any sensitive data exposure


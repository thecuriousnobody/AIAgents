from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaIoBaseUpload
from io import BytesIO

output = "Hi, How Are You?"
topic = "MentalHealth"


# def save_to_google_drive(content, file_name):
#     creds = None
#     if creds and creds.expired and creds.refresh_token:
#         creds.refresh(Request())
#     else:
#         flow = InstalledAppFlow.from_client_secrets_file('/Users/rajeevkumar/Documents/myPersonalDocuments/client_secret_949298345051-ieb70h2d31ot22jfjv1vs3la4149vmp5.apps.googleusercontent.com.json', ['https://www.googleapis.com/auth/drive'])
#         creds = flow.run_local_server(port=0)
#
#     try:
#         service = build('drive', 'v3', credentials=creds)
#         file_metadata = {'name': file_name, 'mimeType': 'text/plain'}
#         file = service.files().create(body=file_metadata, media_body=content.encode('utf-8')).execute()
#         print(f'File ID: {file.get("id")}')
#     except HttpError as error:
#         print(f'An error occurred: {error}')
#         file = None
#
#     return file



def save_to_google_drive(content, file_name):
    creds = None
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('/Users/rajeevkumar/Documents/myPersonalDocuments/client_secret_949298345051-ieb70h2d31ot22jfjv1vs3la4149vmp5.apps.googleusercontent.com.json', ['https://www.googleapis.com/auth/drive'])
        creds = flow.run_local_server(port=0)

    try:
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': file_name, 'mimeType': 'text/plain'}
        media = MediaIoBaseUpload(BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media).execute()
        print(f'File ID: {file.get("id")}')
    except HttpError as error:
        print(f'An error occurred: {error}')
        file = None

    return file

# Save the output to Google Drive
file_name = f"{topic}_guests.doc"
print(file_name)
save_to_google_drive(output, file_name)
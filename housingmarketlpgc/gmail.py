import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup


# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def gmail_authenticate(token_file, cred_file):
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")

    return service


# get the Gmail API service
# service = gmail_authenticate()


def list_messages(service, user_id, label, query=""):
    try:
        all_labels = service.users().labels().list(userId="me").execute()["labels"]
        label_id = "".join([d["id"] for d in all_labels if d["name"] in label])
        response = (
            service.users()
            .messages()
            .list(userId=user_id, q=query, labelIds=label_id)
            .execute()
        )
        messages = []
        if "messages" in response:
            messages.extend(response["messages"])

        while "nextPageToken" in response:
            page_token = response["nextPageToken"]
            response = (
                service.users()
                .messages()
                .list(userId=user_id, q=query, pageToken=page_token)
                .execute()
            )
            messages.extend(response["messages"])

        return messages
    except HttpError as error:
        # Again ,depends on error handling method, its a print command for this task
        print("An error occurred: %s" % error)


# id = '17a9d7494bdee5fe'


def get_email_details(service, msg_id):
    # service = gmail_authenticate()
    txt = service.users().messages().get(userId="me", id=msg_id).execute()

    # Get value of 'payload' from dictionary 'txt'
    payload = txt["payload"]
    headers = payload["headers"]

    # Look for Subject and Sender Email in the headers
    for d in headers:
        if d["name"] == "Subject":
            subject = d["value"]
        if d["name"] == "From":
            sender = d["value"]

    # The Body of the message is in Encrypted format. So, we have to decode it.
    # Get the data and decode it with base 64 decoder.
    parts = payload.get("parts")[0]
    data = parts["parts"][0]["body"]["data"]
    data = data.replace("-", "+").replace("_", "/")
    decoded_data = base64.b64decode(data).decode("utf-8")
    decoded_data = BeautifulSoup(decoded_data, "lxml")

    email_dict = {"subject": subject, "sender": sender, "body": decoded_data}

    return email_dict

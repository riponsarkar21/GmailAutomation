import os.path
import datetime
import tkinter as tk
from tkinter import ttk
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_emails_received_in_month(service, year, month):
    """Get the number of emails received in the specified month and year."""
    start_of_month = datetime.datetime(year, month, 1)
    
    # Calculate the start of the next month
    if month == 12:
        start_of_next_month = datetime.datetime(year + 1, 1, 1)
    else:
        start_of_next_month = datetime.datetime(year, month + 1, 1)

    # Format the dates in simple YYYY/MM/DD format
    start_of_month_str = start_of_month.strftime('%Y/%m/%d')
    start_of_next_month_str = start_of_next_month.strftime('%Y/%m/%d')

    print(f"Querying emails from {start_of_month_str} to {start_of_next_month_str}")

    try:
        # Query Gmail API for emails received in the specified month
        query = f"after:{start_of_month_str} before:{start_of_next_month_str}"
        response = service.users().messages().list(userId="me", q=query, maxResults=500).execute()

        # Get the count of emails
        emails = response.get("messages", [])
        num_emails = len(emails)

        # Print the query and number of emails found for debugging
        print(f"Query: {query}")
        print(f"Number of emails found: {num_emails}")

        return num_emails

    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)

        # Create a simple GUI to select month and year
        root = tk.Tk()
        root.title("Select Month and Year")

        tk.Label(root, text="Select Month:").grid(row=0, column=0)
        tk.Label(root, text="Select Year:").grid(row=1, column=0)

        month_var = tk.StringVar()
        year_var = tk.StringVar()

        month_combobox = ttk.Combobox(root, textvariable=month_var)
        month_combobox['values'] = [str(i) for i in range(1, 13)]
        month_combobox.grid(row=0, column=1)

        year_combobox = ttk.Combobox(root, textvariable=year_var)
        year_combobox['values'] = [str(i) for i in range(2000, datetime.datetime.now().year + 1)]
        year_combobox.grid(row=1, column=1)

        def on_submit():
            selected_month = int(month_var.get())
            selected_year = int(year_var.get())

            num_emails = get_emails_received_in_month(service, selected_year, selected_month)
            
            if num_emails is not None:
                result_label.config(text=f"Number of emails received: {num_emails}")
            else:
                result_label.config(text="Unable to retrieve the number of emails.")

        submit_button = tk.Button(root, text="Submit", command=on_submit)
        submit_button.grid(row=2, columnspan=2)

        result_label = tk.Label(root, text="")
        result_label.grid(row=3, columnspan=2)

        root.mainloop()

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()

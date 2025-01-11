import pandas as pd
import win32com.client 
from datetime import datetime, timedelta
# Connect to Outlook
outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
inbox = outlook.GetDefaultFolder(6) # 6 = refers to the Inbox folder

# Calculate the date for one week ago
last_week = datetime.now() - timedelta(days=7)
filter_string = "[ReceivedTime] >= '" + last_week.strftime("%m/%d/%Y") + "'"

# Apply filter to get emails from the last week
filtered_emails = inbox.Items.Restrict(filter_string)

# Extract and store email details, converting ReceivedTime to naive datetime if necessary
email_details = []
for email in filtered_emails:
    sender = email.SenderName
    received_time = email.ReceivedTime
    body = email.Body
    # Convert to naive datetime by removing timezone info
    if received_time.tzinfo is not None:
        received_time = received_time.replace(tzinfo=None)
        email_details.append((sender, received_time, body))

# Create a DataFrame
df = pd.DataFrame(email_details, columns=["Sender", "ReceivedTime", "Body"])

# Export to Excel
df.to_excel("emails_from_last_week.xlsx", index=False)

print("Emails exported successfully!")
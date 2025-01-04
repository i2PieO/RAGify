import win32com.client
from datetime import datetime


def connect_to_outlook():
    """Connect to Outlook application"""
    try:
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        return namespace
    except Exception as e:
        print(f"Error connecting to Outlook: {e}")
        return None


def get_inbox(namespace):
    """Get the inbox folder"""
    try:
        inbox = namespace.GetDefaultFolder(6)  # 6 is the index for the inbox folder
        return inbox
    except Exception as e:
        print(f"Error accessing inbox: {e}")
        return None


def parse_email(message):
    """Parse email content and return a structured dictionary"""
    email_data = {
        "subject": message.Subject,
        "sender": message.SenderName,
        "sender_email": message.SenderEmailAddress,
        "recipient": message.To,
        "cc": message.CC,
        "received_time": message.ReceivedTime.strftime("%Y-%m-%d %H:%M:%S"),
        "body": message.Body[:200],  # First 200 characters of the body
        "attachments": [attachment.FileName for attachment in message.Attachments]
    }
    return email_data


def read_emails(inbox, num_emails=10):
    """Read the specified number of emails from inbox and return structured data"""
    email_list = []
    try:
        messages = inbox.Items
        messages.Sort("[ReceivedTime]", True)

        for i, message in enumerate(messages):
            if i >= num_emails:
                break

            email_data = parse_email(message)
            email_list.append(email_data)

    except Exception as e:
        print(f"Error reading emails: {e}")

    return email_list


def main():
    # Connect to Outlook
    namespace = connect_to_outlook()
    if not namespace:
        return

    # Get inbox
    inbox = get_inbox(namespace)
    if not inbox:
        return

    # Read last 5 emails and store the results
    print("Reading the last 5 emails from your inbox...")
    emails = read_emails(inbox, 5)

    # Print email data in structured form
    for email in emails:
        print("\n" + "="*50)
        print(f"Subject: {email['subject']}")
        print(f"Sender: {email['sender']} <{email['sender_email']}>")
        print(f"Received: {email['received_time']}")
        print(f"Recipient(s): {email['recipient']}")
        print(f"CC: {email['cc']}")
        print(f"Body Preview: {email['body']}...")
        print(f"Attachments: {', '.join(email['attachments']) if email['attachments'] else 'None'}")


if __name__ == "__main__":
    main()

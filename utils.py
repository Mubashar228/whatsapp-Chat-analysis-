import pandas as pd
import re

def parse_chat(chat_lines):
    pattern = r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) ?(am|pm)? - ([^:]+): (.+)"
    data = []

    for line in chat_lines:
        line = line.strip().replace('\u202f', ' ').replace('\xa0', ' ')
        match = re.match(pattern, line)
        if match:
            date = match.group(1)
            time = match.group(2)
            ampm = match.group(3)
            sender = match.group(4)
            message = match.group(5)

            if ampm:
                time = f"{time} {ampm}"
            timestamp = f"{date} {time}"
            data.append([timestamp, sender, message])

    df = pd.DataFrame(data, columns=["Timestamp", "User", "Message"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)
    return df

def get_top_users(df, n=5):
    return df['User'].value_counts().head(n)

def get_daily_messages(df):
    df['Date'] = df['Timestamp'].dt.date
    return df.groupby('Date').count()['Message']

def get_hourly_messages(df):
    df['Hour'] = df['Timestamp'].dt.hour
    return df['Hour'].value_counts().sort_index()

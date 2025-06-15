import streamlit as st
import pandas as pd
import re
from io import StringIO

st.set_page_config(page_title="WhatsApp Chat Analyzer", layout="wide")
st.title("📱 WhatsApp Chat Analyzer")

# Upload file
uploaded_file = st.file_uploader("Upload WhatsApp Chat File (.txt)", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    chat = content.splitlines()

    # Regex pattern to extract messages
    pattern = r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) ?(am|pm)? - ([^:]+): (.+)"
    data = []

    for line in chat:
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

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Timestamp", "User", "Message"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce", dayfirst=True)

    st.success("✅ Chat successfully parsed!")
    st.write(df.head())

    # Top users
    st.subheader("👥 Top Users by Message Count")
    top_users = df['User'].value_counts().head()
    st.bar_chart(top_users)

    # Daily activity
    st.subheader("📅 Daily Messages")
    df['Date'] = df['Timestamp'].dt.date
    daily_messages = df.groupby('Date').count()['Message']
    st.line_chart(daily_messages)

    # Hourly activity
    st.subheader("⏰ Messages by Hour")
    df['Hour'] = df['Timestamp'].dt.hour
    st.bar_chart(df['Hour'].value_counts().sort_index())

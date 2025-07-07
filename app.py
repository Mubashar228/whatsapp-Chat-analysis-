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
    df.dropna(inplace=True)  # Drop rows with invalid timestamps

    st.success("✅ Chat successfully parsed!")
    st.write(df.head())

    # Top users
    st.subheader("👥 Top Users by Message Count")
    top_users = df['User'].value_counts().head()
    st.bar_chart(top_users)

    # Chat activity overview
    st.subheader("🗓️ Chat Activity Overview")
    agg_option = st.selectbox("Select Time Interval", ["Daily", "Weekly", "Monthly"])

    if agg_option == "Daily":
        df['Date'] = df['Timestamp'].dt.date
        daily_messages = df.groupby('Date')['Message'].count()
        st.line_chart(daily_messages)

        st.write("🔝 Top User Per Day")
        top_per_day = df.groupby(['Date', 'User'])['Message'].count().reset_index()
        top_user_day = top_per_day.loc[top_per_day.groupby('Date')['Message'].idxmax()]
        st.dataframe(top_user_day.rename(columns={'Date': 'Date', 'User': 'Top User', 'Message': 'Messages'}))

    elif agg_option == "Weekly":
        df['Week'] = df['Timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly_messages = df.groupby('Week')['Message'].count()
        st.bar_chart(weekly_messages)

        st.write("🔝 Top User Per Week")
        top_per_week = df.groupby(['Week', 'User'])['Message'].count().reset_index()
        top_user_week = top_per_week.loc[top_per_week.groupby('Week')['Message'].idxmax()]
        st.dataframe(top_user_week.rename(columns={'Week': 'Week Start', 'User': 'Top User', 'Message': 'Messages'}))

    elif agg_option == "Monthly":
        df['Month'] = df['Timestamp'].dt.to_period('M').astype(str)
        monthly_messages = df.groupby('Month')['Message'].count()
        st.bar_chart(monthly_messages)

        st.write("🔝 Top User Per Month")
        top_per_month = df.groupby(['Month', 'User'])['Message'].count().reset_index()
        top_user_month = top_per_month.loc[top_per_month.groupby('Month')['Message'].idxmax()]
        st.dataframe(top_user_month.rename(columns={'Month': 'Month', 'User': 'Top User', 'Message': 'Messages'}))

    # Hourly analysis
    st.subheader("⏰ Messages by Hour of Day")
    df['Hour'] = df['Timestamp'].dt.hour
    st.bar_chart(df['Hour'].value_counts().sort_index())

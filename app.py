import streamlit as st
import pandas as pd
import re
from io import StringIO
from datetime import datetime

st.set_page_config(page_title="📊 Advanced WhatsApp Chat Analyzer", layout="wide")
st.title("📱 Advanced WhatsApp Chat Analyzer")

uploaded_file = st.file_uploader("📁 Upload WhatsApp Chat (.txt)", type="txt")

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    chat_lines = content.splitlines()

    # Regex pattern
    pattern = r"^(\d{1,2}/\d{1,2}/\d{2,4}), (\d{1,2}:\d{2}) ?(AM|PM|am|pm)? - ([^:]+): (.+)"
    messages = []

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
            try:
                timestamp = pd.to_datetime(f"{date} {time}", dayfirst=True)
                messages.append([timestamp, sender, message])
            except:
                continue

    # DataFrame
    df = pd.DataFrame(messages, columns=["Timestamp", "User", "Message"])
    df.dropna(inplace=True)

    # Derived columns
    df['Date'] = df['Timestamp'].dt.date
    df['Week'] = df['Timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
    df['Month'] = df['Timestamp'].dt.to_period('M').astype(str)
    df['Hour'] = df['Timestamp'].dt.hour

    st.success("✅ Chat successfully parsed!")

    # Global stats
    st.header("📈 Group Summary")

    total_messages = df.shape[0]
    total_users = df['User'].nunique()
    media_msgs = df[df['Message'].str.lower().str.contains('<media omitted>')].shape[0]
    links = df['Message'].str.contains(r'http[s]?://', regex=True).sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Messages", total_messages)
    col2.metric("Unique Users", total_users)
    col3.metric("Media Messages", media_msgs)
    col4.metric("Links Shared", links)

    st.divider()

    # Select user for detailed analysis
    selected_user = st.selectbox("👤 Select a user for analysis", ['All'] + sorted(df['User'].unique()))

    user_df = df if selected_user == 'All' else df[df['User'] == selected_user]

    # Time aggregation
    st.subheader("🗓️ Activity Over Time")
    time_interval = st.radio("Select Interval", ["Daily", "Weekly", "Monthly"], horizontal=True)

    if time_interval == "Daily":
        msg_count = user_df.groupby('Date')['Message'].count()
        st.line_chart(msg_count)

    elif time_interval == "Weekly":
        msg_count = user_df.groupby('Week')['Message'].count()
        st.bar_chart(msg_count)

    elif time_interval == "Monthly":
        msg_count = user_df.groupby('Month')['Message'].count()
        st.bar_chart(msg_count)

    # Hourly activity
    st.subheader("⏰ Hourly Activity")
    hourly = user_df['Hour'].value_counts().sort_index()
    st.bar_chart(hourly)

    # Word count
    st.subheader("📝 Word Analysis")
    user_df['Word Count'] = user_df['Message'].apply(lambda x: len(x.split()))
    total_words = user_df['Word Count'].sum()
    avg_words = user_df['Word Count'].mean()
    st.write(f"🔤 Total Words: `{total_words}` | 📏 Average Words per Message: `{avg_words:.2f}`")

    # Most active users
    if selected_user == 'All':
        st.subheader("🏆 Most Active Users")
        active_users = df['User'].value_counts().head(10)
        st.bar_chart(active_users)

        st.subheader("📅 Top Users by Each Month")
        top_month_user = df.groupby(['Month', 'User'])['Message'].count().reset_index()
        top_month_user = top_month_user.loc[top_month_user.groupby('Month')['Message'].idxmax()]
        st.dataframe(top_month_user.rename(columns={'User': 'Top User', 'Message': 'Messages'}))

    # Message Table
    with st.expander("📄 Show Full Chat Table"):
        st.dataframe(user_df[['Timestamp', 'User', 'Message']].reset_index(drop=True))

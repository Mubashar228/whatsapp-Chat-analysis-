    # Select aggregation level
    st.subheader("🗓️ Chat Activity Overview")
    agg_option = st.selectbox("Select Time Interval", ["Daily", "Weekly", "Monthly"])

    if agg_option == "Daily":
        activity_df = df.groupby(df['Timestamp'].dt.date)['Message'].count()
        st.line_chart(activity_df)
        st.write("🔝 Top User Per Day")
        top_per_day = df.groupby([df['Timestamp'].dt.date, 'User']).count()['Message'].reset_index()
        top_user_day = top_per_day.loc[top_per_day.groupby('Timestamp')['Message'].idxmax()]
        st.dataframe(top_user_day.rename(columns={'Timestamp': 'Date'}))

    elif agg_option == "Weekly":
        df['Week'] = df['Timestamp'].dt.to_period('W').apply(lambda r: r.start_time)
        weekly = df.groupby('Week')['Message'].count()
        st.bar_chart(weekly)
        st.write("🔝 Top User Per Week")
        top_per_week = df.groupby([df['Week'], 'User']).count()['Message'].reset_index()
        top_user_week = top_per_week.loc[top_per_week.groupby('Week')['Message'].idxmax()]
        st.dataframe(top_user_week)

    elif agg_option == "Monthly":
        df['Month'] = df['Timestamp'].dt.to_period('M').astype(str)
        monthly = df.groupby('Month')['Message'].count()
        st.bar_chart(monthly)
        st.write("🔝 Top User Per Month")
        top_per_month = df.groupby(['Month', 'User']).count()['Message'].reset_index()
        top_user_month = top_per_month.loc[top_per_month.groupby('Month')['Message'].idxmax()]
        st.dataframe(top_user_month)

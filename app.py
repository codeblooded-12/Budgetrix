import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AI Budget Advisor", layout="wide")

st.title("💰 BUDGETRIX ")

# ==============================
# 📂 Upload CSV
# ==============================
uploaded_file = st.file_uploader("Upload your expense CSV file", type=["csv"])

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    # Ensure correct format
    df["Date"] = pd.to_datetime(df["Date"])
    df["Amount"] = pd.to_numeric(df["Amount"])

    # ==============================
    # 📅 Budget Settings
    # ==============================
    st.sidebar.header("📅 Monthly Budget Settings")

    if "budget" not in st.session_state:
        st.session_state.budget = 0.0

    if "month_start" not in st.session_state:
        st.session_state.month_start = 1

    st.session_state.budget = st.sidebar.number_input(
        "Enter Monthly Budget (₹)",
        min_value=0.0,
        value=st.session_state.budget
    )

    
    # ==============================
    # 📊 Monthly Calculation
    # ==============================
    today = datetime.today()

    if today.day >= st.session_state.month_start:
        start_date = datetime(today.year, today.month, st.session_state.month_start)
    else:
        if today.month == 1:
            start_date = datetime(today.year - 1, 12, st.session_state.month_start)
        else:
            start_date = datetime(today.year, today.month - 1, st.session_state.month_start)

    monthly_df = df[df["Date"] >= start_date]

    month_spending = monthly_df["Amount"].sum()
    remaining = st.session_state.budget - month_spending

    # ==============================
    # 💳 Budget Display
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("💸 Total Spent This Month", f"₹{round(month_spending,2)}")
    col2.metric("💰 Remaining Budget", f"₹{round(remaining,2)}")
   

    # ==============================
    # ⭐ SAFE DAILY SPEND LIMIT
    # ==============================
    if st.session_state.budget > 0:

        days_passed = (today - start_date).days + 1
        days_in_cycle = 30
        days_remaining = days_in_cycle - days_passed

        if days_remaining > 0:
            safe_daily_limit = remaining / days_remaining
        else:
            safe_daily_limit = 0

        st.info(f"⭐ Safe Daily Spend Limit: ₹{round(safe_daily_limit,2)} per day")

    # ==============================
    # 📊 Interactive Spending Chart
    # ==============================
    st.subheader("📈 Daily Spending Trend")

    daily = monthly_df.groupby("Date")["Amount"].sum().reset_index()

    fig = px.bar(
        daily,
        x="Date",
        y="Amount",
        title="Daily Spending",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # ==============================
    # 📊 Category Breakdown
    # ==============================
    st.subheader("📊 Category Breakdown")

    category_totals = monthly_df.groupby("Category")["Amount"].sum().reset_index()

    pie = px.pie(
        category_totals,
        names="Category",
        values="Amount",
        title="Spending by Category",
        hole=0.4
    )

    st.plotly_chart(pie, use_container_width=True)

    # ==============================
    # 🧠 AI FINANCIAL INSIGHTS
    # ==============================
    st.subheader("🧠 AI Smart Financial Suggestions")

    insights = []
    total_spent = category_totals["Amount"].sum()

    if total_spent > 0:

        top_row = category_totals.loc[category_totals["Amount"].idxmax()]
        top_category = top_row["Category"]
        top_amount = top_row["Amount"]
        top_percent = (top_amount / total_spent) * 100

        insights.append(f"📌 Highest spending category is **{top_category}** ({round(top_percent,1)}% of total spending).")

        potential_save = top_amount * 0.4
        insights.append(f"💡 You could save approximately ₹{round(potential_save,2)} if you reduce {top_category} expenses by 40%.")

    # Spike detection (last 3 days)
    if len(daily) > 5:
        recent_avg = daily.tail(3)["Amount"].mean()
        overall_avg = daily["Amount"].mean()

        if recent_avg > overall_avg * 1.5:
            insights.append("⚠️ There is a recent spike in spending in the last 3 days.")

    # Travel spike
    if "Travel" in category_totals["Category"].values:
        travel_avg = monthly_df[monthly_df["Category"] == "Travel"]["Amount"].mean()
        if travel_avg > monthly_df["Amount"].mean() * 1.3:
            insights.append("✈️ Travelling expenses are unusually high this month.")

    # Food suggestion
    if "Food" in category_totals["Category"].values:
        food_avg = monthly_df[monthly_df["Category"] == "Food"]["Amount"].mean()
        three_day_saving = food_avg * 3
        insights.append(f"🍽️ Avoiding outside food for 3 days could save around ₹{round(three_day_saving,2)}.")

    # Budget warning
    if st.session_state.budget > 0:
        if month_spending > st.session_state.budget * 0.8:
            insights.append("🚨 You have already used more than 80% of your monthly budget.")
        if month_spending > st.session_state.budget:
            insights.append("❌ You have exceeded your monthly budget.")

    # Safe daily warning
    if st.session_state.budget > 0 and days_remaining > 0:
        today_spend = daily[daily["Date"] == daily["Date"].max()]["Amount"].sum()
        if today_spend > safe_daily_limit:
            insights.append("⚠️ Today's spending exceeded your safe daily limit.")

    if insights:
        for tip in insights:
            st.write(tip)
    else:
        st.success("✅ Your spending pattern looks balanced this month!")

else:
    st.warning("Please upload a CSV file to begin.")

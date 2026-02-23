import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AI Budget Advisor", layout="wide")

st.title("💰 BUDGETRIX ")

# ==============================
# 📦 Initialize Data Storage
# ==============================
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount"]
    )

if "budget" not in st.session_state:
    st.session_state.budget = 0.0

if "month_start" not in st.session_state:
    st.session_state.month_start = 1


# ==============================
# ➕ Add Expense Section
# ==============================
st.sidebar.header("➕ Add New Expense")

expense_date = st.sidebar.date_input("Date", datetime.today())
expense_category = st.sidebar.selectbox(
    "Category",
    ["Food", "Travel", "Shopping", "Bills", "Entertainment", "Other"]
)
expense_amount = st.sidebar.number_input("Amount (₹)", min_value=0.0)

if st.sidebar.button("Add Expense"):
    new_data = pd.DataFrame({
        "Date": [expense_date],
        "Category": [expense_category],
        "Amount": [expense_amount]
    })

    st.session_state.expenses = pd.concat(
        [st.session_state.expenses, new_data],
        ignore_index=True
    )

    st.sidebar.success("Expense Added!")


# ==============================
# 📅 Budget Settings
# ==============================
st.sidebar.header("📅 Monthly Budget Settings")

st.session_state.budget = st.sidebar.number_input(
    "Enter Monthly Budget (₹)",
    min_value=0.0,
    value=st.session_state.budget
)





    # ==============================
    # 📊 Monthly Filtering
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
    # 💳 Budget Metrics
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("💸 Total Spent This Month", f"₹{round(month_spending,2)}")
    col2.metric("💰 Remaining Budget", f"₹{round(remaining,2)}")
    

    # ==============================
    # ⭐ Safe Daily Limit
    # ==============================
    if st.session_state.budget > 0:
        days_passed = (today - start_date).days + 1
        days_remaining = 30 - days_passed

        if days_remaining > 0:
            safe_daily_limit = remaining / days_remaining
        else:
            safe_daily_limit = 0

        st.info(f"⭐ Safe Daily Spend Limit: ₹{round(safe_daily_limit,2)} per day")

    # ==============================
    # 📊 Daily Spending Chart
    # ==============================
    st.subheader("📈 Daily Spending")

    daily = monthly_df.groupby("Date")["Amount"].sum().reset_index()

    fig = px.bar(daily, x="Date", y="Amount", title="Daily Spending")
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
        hole=0.4,
        title="Spending by Category"
    )

    st.plotly_chart(pie, use_container_width=True)

    # ==============================
    # 🧠 AI Financial Insights
    # ==============================
    st.subheader("🧠 AI Smart Suggestions")

    insights = []
    total_spent = category_totals["Amount"].sum()

    if total_spent > 0:
        top_row = category_totals.loc[category_totals["Amount"].idxmax()]
        top_category = top_row["Category"]
        top_amount = top_row["Amount"]
        top_percent = (top_amount / total_spent) * 100

        insights.append(
            f"📌 Highest spending category is {top_category} ({round(top_percent,1)}%)."
        )

        potential_save = top_amount * 0.4
        insights.append(
            f"💡 You could save ₹{round(potential_save,2)} by reducing {top_category} expenses by 40%."
        )

    if len(daily) > 5:
        recent_avg = daily.tail(3)["Amount"].mean()
        overall_avg = daily["Amount"].mean()

        if recent_avg > overall_avg * 1.5:
            insights.append("⚠️ Recent spending spike detected.")

    if st.session_state.budget > 0:
        if month_spending > st.session_state.budget * 0.8:
            insights.append("🚨 You have used more than 80% of your budget.")
        if month_spending > st.session_state.budget:
            insights.append("❌ You have exceeded your monthly budget.")

    if insights:
        for tip in insights:
            st.write(tip)
    else:
        st.success("✅ Your spending looks balanced this month.")

    # ==============================
    # 📋 Show Expense Table
    # ==============================
    st.subheader("📋 All Expenses")
    st.dataframe(df)

else:
    st.info("Add expenses from the sidebar to get started.")

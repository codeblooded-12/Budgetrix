import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import calendar

st.set_page_config(page_title="AI Budget Advisor", layout="wide")

st.title("💰 BUDGETRIX ")

# ==============================
# 📦 Initialize Storage
# ==============================
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(
        columns=["Date", "Category", "Amount"]
    )

if "budget" not in st.session_state:
    st.session_state.budget = 0.0


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
# 💰 Monthly Budget Setting
# ==============================
st.sidebar.header("💰 Monthly Budget")

st.session_state.budget = st.sidebar.number_input(
    "Enter Monthly Budget (₹)",
    min_value=0.0,
    value=st.session_state.budget
)


df = st.session_state.expenses.copy()

if not df.empty:

    df["Date"] = pd.to_datetime(df["Date"])

    # ==============================
    # 📅 Filter Current Month
    # ==============================
    today = datetime.today()
    current_month = today.month
    current_year = today.year

    monthly_df = df[
        (df["Date"].dt.month == current_month) &
        (df["Date"].dt.year == current_year)
    ]

    month_spending = monthly_df["Amount"].sum()
    remaining = st.session_state.budget - month_spending

    # ==============================
    # 📊 Budget Metrics
    # ==============================
    col1, col2, col3 = st.columns(3)

    col1.metric("💸 Total Spent This Month", f"₹{round(month_spending,2)}")
    col2.metric("💰 Remaining Budget", f"₹{round(remaining,2)}")
    col3.metric("📅 Current Month", today.strftime("%B %Y"))

    # ==============================
    # ⭐ Safe Daily Spend Limit
    # ==============================
    if st.session_state.budget > 0:

        total_days = calendar.monthrange(current_year, current_month)[1]
        days_passed = today.day
        days_remaining = total_days - days_passed

        if days_remaining > 0:
            safe_daily_limit = remaining / days_remaining
        else:
            safe_daily_limit = 0

        st.info(f"⭐ Safe Daily Spend Limit: ₹{round(safe_daily_limit,2)} per day")

    # ==============================
    # 📈 Daily Spending Chart
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

    if not category_totals.empty:
        pie = px.pie(
            category_totals,
            names="Category",
            values="Amount",
            hole=0.4,
            title="Spending by Category"
        )

        st.plotly_chart(pie, use_container_width=True)

    # ==============================
    # 🧠 AI Smart Suggestions
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
    st.dataframe(monthly_df)

else:
    st.info("Add expenses from the sidebar to get started.")

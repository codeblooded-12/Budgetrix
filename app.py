import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Budgetrix Finance AI", layout="wide")

st.title("💰 Budgetrix – AI Finance Dashboard")

DATA_FILE = "expenses.csv"

# ---------- LOAD DATA ----------
try:
    df = pd.read_csv(DATA_FILE)
except:
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Note"])
    df.to_csv(DATA_FILE, index=False)

if df.empty:
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Note"])

df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

# ==============================
# 💳 BUDGET SETTINGS
# ==============================
st.subheader("💳 Monthly Budget Settings")

if "budget" not in st.session_state:
    st.session_state.budget = 0.0

if "month_start" not in st.session_state:
    st.session_state.month_start = 1

col1, col2 = st.columns(2)

with col1:
    st.session_state.budget = st.number_input(
        "Set Monthly Budget (₹)",
        min_value=0.0,
        value=st.session_state.budget,
        step=100.0
    )

with col2:
    st.session_state.month_start = st.number_input(
        "Month Starts On (Day of Month)",
        min_value=1,
        max_value=28,
        value=st.session_state.month_start
    )

# ==============================
# ➕ ADD EXPENSE
# ==============================
st.subheader("➕ Add Expense")

col1, col2 = st.columns(2)

with col1:
    amount = st.number_input("Amount ₹", min_value=0.0, step=1.0)
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])

with col2:
    note = st.text_input("Note")

if st.button("Add Expense"):
    new_row = pd.DataFrame(
        [[pd.Timestamp.today(), amount, category, note]],
        columns=["Date", "Amount", "Category", "Note"]
    )
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    st.success("✅ Expense added successfully!")

# Stop if no meaningful data
if df.empty or df["Amount"].sum() == 0:
    st.info("No expenses added yet. Add your first expense to unlock analytics 🚀")
    st.stop()

df = df.dropna(subset=["Date"])

# ==============================
# 📊 BUDGET CALCULATION
# ==============================
if st.session_state.budget > 0:

    today = pd.Timestamp.today()

    if today.day >= st.session_state.month_start:
        period_start = pd.Timestamp(
            year=today.year,
            month=today.month,
            day=st.session_state.month_start
        )
    else:
        previous_month = today.month - 1 if today.month > 1 else 12
        year_adjust = today.year if today.month > 1 else today.year - 1

        period_start = pd.Timestamp(
            year=year_adjust,
            month=previous_month,
            day=st.session_state.month_start
        )

    month_spending = df[df["Date"] >= period_start]["Amount"].sum()
    remaining = st.session_state.budget - month_spending
    percent_used = (month_spending / st.session_state.budget) * 100

    st.subheader("📊 Budget Status")

    col1, col2 = st.columns(2)
    col1.metric("💸 Spent This Period", f"₹ {round(month_spending,2)}")
    col2.metric("💰 Remaining Budget", f"₹ {round(remaining,2)}")

    st.progress(min(int(percent_used), 100))

    if remaining < 0:
        st.error("🚨 You have exceeded your budget!")
    elif remaining < st.session_state.budget * 0.2:
        st.warning("⚠️ You are close to exceeding your budget.")
    else:
        st.success("✅ You are within your budget.")

# ==============================
# 📈 DAILY AGGREGATION
# ==============================
daily = df.groupby(df["Date"].dt.date)["Amount"].sum().reset_index()
daily.columns = ["Date", "Amount"]

# ==============================
# 🔮 AI PREDICTION
# ==============================
if len(daily) > 7:
    daily["prev_day"] = daily["Amount"].shift(1)
    daily["rolling_avg"] = daily["Amount"].rolling(7).mean()
    daily = daily.dropna()

    if not daily.empty:
        X = daily[["prev_day", "rolling_avg"]]
        y = daily["Amount"]

        model = RandomForestRegressor(n_estimators=200, random_state=42)
        model.fit(X, y)

        latest = daily.iloc[-1]
        prediction = model.predict([[latest["prev_day"], latest["rolling_avg"]]])[0]

        st.metric("🔮 Predicted Tomorrow Spending", f"₹ {round(prediction,2)}")

# ==============================
# 📊 INTERACTIVE PLOTLY BAR CHART
# ==============================
st.subheader("📊 Interactive Daily Spending")

fig = px.bar(
    daily,
    x="Date",
    y="Amount",
    title="Daily Spending Overview",
    text_auto=True
)

st.plotly_chart(fig, use_container_width=True)

# ==============================
# 🥧 CATEGORY PIE CHART (Interactive)
# ==============================
st.subheader("🥧 Spending by Category")

category_data = df.groupby("Category")["Amount"].sum().reset_index()

fig2 = px.pie(
    category_data,
    names="Category",
    values="Amount",
    title="Category Distribution"
)

st.plotly_chart(fig2, use_container_width=True)

# ==============================
# 📅 DATE FILTER
# ==============================
st.subheader("📅 Filter by Date")

min_date = df["Date"].min()
max_date = df["Date"].max()

start_date = st.date_input("Start Date", min_date)
end_date = st.date_input("End Date", max_date)

filtered_df = df[(df["Date"].dt.date >= start_date) &
                 (df["Date"].dt.date <= end_date)]

st.dataframe(filtered_df.sort_values("Date", ascending=False))

# ==============================
# 📥 DOWNLOAD BUTTON
# ==============================
st.download_button(
    label="📥 Download Expense Data",
    data=df.to_csv(index=False),
    file_name="expenses_export.csv",
    mime="text/csv"
)

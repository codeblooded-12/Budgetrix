import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor

st.set_page_config(page_title="Budgetrix Finance AI", layout="wide")

st.title("💰 BUDGETRIX ")

DATA_FILE = "expenses.csv"

# ---------- Load Data Safely ----------
try:
    df = pd.read_csv(DATA_FILE)
except:
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Note"])
    df.to_csv(DATA_FILE, index=False)

if df.empty:
    df = pd.DataFrame(columns=["Date", "Amount", "Category", "Note"])

# Convert Date safely
df["Date"] = pd.to_datetime(df.get("Date"), errors="coerce")

# ---------- Add Expense ----------
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

# ---------- Stop If No Data ----------
if df.empty or df["Amount"].sum() == 0:
    st.info("No expenses added yet. Add your first expense to unlock analytics 🚀")
    st.stop()

# Remove invalid dates
df = df.dropna(subset=["Date"])

# ---------- Daily Aggregation (SAFE) ----------
daily = df.groupby(df["Date"].dt.date)["Amount"].sum().reset_index()

if daily.empty:
    st.info("Not enough valid data yet.")
    st.stop()

daily.columns = ["Date", "Amount"]

# ---------- AI Prediction ----------
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

# ---------- Spending Chart ----------
st.subheader("📊 Spending Trend")

fig, ax = plt.subplots()
ax.plot(daily["Date"], daily["Amount"])
ax.set_ylabel("Amount (₹)")
ax.set_xlabel("Date")
plt.xticks(rotation=45)
st.pyplot(fig)

# ---------- Raw Data ----------
st.subheader("📂 Expense History")
st.dataframe(df.sort_values("Date", ascending=False))


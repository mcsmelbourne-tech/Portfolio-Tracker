import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Stock Portfolio & Trade Tracker", page_icon="📈", layout="wide"
)

DATA_FILE = "portfolio_trades.csv"


@st.cache_data
def load_data():
  try:
    return pd.read_csv(DATA_FILE)
  except FileNotFoundError:
    df = pd.DataFrame(
        columns=[
            "ID",
            "Date",
            "Ticker",
            "Type",
            "Quantity",
            "Buy Price",
            "Sell Price",
            "Status",
        ]
    )
    df.to_csv(DATA_FILE, index=False)
    return df


def save_data(df):
  df.to_csv(DATA_FILE, index=False)


def fetch_current_price(ticker):
  try:
    stock = yf.Ticker(ticker)
    todays_data = stock.history(period="1d")
    if not todays_data.empty:
      return round(todays_data["Close"].iloc[-1], 2)
  except Exception:
    pass
  return None


st.title("📈 Stock Portfolio & Trade Tracker")
st.markdown(
    "Track your active and closed trades, live market performance, and"
    " portfolio metrics."
)

df = load_data()

# Sidebar: Add New Trade Form
st.sidebar.header("➕ Add New Trade")
with st.sidebar.form("trade_form", clear_on_submit=True):
  trade_date = st.date_input("Trade Date", datetime.date.today())
  ticker = st.text_input("Ticker Symbol (e.g., AAPL, TSLA, BHP.AX)", "").upper()
  trade_type = st.selectbox("Type", ["Buy/Long", "Sell/Short"])
  quantity = st.number_input("Quantity", min_value=0.01, value=10.0, step=1.0)
  buy_price = st.number_input(
      "Buy Price ($)", min_value=0.01, value=100.0, step=0.1
  )
  status = st.selectbox("Status", ["Active", "Closed"])

  sell_price = 0.0
  if status == "Closed":
    sell_price = st.number_input(
        "Sell Price ($)", min_value=0.0, value=105.0, step=0.1
    )

  submitted = st.form_submit_button("Add Trade")

  if submitted:
    if not ticker:
      st.sidebar.error("Please enter a ticker symbol.")
    else:
      new_id = (
          int(df["ID"].max()) + 1
          if not df.empty and "ID" in df.columns and pd.notna(df["ID"].max())
          else 1
      )
      new_row = pd.DataFrame({
          "ID": [new_id],
          "Date": [str(trade_date)],
          "Ticker": [ticker],
          "Type": [trade_type],
          "Quantity": [quantity],
          "Buy Price": [buy_price],
          "Sell Price": [sell_price if status == "Closed" else 0.0],
          "Status": [status],
      })
      # Prepend new row so it appears at the top of the table
      df = pd.concat([new_row, df], ignore_index=True)
      save_data(df)
      st.sidebar.success(f"Trade for {ticker} added successfully!")
      st.rerun()

if not df.empty:
  if "ID" in df.columns:
    df = df.sort_values(by="ID", ascending=False).reset_index(drop=True)

  # Calculations for live prices and profits
  current_prices = []
  current_values = []
  profits = []
  profit_pcts = []

  for idx, row in df.iterrows():
    t_ticker = row["Ticker"]
    qty = float(row["Quantity"])
    b_price = float(row["Buy Price"])
    s_price = float(row["Sell Price"])
    t_status = row["Status"]

    if t_status == "Active":
      c_price = fetch_current_price(t_ticker)
      if c_price is None:
        c_price = b_price
      curr_val = qty * c_price
      profit = (c_price - b_price) * qty
      profit_pct = ((c_price - b_price) / b_price) * 100 if b_price > 0 else 0
    else:
      c_price = s_price
      curr_val = qty * s_price
      profit = (s_price - b_price) * qty
      profit_pct = ((s_price - b_price) / b_price) * 100 if b_price > 0 else 0

    current_prices.append(c_price)
    current_values.append(curr_val)
    profits.append(round(profit, 2))
    profit_pcts.append(round(profit_pct, 2))

  df["Current Price"] = current_prices
  df["Current Value"] = current_values
  df["Profit/Loss ($)"] = profits
  df["Profit/Loss (%)"] = profit_pcts

  # Summary Metrics Dashboard
  active_df = df[df["Status"] == "Active"]
  total_invested = (
      (active_df["Quantity"] * active_df["Buy Price"]).sum()
      if not active_df.empty
      else 0
  )
  total_current_val = (
      active_df["Current Value"].sum() if not active_df.empty else 0
  )
  total_profit = df["Profit/Loss ($)"].sum()

  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Active Trades", len(active_df))
  col2.metric("Total Invested", f"${total_invested:,.2f}")
  col3.metric("Current Portfolio Value", f"${total_current_val:,.2f}")
  col4.metric(
      "Total Profit / Loss",
      f"${total_profit:,.2f}",
      delta=f"${total_profit:,.2f}",
  )

  st.markdown("---")

  # Tabs for navigation
  tab1, tab2, tab3 = st.tabs(
      ["📋 Trade Ledger", "📊 Charts & Analytics", "⚙️ Manage Trades"]
  )

  with tab1:
    st.subheader("All Trades (Newest on Top)")
    st.dataframe(df, use_container_width=True)

  with tab2:
    col_a, col_b = st.columns(2)

    with col_a:
      st.subheader("Profit / Loss per Trade")
      if not df.empty:
        fig_bar = px.bar(
            df,
            x="Ticker",
            y="Profit/Loss ($)",
            color="Profit/Loss ($)",
            color_continuous_scale=["red", "green"],
            title="Profit / Loss by Ticker",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
      st.subheader("Portfolio Allocation")
      if not active_df.empty:
        fig_pie = px.pie(
            active_df,
            names="Ticker",
            values="Current Value",
            title="Active Asset Allocation",
        )
        st.plotly_chart(fig_pie, use_container_width=True)
      else:
        st.info("No active trades available for allocation chart.")

  with tab3:
    st.subheader("Delete a Trade Record")
    trade_to_delete = st.selectbox(
        "Select Trade ID to Delete", df["ID"].tolist() if not df.empty else []
    )
    if st.button("Delete Trade"):
      df = df[df["ID"] != trade_to_delete]
      save_data(df)
      st.success(f"Trade ID {trade_to_delete} deleted successfully!")
      st.rerun()

else:
  st.info("No trades recorded yet. Use the sidebar to add your first trade!")

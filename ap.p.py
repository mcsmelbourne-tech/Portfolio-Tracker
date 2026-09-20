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


def load_data():
  try:
    df = pd.read_csv(DATA_FILE)
    expected_columns = [
        "ID",
        "Date",
        "Ticker",
        "Type",
        "Quantity",
        "Buy Price",
        "Sell Price",
        "Status",
    ]
    for col in expected_columns:
      if col not in df.columns:
        df[col] = []
    return df
  except (FileNotFoundError, pd.errors.EmptyDataError):
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


df = load_data()

# Ensure correct sorting: Newest trades on top
if not df.empty and "ID" in df.columns:
  df = df.sort_values(by="ID", ascending=False).reset_index(drop=True)

# Calculations for live prices and profits if df is not empty
starting_capital = 0.0
total_profit = 0.0
current_capital = 0.0
active_df = pd.DataFrame()

if not df.empty:
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

  active_df = df[df["Status"] == "Active"]
  starting_capital = (df["Quantity"] * df["Buy Price"]).sum()
  total_profit = df["Profit/Loss ($)"].sum()
  current_capital = starting_capital + total_profit

# --- HEADER SECTION WITH CAPITAL METRICS RIGHT NEXT TO TITLE ---
head_col1, head_col2, head_col3, head_col4 = st.columns([2, 1, 1, 1])
with head_col1:
  st.title("📈 Stock Portfolio & Trade Tracker")
with head_col2:
  st.metric("Starting Capital", f"${starting_capital:,.2f}")
with head_col3:
  st.metric("Total Profit", f"${total_profit:,.2f}", delta=f"${total_profit:,.2f}")
with head_col4:
  st.metric("Current Capital", f"${current_capital:,.2f}")

st.markdown(
    "Manage your trades, view live market prices, and monitor capital and"
    " performance."
)
st.markdown("---")

# --- DASHBOARD SECTION: ADD NEW TRADE ---
with st.expander("➕ Add New Trade", expanded=df.empty):
  with st.form("trade_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
      trade_date = st.date_input("Trade Date", datetime.date.today())
      ticker = st.text_input(
          "Ticker Symbol (e.g., AAPL, TSLA, BHP.AX)", ""
      ).upper()
    with col2:
      trade_type = st.selectbox("Type", ["Buy/Long", "Sell/Short"])
      quantity = st.number_input("Quantity", min_value=0.01, value=10.0, step=1.0)
    with col3:
      buy_price = st.number_input(
          "Buy Price ($)", min_value=0.01, value=100.0, step=0.1
      )
      status = st.selectbox("Status", ["Active", "Closed"])

    sell_price = 0.0
    if status == "Closed":
      sell_price = st.number_input(
          "Sell Price ($)", min_value=0.0, value=105.0, step=0.1
      )

    submitted = st.form_submit_button("Save Trade to Dashboard")

    if submitted:
      if not ticker:
        st.error("Please enter a ticker symbol.")
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
        df = pd.concat([new_row, df], ignore_index=True)
        save_data(df)
        st.success(f"Trade for {ticker} added successfully!")
        st.rerun()

st.markdown("---")

if not df.empty:
  # Additional secondary overview metrics
  m1, m2, m3 = st.columns(3)
  m1.metric("Active Trades", len(active_df))
  m2.metric(
      "Active Market Value",
      (
          f"${active_df['Current Value'].sum():,.2f}"
          if not active_df.empty
          else "$0.00"
      ),
  )
  m3.metric("Total Trades Recorded", len(df))

  st.markdown("---")

  # Main Dashboard Tabs
  tab1, tab2, tab3 = st.tabs(
      [
          "📋 Trade Ledger & Live Prices",
          "📊 Analytics & Capital Pie Charts",
          "🗑️ Delete Trades",
      ]
  )

  with tab1:
    st.subheader("Active & Closed Trades (Newest on Top)")
    st.dataframe(df, use_container_width=True)

  with tab2:
    col_a, col_b = st.columns(2)
    with col_a:
      st.subheader("Profit / Loss per Ticker")
      fig_bar = px.bar(
          df,
          x="Ticker",
          y="Profit/Loss ($)",
          color="Profit/Loss ($)",
          color_continuous_scale=["red", "green"],
      )
      st.plotly_chart(fig_bar, use_container_width=True)

    with col_b:
      st.subheader("Capital vs. Profit Composition")
      if starting_capital > 0:
        pie_data = pd.DataFrame({
            "Category": ["Starting Capital", "Net Profit / Loss"],
            "Amount": [starting_capital, total_profit],
        })
        fig_pie_cap = px.pie(
            pie_data,
            names="Category",
            values="Amount",
            title="Capital Breakdown",
            hole=0.3,
        )
        st.plotly_chart(fig_pie_cap, use_container_width=True)
      else:
        st.info("Insufficient data for capital composition pie chart.")

    st.markdown("---")
    st.subheader("Active Asset Allocation")
    if not active_df.empty:
      fig_pie_alloc = px.pie(
          active_df,
          names="Ticker",
          values="Current Value",
          title="Active Ticker Allocation",
          hole=0.3,
      )
      st.plotly_chart(fig_pie_alloc, use_container_width=True)
    else:
      st.info("No active trades available for asset allocation chart.")

  with tab3:
    st.subheader("Manage / Delete Trades")
    trade_to_delete = st.selectbox(
        "Select Trade ID to Delete", df["ID"].tolist()
    )
    if st.button("Delete Selected Trade", type="primary"):
      df_stored = pd.read_csv(DATA_FILE)
      df_stored = df_stored[df_stored["ID"] != trade_to_delete]
      save_data(df_stored)
      st.success(f"Trade ID {trade_to_delete} deleted successfully!")
      st.rerun()

else:
  st.info(
      "No trades recorded yet. Use the **'➕ Add New Trade'** section above to"
      " add your first trade!"
  )

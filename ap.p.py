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
  expected_columns = [
      "ID",
      "Date",
      "Ticker",
      "Market",
      "Type",
      "Quantity",
      "Buy Price",
      "Sell Price",
      "Status",
  ]
  try:
    df = pd.read_csv(DATA_FILE)
    # Check if any expected columns are missing and add them safely with default empty/null values
    for col in expected_columns:
      if col not in df.columns:
        df[col] = None
    return df
  except (FileNotFoundError, pd.errors.EmptyDataError):
    df = pd.DataFrame(columns=expected_columns)
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

# Calculations for live prices, profits, and market categorizations
india_start = india_profit = india_current = 0.0
usa_start = usa_profit = usa_current = 0.0
cfd_start = cfd_profit = cfd_current = 0.0

if not df.empty:
  current_prices = []
  current_values = []
  profits = []
  profit_pcts = []
  flags = []
  markets = []

  for idx, row in df.iterrows():
    raw_ticker = str(row["Ticker"]).upper()
    # Clean up ticker string if it already contains a flag emoji from previous saves
    t_ticker = (
        raw_ticker.split(" ")[-1] if " " in raw_ticker else raw_ticker
    )
    qty = float(row["Quantity"]) if pd.notna(row["Quantity"]) else 0.0
    b_price = float(row["Buy Price"]) if pd.notna(row["Buy Price"]) else 0.0
    s_price = float(row["Sell Price"]) if pd.notna(row["Sell Price"]) else 0.0
    t_status = str(row["Status"])

    existing_market = (
        row["Market"] if "Market" in df.columns and pd.notna(row["Market"]) else ""
    )

    if (
        "NS" in t_ticker
        or "BO" in t_ticker
        or existing_market == "India (INR)"
    ):
      market = "India (INR)"
      flag = "🇮🇳"
    elif ".AX" in t_ticker or existing_market == "CFD (AUD)":
      market = "CFD (AUD)"
      flag = "🇦🇺"
    else:
      market = "USA (USD)"
      flag = "🇺🇸"

    markets.append(market)
    flags.append(f"{flag} {t_ticker}")

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

  df["Market"] = markets
  df["Ticker"] = flags  # Displays flag directly with the ticker symbol
  df["Current Price"] = current_prices
  df["Current Value"] = current_values
  df["Profit/Loss ($)"] = profits
  df["Profit/Loss (%)"] = profit_pcts

  # Calculate segregated metrics
  india_df = df[df["Market"] == "India (INR)"]
  usa_df = df[df["Market"] == "USA (USD)"]
  cfd_df = df[df["Market"] == "CFD (AUD)"]

  if not india_df.empty:
    india_start = (india_df["Quantity"] * india_df["Buy Price"]).sum()
    india_profit = india_df["Profit/Loss ($)"].sum()
    india_current = india_start + india_profit

  if not usa_df.empty:
    usa_start = (usa_df["Quantity"] * usa_df["Buy Price"]).sum()
    usa_profit = usa_df["Profit/Loss ($)"].sum()
    usa_current = usa_start + usa_profit

  if not cfd_df.empty:
    cfd_start = (cfd_df["Quantity"] * cfd_df["Buy Price"]).sum()
    cfd_profit = cfd_df["Profit/Loss ($)"].sum()
    cfd_current = cfd_start + cfd_profit

# --- HEADER SECTION ---
st.title("📈 Stock Portfolio & Trade Tracker")
st.markdown(
    "Multi-market tracker partitioned by USA, India, and Australian CFD assets."
)
st.markdown("---")

# --- SEGREGATED CAPITAL METRICS DISPLAY ---
st.subheader("🌍 Regional Capital & Profit Overview")
col_ind, col_usa, col_cfd = st.columns(3)

with col_ind:
  st.markdown("### 🇮🇳 India Market")
  st.metric("Starting Capital", f"₹{india_start:,.2f}")
  st.metric(
      "Net Profit / Loss",
      f"₹{india_profit:,.2f}",
      delta=f"₹{india_profit:,.2f}",
  )
  st.metric("Current Capital", f"₹{india_current:,.2f}")

with col_usa:
  st.markdown("### 🇺🇸 USA Market")
  st.metric("Starting Capital", f"${usa_start:,.2f}")
  st.metric(
      "Net Profit / Loss", f"${usa_profit:,.2f}", delta=f"${usa_profit:,.2f}"
  )
  st.metric("Current Capital", f"${usa_current:,.2f}")

with col_cfd:
  st.markdown("### 🇦🇺 CFD Market (Australia)")
  st.metric("Starting Capital", f"${cfd_start:,.2f}")
  st.metric(
      "Net Profit / Loss", f"${cfd_profit:,.2f}", delta=f"${cfd_profit:,.2f}"
  )
  st.metric("Current Capital", f"${cfd_current:,.2f}")

st.markdown("---")

# --- DASHBOARD SECTION: ADD NEW TRADE ---
with st.expander("➕ Add New Trade", expanded=df.empty):
  with st.form("trade_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
      trade_date = st.date_input("Trade Date", datetime.date.today())
      ticker = st.text_input(
          "Ticker Symbol (e.g., AAPL, RELIANCE.NS, BHP.AX)", ""
      ).upper()
    with col2:
      market_selection = st.selectbox(
          "Market / Currency Group", ["USA (USD)", "India (INR)", "CFD (AUD)"]
      )
      trade_type = st.selectbox("Type", ["Buy/Long", "Sell/Short"])
    with col3:
      quantity = st.number_input("Quantity", min_value=0.01, value=10.0, step=1.0)
      buy_price = st.number_input(
          "Buy Price", min_value=0.01, value=100.0, step=0.1
      )

    status = st.selectbox("Status", ["Active", "Closed"])
    sell_price = 0.0
    if status == "Closed":
      sell_price = st.number_input(
          "Sell Price", min_value=0.0, value=105.0, step=0.1
      )

    submitted = st.form_submit_button("Save Trade to Dashboard")

    if submitted:
      if not ticker:
        st.error("Please enter a ticker symbol.")
      else:
        # Load raw stored data to append correctly without duplicate flag labels
        raw_df = load_data()
        new_id = (
            int(raw_df["ID"].max()) + 1
            if not raw_df.empty
            and "ID" in raw_df.columns
            and pd.notna(raw_df["ID"].max())
            else 1
        )
        new_row = pd.DataFrame({
            "ID": [new_id],
            "Date": [str(trade_date)],
            "Ticker": [ticker.strip().upper()],
            "Market": [market_selection],
            "Type": [trade_type],
            "Quantity": [quantity],
            "Buy Price": [buy_price],
            "Sell Price": [sell_price if status == "Closed" else 0.0],
            "Status": [status],
        })
        raw_df = pd.concat([new_row, raw_df], ignore_index=True)
        save_data(raw_df)
        st.success(f"Trade for {ticker} added successfully!")
        st.rerun()

st.markdown("---")

if not df.empty:
  # Main Dashboard Tabs
  tab1, tab2, tab3 = st.tabs(
      [
          "📋 Trade Ledger & Live Prices",
          "📊 Regional Analytics & Charts",
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
      st.subheader("Capital Distribution by Market")
      market_alloc = (
          df.groupby("Market")["Current Value"].sum().reset_index()
      )
      if not market_alloc.empty:
        fig_pie_market = px.pie(
            market_alloc,
            names="Market",
            values="Current Value",
            title="Portfolio Split Across Regions",
            hole=0.3,
        )
        st.plotly_chart(fig_pie_market, use_container_width=True)
      else:
        st.info("No market valuation data available for pie chart.")

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
      " get started!"
  )

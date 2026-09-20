import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Stock Portfolio & Trade Tracker", page_icon="📈", layout="wide"
)

# Custom CSS for compact metrics & broker-style dark layout styling
st.markdown("""
    <style>
        h3 { font-size: 1.1rem !important; }
        div[data-testid="stMetricValue"] { font-size: 1.15rem !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.75rem !important; }
    </style>
""", unsafe_allow_html=True)

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

global_invested = 0.0
global_current_val = 0.0
global_unrealised_pl = 0.0
global_realised_pl = 0.0

broker_display_rows = []

if not df.empty:
  for idx, row in df.iterrows():
    raw_ticker = str(row["Ticker"]).upper()
    t_ticker = raw_ticker.split(" ")[-1] if " " in raw_ticker else raw_ticker
    qty = float(row["Quantity"]) if pd.notna(row["Quantity"]) else 0.0
    b_price = float(row["Buy Price"]) if pd.notna(row["Buy Price"]) else 0.0
    s_price = float(row["Sell Price"]) if pd.notna(row["Sell Price"]) else 0.0
    t_status = str(row["Status"])
    t_type = str(row["Type"])

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
      curr_symbol = "₹"
    elif ".AX" in t_ticker or existing_market == "CFD (AUD)":
      market = "CFD (AUD)"
      flag = "🇦🇺"
      curr_symbol = "$"
    else:
      market = "USA (USD)"
      flag = "🇺🇸"
      curr_symbol = "$"

    # Fetch live LTP (Last Traded Price)
    if t_status == "Active":
      c_price = fetch_current_price(t_ticker)
      if c_price is None:
        c_price = b_price
      inv_val = qty * b_price
      curr_val = qty * c_price
      pl = (c_price - b_price) * qty
      pl_pct = ((c_price - b_price) / b_price) * 100 if b_price > 0 else 0
      global_invested += inv_val
      global_current_val += curr_val
      global_unrealised_pl += pl
    else:
      c_price = s_price
      inv_val = qty * b_price
      curr_val = qty * s_price
      pl = (s_price - b_price) * qty
      pl_pct = ((s_price - b_price) / b_price) * 100 if b_price > 0 else 0
      global_realised_pl += pl

    broker_display_rows.append({
        "ID": row["ID"],
        "Symbol": f"{flag} {t_ticker}",
        "Action": t_type,
        "Qty": qty,
        "Avg Price": f"{curr_symbol}{b_price:,.2f}",
        "LTP": f"{curr_symbol}{c_price:,.2f}",
        "Investment Value": f"{curr_symbol}{inv_val:,.2f}",
        "Current Value": f"{curr_symbol}{curr_val:,.2f}",
        "Unrealised P&L": f"{curr_symbol}{pl:,.2f}",
        "Unrealised P&L %": f"{pl_pct:,.2f}%",
        "Market": market,
        "Raw P&L": pl,
        "Raw Inv": inv_val,
        "Raw Curr": curr_val,
    })

  display_df = pd.DataFrame(broker_display_rows)

  india_df = display_df[display_df["Market"] == "India (INR)"]
  usa_df = display_df[display_df["Market"] == "USA (USD)"]
  cfd_df = display_df[display_df["Market"] == "CFD (AUD)"]

  if not india_df.empty:
    india_start = india_df["Raw Inv"].sum()
    india_profit = india_df["Raw P&L"].sum()
    india_current = india_start + india_profit

  if not usa_df.empty:
    usa_start = usa_df["Raw Inv"].sum()
    usa_profit = usa_df["Raw P&L"].sum()
    usa_current = usa_start + usa_profit

  if not cfd_df.empty:
    cfd_start = cfd_df["Raw Inv"].sum()
    cfd_profit = cfd_df["Raw P&L"].sum()
    cfd_current = cfd_start + cfd_profit

# --- TOP BROKER SUMMARY BANNER ---
st.title("📈 Stock Portfolio & Trade Tracker")
st.markdown("---")

if not df.empty:
  col_s1, col_s2, col_s3, col_s4 = st.columns(4)
  with col_s1:
    st.metric("Invested Value", f"${global_invested:,.2f}")
  with col_s2:
    st.metric("Current Value", f"${global_current_val:,.2f}")
  with col_s3:
    unreal_pct = (
        (global_unrealised_pl / global_invested) * 100
        if global_invested > 0
        else 0
    )
    st.metric(
        "Unrealised P&L",
        f"${global_unrealised_pl:,.2f}",
        delta=f"{unreal_pct:.2f}%",
    )
  with col_s4:
    st.metric("Realised P&L", f"${global_realised_pl:,.2f}")

  st.markdown("---")

# --- REGIONAL METRICS & PIE CHARTS ---
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
          "📋 Broker Trade Ledger",
          "📊 Regional Analytics & Charts",
          "🗑️ Delete Trades",
      ]
  )

  with tab1:
    st.subheader("📋 Active & Closed Broker Ledger")
    # Display clean broker columns layout excluding raw helper columns
    cols_to_display = [
        "ID",
        "Symbol",
        "Action",
        "Qty",
        "Avg Price",
        "LTP",
        "Investment Value",
        "Current Value",
        "Unrealised P&L",
        "Unrealised P&L %",
    ]
    st.dataframe(display_df[cols_to_display], use_container_width=True)

  with tab2:
    st.subheader("📊 Individual Market Breakdown Charts")
    chart_col1, chart_col2, chart_col3 = st.columns(3)

    with chart_col1:
      st.markdown("##### 🇮🇳 India Allocation")
      if not india_df.empty:
        fig_ind = px.pie(
            india_df, names="Symbol", values="Raw Curr", hole=0.3
        )
        st.plotly_chart(fig_ind, use_container_width=True)
      else:
        st.info("No India trades.")

    with chart_col2:
      st.markdown("##### 🇺🇸 USA Allocation")
      if not usa_df.empty:
        fig_usa = px.pie(usa_df, names="Symbol", values="Raw Curr", hole=0.3)
        st.plotly_chart(fig_usa, use_container_width=True)
      else:
        st.info("No USA trades.")

    with chart_col3:
      st.markdown("##### 🇦🇺 CFD Allocation")
      if not cfd_df.empty:
        fig_cfd = px.pie(cfd_df, names="Symbol", values="Raw Curr", hole=0.3)
        st.plotly_chart(fig_cfd, use_container_width=True)
      else:
        st.info("No CFD trades.")

    st.markdown("---")
    st.subheader("Overall Profit / Loss per Symbol")
    fig_bar = px.bar(
        display_df,
        x="Symbol",
        y="Raw P&L",
        color="Raw P&L",
        color_continuous_scale=["red", "green"],
        labels={"Raw P&L": "Profit/Loss ($)"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)

  with tab3:
    st.subheader("Manage / Delete Trades")
    trade_to_delete = st.selectbox("Select Trade ID to Delete", df["ID"].tolist())
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

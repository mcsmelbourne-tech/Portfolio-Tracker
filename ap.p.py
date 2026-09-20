import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="Stock Portfolio & Trade Tracker", page_icon="📈", layout="wide"
)

# Custom CSS for compact metrics & fonts
st.markdown("""
    <style>
        h3 { font-size: 1.0rem !important; }
        h4 { font-size: 0.9rem !important; }
        div[data-testid="stMetricValue"] { font-size: 1.05rem !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.7rem !important; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "portfolio_trades.csv"
CAPITAL_FILE = "market_capitals.csv"


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


def load_manual_capitals():
  try:
    cdf = pd.read_csv(CAPITAL_FILE)
    return {
        row["Market"]: float(row["Starting Capital"]) for _, row in cdf.iterrows()
    }
  except Exception:
    return {"India (INR)": 0.0, "USA (USD)": 0.0, "CFD (AUD)": 0.0}


def save_manual_capitals(caps):
  cdf = pd.DataFrame(
      list(caps.items()), columns=["Market", "Starting Capital"]
  )
  cdf.to_csv(CAPITAL_FILE, index=False)


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
manual_caps = load_manual_capitals()

# Ensure correct sorting: Newest trades on top
if not df.empty and "ID" in df.columns:
  df = df.sort_values(by="ID", ascending=False).reset_index(drop=True)

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

  india_profit = india_df["Raw P&L"].sum() if not india_df.empty else 0.0
  india_current = (
      manual_caps.get("India (INR)", 0.0)
      + india_df["Raw Curr"].sum()
      if not india_df.empty
      else manual_caps.get("India (INR)", 0.0)
  )

  usa_profit = usa_df["Raw P&L"].sum() if not usa_df.empty else 0.0
  usa_current = (
      manual_caps.get("USA (USD)", 0.0) + usa_df["Raw Curr"].sum()
      if not usa_df.empty
      else manual_caps.get("USA (USD)", 0.0)
  )

  cfd_profit = cfd_df["Raw P&L"].sum() if not cfd_df.empty else 0.0
  cfd_current = (
      manual_caps.get("CFD (AUD)", 0.0) + cfd_df["Raw Curr"].sum()
      if not cfd_df.empty
      else manual_caps.get("CFD (AUD)", 0.0)
  )
else:
  display_df = pd.DataFrame()
  india_df = usa_df = cfd_df = pd.DataFrame()
  india_profit = usa_profit = cfd_profit = 0.0
  india_current = manual_caps.get("India (INR)", 0.0)
  usa_current = manual_caps.get("USA (USD)", 0.0)
  cfd_current = manual_caps.get("CFD (AUD)", 0.0)

# --- HEADER SECTION ---
st.title("📈 Stock Portfolio & Trade Tracker")
st.markdown("---")

# --- CAPITAL CONFIGURATION EXPANDER ---
with st.expander("⚙️ Set / Update Starting Capital for Markets"):
  with st.form("capital_form"):
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
      new_ind_cap = st.number_input(
          "🇮🇳 India Starting Capital (₹)",
          min_value=0.0,
          value=manual_caps.get("India (INR)", 0.0),
          step=1000.0,
      )
    with c_col2:
      new_usa_cap = st.number_input(
          "🇺🇸 USA Starting Capital ($)",
          min_value=0.0,
          value=manual_caps.get("USA (USD)", 0.0),
          step=100.0,
      )
    with c_col3:
      new_cfd_cap = st.number_input(
          "🇦🇺 CFD Starting Capital ($)",
          min_value=0.0,
          value=manual_caps.get("CFD (AUD)", 0.0),
          step=100.0,
      )

    cap_submitted = st.form_submit_button("Save Starting Capitals")
    if cap_submitted:
      updated_caps = {
          "India (INR)": new_ind_cap,
          "USA (USD)": new_usa_cap,
          "CFD (AUD)": new_cfd_cap,
      }
      save_manual_capitals(updated_caps)
      st.success("Starting capitals updated successfully!")
      st.rerun()

# --- TOP BROKER SUMMARY BANNER ---
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

# --- REGIONAL METRICS & PIE CHARTS SIDE-BY-SIDE ---
st.subheader("🌍 Regional Capital & Profit Overview")

market_cols = st.columns(3)

markets_data = [
    (
        "🇮🇳 India Market",
        "₹",
        manual_caps.get("India (INR)", 0.0),
        india_profit,
        india_current,
        india_df,
    ),
    (
        "🇺🇸 USA Market",
        "$",
        manual_caps.get("USA (USD)", 0.0),
        usa_profit,
        usa_current,
        usa_df,
    ),
    (
        "🇦🇺 CFD Market (Australia)",
        "$",
        manual_caps.get("CFD (AUD)", 0.0),
        cfd_profit,
        cfd_current,
        cfd_df,
    ),
]

for col, (m_title, curr, start_c, profit_c, curr_c, m_df) in zip(
    market_cols, markets_data
):
  with col:
    st.markdown(f"### {m_title}")
    sub_col1, sub_col2 = st.columns([1.2, 0.8])

    with sub_col1:
      st.metric("Starting Capital", f"{curr}{start_c:,.2f}")
      st.metric(
          "Net Profit / Loss",
          f"{curr}{profit_c:,.2f}",
          delta=f"{curr}{profit_c:,.2f}",
      )
      st.metric("Current Capital", f"{curr}{curr_c:,.2f}")

    with sub_col2:
      if not m_df.empty:
        fig_mini = px.pie(
            m_df, names="Symbol", values="Raw Curr", hole=0.4
        )
        fig_mini.update_layout(
            showlegend=False,
            margin=dict(t=10, b=10, l=10, r=10),
            height=140,
        )
        st.plotly_chart(
            fig_mini, use_container_width=True, config={"displayModeBar": False}
        )
      else:
        st.caption("No allocation")

st.markdown("---")

# --- DASHBOARD SECTION: ADD NEW TRADE & EXCEL IMPORT ---
with st.expander("➕ Add New Trade / Import from Excel", expanded=df.empty):
  tab_single, tab_excel = st.tabs(["Manual Entry", "📥 Import from Excel"])

  with tab_single:
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
        quantity = st.number_input(
            "Quantity", min_value=0.01, value=10.0, step=1.0
        )
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

  with tab_excel:
    st.markdown(
        "Upload an Excel file (`.xlsx`) containing your trades. The file"
        " should ideally include columns: **Date, Ticker, Market, Type,"
        " Quantity, Buy Price, Sell Price, Status**."
    )
    uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
    if uploaded_file is not None:
      try:
        imported_df = pd.read_excel(uploaded_file)
        st.write("Preview of imported data:", imported_df.head())

        if st.button("Confirm and Append Trades"):
          raw_df = load_data()
          start_id = (
              int(raw_df["ID"].max()) + 1
              if not raw_df.empty
              and "ID" in raw_df.columns
              and pd.notna(raw_df["ID"].max())
              else 1
          )

          # Normalize / map columns if needed
          expected_cols = [
              "Date",
              "Ticker",
              "Market",
              "Type",
              "Quantity",
              "Buy Price",
              "Sell Price",
              "Status",
          ]
          for col in expected_cols:
            if col not in imported_df.columns:
              imported_df[col] = (
                  ""
                  if col in ["Date", "Ticker", "Market", "Type", "Status"]
                  else 0.0
              )

          processed_rows = []
          curr_id = start_id
          for _, row in imported_df.iterrows():
            processed_rows.append({
                "ID": curr_id,
                "Date": str(row.get("Date", datetime.date.today())),
                "Ticker": str(row.get("Ticker", "")).strip().upper(),
                "Market": str(
                    row.get("Market", "USA (USD)")
                ),  # default fallback
                "Type": str(row.get("Type", "Buy/Long")),
                "Quantity": float(row.get("Quantity", 1.0)),
                "Buy Price": float(row.get("Buy Price", 0.0)),
                "Sell Price": float(row.get("Sell Price", 0.0)),
                "Status": str(row.get("Status", "Active")),
            })
            curr_id += 1

          new_import_df = pd.DataFrame(processed_rows)
          combined_df = pd.concat([new_import_df, raw_df], ignore_index=True)
          save_data(combined_df)
          st.success(
              f"Successfully imported {len(new_import_df)} trades from Excel!"
          )
          st.rerun()
      except Exception as e:
        st.error(f"Error reading Excel file: {e}")

st.markdown("---")

if not df.empty:
  tab1, tab2, tab3 = st.tabs(
      [
          "📋 Broker Trade Ledger",
          "📊 Regional Analytics & Charts",
          "🗑️ Delete Trades",
      ]
  )

  with tab1:
    st.subheader("📋 Active & Closed Broker Ledger")
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
      "No trades recorded yet. Use the **'➕ Add New Trade / Import from"
      " Excel'** section above to get started!"
  )

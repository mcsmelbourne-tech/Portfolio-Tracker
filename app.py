import datetime
import pandas as pd
import plotly.express as px
import streamlit as st
import yfinance as yf

# Page configuration
st.set_page_config(
    page_title="QuantFx -Stock Portfolio & Trade Tracker", page_icon="📈", layout="wide"
)

# Custom CSS for compact metrics, fonts, and positive/negative colors
st.markdown("""
    <style>
        h3 { font-size: 1.1rem !important; }
        h4 { font-size: 1.0rem !important; }
        div[data-testid="stMetricValue"] { font-size: 1.15rem !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
        .profit-green { color: #00FF66; font-weight: bold; }
        .loss-red { color: #FF3333; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

DATA_FILE = "portfolio_trades.csv"
CAPITAL_FILE = "market_capitals.csv"


def get_default_portfolio():
    data = [
        [
            1,
            "2026-01-01",
            "ACC.NS",
            "India (INR)",
            "Buy/Long",
            20,
            1753.02,
            1259.70,
            "Active",
        ],
        [
            2,
            "2026-01-01",
            "ABFRL.NS",
            "India (INR)",
            "Buy/Long",
            100,
            262.26,
            50.16,
            "Active",
        ],
        [
            3,
            "2026-01-01",
            "ALKEM.NS",
            "India (INR)",
            "Buy/Long",
            13,
            6143.80,
            5466.50,
            "Active",
        ],
        [
            4,
            "2026-01-01",
            "AMBER.NS",
            "India (INR)",
            "Buy/Long",
            2,
            6179.41,
            7125.00,
            "Active",
        ],
        [
            5,
            "2026-01-01",
            "BAJAJHLDNG.NS",
            "India (INR)",
            "Buy/Long",
            7,
            10688.22,
            11282.00,
            "Active",
        ],
        [
            6,
            "2026-01-01",
            "BAJAJHFL.NS",
            "India (INR)",
            "Buy/Long",
            400,
            170.20,
            85.58,
            "Active",
        ],
        [
            7,
            "2026-01-01",
            "BRITANNIA.NS",
            "India (INR)",
            "Buy/Long",
            15,
            5790.26,
            4998.00,
            "Active",
        ],
        [
            8,
            "2026-01-01",
            "BSE.NS",
            "India (INR)",
            "Buy/Long",
            222,
            196.34,
            3266.40,
            "Active",
        ],
        [
            9,
            "2026-01-01",
            "CIPLA.NS",
            "India (INR)",
            "Buy/Long",
            20,
            1685.85,
            1394.50,
            "Active",
        ],
        [
            10,
            "2026-01-01",
            "ESCORTS.NS",
            "India (INR)",
            "Buy/Long",
            10,
            4077.02,
            2798.20,
            "Active",
        ],
        [
            11,
            "2026-01-01",
            "EXIDEIND.NS",
            "India (INR)",
            "Buy/Long",
            100,
            490.60,
            435.85,
            "Active",
        ],
        [
            12,
            "2026-01-01",
            "GODREJPROP.NS",
            "India (INR)",
            "Buy/Long",
            20,
            3003.02,
            1691.10,
            "Active",
        ],
        [
            13,
            "2026-01-01",
            "GUJENERGY.NS",
            "India (INR)",
            "Buy/Long",
            150,
            566.07,
            244.64,
            "Active",
        ],
        [
            14,
            "2026-01-01",
            "HDFCGOLD.NS",
            "India (INR)",
            "Buy/Long",
            1100,
            130.24,
            130.64,
            "Active",
        ],
        [
            15,
            "2026-01-01",
            "HDFCSILVER.NS",
            "India (INR)",
            "Buy/Long",
            600,
            252.13,
            223.95,
            "Active",
        ],
        [
            16,
            "2026-01-01",
            "IRFC.NS",
            "India (INR)",
            "Buy/Long",
            400,
            175.11,
            81.50,
            "Active",
        ],
        [
            17,
            "2026-01-01",
            "ITCHOTELS.NS",
            "India (INR)",
            "Buy/Long",
            20,
            282.44,
            158.80,
            "Active",
        ],
        [
            18,
            "2026-01-01",
            "JUBLFOOD.NS",
            "India (INR)",
            "Buy/Long",
            100,
            631.22,
            500.00,
            "Active",
        ],
        [
            19,
            "2026-01-01",
            "LTM.NS",
            "India (INR)",
            "Buy/Long",
            40,
            4775.26,
            4275.10,
            "Active",
        ],
        [
            20,
            "2026-01-01",
            "M&MFIN.NS",
            "India (INR)",
            "Buy/Long",
            100,
            362.81,
            353.30,
            "Active",
        ],
        [
            21,
            "2026-01-01",
            "MPHASIS.NS",
            "India (INR)",
            "Buy/Long",
            20,
            2940.22,
            2300.40,
            "Active",
        ],
        [
            22,
            "2026-01-01",
            "OIL.NS",
            "India (INR)",
            "Buy/Long",
            150,
            569.03,
            475.70,
            "Active",
        ],
        [
            23,
            "2026-01-01",
            "RVNL.NS",
            "India (INR)",
            "Buy/Long",
            150,
            485.14,
            214.29,
            "Active",
        ],
        [
            24,
            "2026-01-01",
            "RAILTEL.NS",
            "India (INR)",
            "Buy/Long",
            75,
            441.79,
            265.00,
            "Active",
        ],
        [
            25,
            "2026-01-01",
            "SBIN.NS",
            "India (INR)",
            "Buy/Long",
            300,
            250.12,
            996.20,
            "Active",
        ],
        [
            26,
            "2026-01-01",
            "TCS.NS",
            "India (INR)",
            "Buy/Long",
            40,
            3446.86,
            2105.00,
            "Active",
        ],
        [
            27,
            "2026-01-01",
            "TATAELXSI.NS",
            "India (INR)",
            "Buy/Long",
            10,
            5636.02,
            3266.70,
            "Active",
        ],
        [
            28,
            "2026-01-01",
            "TMCV.NS",
            "India (INR)",
            "Buy/Long",
            150,
            163.37,
            442.90,
            "Active",
        ],
        [
            29,
            "2026-01-01",
            "TMPV.NS",
            "India (INR)",
            "Buy/Long",
            150,
            361.09,
            303.80,
            "Active",
        ],
        [
            30,
            "2026-01-01",
            "TATASTEEL.NS",
            "India (INR)",
            "Buy/Long",
            850,
            40.29,
            185.54,
            "Active",
        ],
        [
            31,
            "2026-01-01",
            "VBL.NS",
            "India (INR)",
            "Buy/Long",
            100,
            601.82,
            421.95,
            "Active",
        ],
        [
            32,
            "2026-01-01",
            "WIPRO.NS",
            "India (INR)",
            "Buy/Long",
            62,
            210.30,
            166.83,
            "Active",
        ],
    ]
    columns = [
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
    return pd.DataFrame(data, columns=columns)


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
                df[col] = "Active" if col == "Status" else None
        if df.empty:
            df = get_default_portfolio()
            df.to_csv(DATA_FILE, index=False)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        df = get_default_portfolio()
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
global_total_pl = 0.0
global_realised_pl = 0.0

broker_display_rows = []

if not df.empty:
    for idx, row in df.iterrows():
        raw_ticker = str(row["Ticker"]).upper()
        t_ticker = raw_ticker.split(" ")[-1] if " " in raw_ticker else raw_ticker
        qty = float(row["Quantity"]) if pd.notna(row["Quantity"]) else 0.0
        b_price = float(row["Buy Price"]) if pd.notna(row["Buy Price"]) else 0.0
        s_price = float(row["Sell Price"]) if pd.notna(row["Sell Price"]) else 0.0
        t_status = (
            str(row["Status"]) if pd.notna(row["Status"]) else "Active"
        )
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
                c_price = (
                    float(row["Sell Price"])
                    if pd.notna(row["Sell Price"]) and float(row["Sell Price"]) > 0
                    else b_price
                )
            inv_val = qty * b_price
            curr_val = qty * c_price
            pl = (c_price - b_price) * qty
            pl_pct = ((c_price - b_price) / b_price) * 100 if b_price > 0 else 0
            global_invested += inv_val
            global_current_val += curr_val
            global_total_pl += pl
        else:  # Cancelled
            c_price = s_price if s_price > 0 else b_price
            inv_val = qty * b_price
            curr_val = qty * c_price
            pl = (c_price - b_price) * qty if s_price > 0 else 0.0
            pl_pct = (
                ((c_price - b_price) / b_price) * 100
                if b_price > 0 and s_price > 0
                else 0.0
            )
            global_realised_pl += pl
            global_total_pl += pl

        broker_display_rows.append({
            "ID": row["ID"],
            "Symbol": f"{flag} {t_ticker}",
            "CleanTicker": t_ticker,
            "Action": t_type,
            "Qty": qty,
            "Avg Price": f"{curr_symbol}{b_price:,.2f}",
            "LTP": f"{curr_symbol}{c_price:,.2f}",
            "Status": t_status,
            "Investment Value": f"{curr_symbol}{inv_val:,.2f}",
            "Current Value": f"{curr_symbol}{curr_val:,.2f}",
            "Total P&L": f"{curr_symbol}{pl:,.2f}",
            "Total P&L %": f"{pl_pct:,.2f}%",
            "Market": market,
            "Raw P&L": pl,
            "Raw P&L %": pl_pct,
            "Raw Inv": inv_val,
            "Raw Curr": curr_val,
        })

    display_df = pd.DataFrame(broker_display_rows)

    india_df = display_df[display_df["Market"] == "India (INR)"]
    usa_df = display_df[display_df["Market"] == "USA (USD)"]
    cfd_df = display_df[display_df["Market"] == "CFD (AUD)"]

    india_profit = india_df["Raw P&L"].sum() if not india_df.empty else 0.0
    india_active_inv = (
        india_df[india_df["Status"] == "Active"]["Raw Inv"].sum()
        if not india_df.empty
        else 0.0
    )
    india_cancelled_returns = (
        india_df[india_df["Status"] == "Cancelled"]["Raw Inv"].sum()
        + india_df[india_df["Status"] == "Cancelled"]["Raw P&L"].sum()
        if not india_df.empty
        else 0.0
    )
    india_remaining_cap = max(
        0.0,
        manual_caps.get("India (INR)", 0.0)
        - india_active_inv
        + india_cancelled_returns,
    )
    india_current = (
        india_remaining_cap
        + india_df[india_df["Status"] == "Active"]["Raw Curr"].sum()
        if not india_df.empty
        else india_remaining_cap
    )

    usa_profit = usa_df["Raw P&L"].sum() if not usa_df.empty else 0.0
    usa_active_inv = (
        usa_df[usa_df["Status"] == "Active"]["Raw Inv"].sum()
        if not usa_df.empty
        else 0.0
    )
    usa_cancelled_returns = (
        usa_df[usa_df["Status"] == "Cancelled"]["Raw Inv"].sum()
        + usa_df[usa_df["Status"] == "Cancelled"]["Raw P&L"].sum()
        if not usa_df.empty
        else 0.0
    )
    usa_remaining_cap = max(
        0.0,
        manual_caps.get("USA (USD)", 0.0)
        - usa_active_inv
        + usa_cancelled_returns,
    )
    usa_current = (
        usa_remaining_cap
        + usa_df[usa_df["Status"] == "Active"]["Raw Curr"].sum()
        if not usa_df.empty
        else usa_remaining_cap
    )

    cfd_profit = cfd_df["Raw P&L"].sum() if not cfd_df.empty else 0.0
    cfd_active_inv = (
        cfd_df[cfd_df["Status"] == "Active"]["Raw Inv"].sum()
        if not cfd_df.empty
        else 0.0
    )
    cfd_cancelled_returns = (
        cfd_df[cfd_df["Status"] == "Cancelled"]["Raw Inv"].sum()
        + cfd_df[cfd_df["Status"] == "Cancelled"]["Raw P&L"].sum()
        if not cfd_df.empty
        else 0.0
    )
    cfd_remaining_cap = max(
        0.0,
        manual_caps.get("CFD (AUD)", 0.0)
        - cfd_active_inv
        + cfd_cancelled_returns,
    )
    cfd_current = (
        cfd_remaining_cap
        + cfd_df[cfd_df["Status"] == "Active"]["Raw Curr"].sum()
        if not cfd_df.empty
        else cfd_remaining_cap
    )
else:
    display_df = pd.DataFrame()
    india_df = usa_df = cfd_df = pd.DataFrame()
    india_profit = usa_profit = cfd_profit = 0.0
    india_remaining_cap = manual_caps.get("India (INR)", 0.0)
    usa_remaining_cap = manual_caps.get("USA (USD)", 0.0)
    cfd_remaining_cap = manual_caps.get("CFD (AUD)", 0.0)
    india_current = india_remaining_cap
    usa_current = usa_remaining_cap
    cfd_current = cfd_remaining_cap

# --- HEADER SECTION ---
st.title("📈 QuantFx - Stock Portfolio & Trade Tracker")
st.markdown("---")

# --- CAPITAL CONFIGURATION EXPANDER ---
with st.expander(
    "⚙️ Set / Update Starting Capital for Markets", expanded=False
):
    c_col1, c_col2, c_col3 = st.columns(3)
    with c_col1:
        new_ind_cap = st.number_input(
            "🇮🇳 India Starting Capital (₹)",
            min_value=0.0,
            value=manual_caps.get("India (INR)", 0.0),
            step=1000.0,
            key="input_ind_cap",
        )
    with c_col2:
        new_usa_cap = st.number_input(
            "🇺🇸 USA Starting Capital ($)",
            min_value=0.0,
            value=manual_caps.get("USA (USD)", 0.0),
            step=100.0,
            key="input_usa_cap",
        )
    with c_col3:
        new_cfd_cap = st.number_input(
            "🇦🇺 CFD Starting Capital ($)",
            min_value=0.0,
            value=manual_caps.get("CFD (AUD)", 0.0),
            step=100.0,
            key="input_cfd_cap",
        )

    if st.button("Save Starting Capitals"):
        updated_caps = {
            "India (INR)": new_ind_cap,
            "USA (USD)": new_usa_cap,
            "CFD (AUD)": new_cfd_cap,
        }
        save_manual_capitals(updated_caps)
        st.success("Starting capitals saved permanently!")
        st.rerun()

# --- TOP BROKER SUMMARY BANNER ---
if not df.empty:
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.metric("Invested Value", f"${global_invested:,.2f}")
    with col_s2:
        st.metric("Current Value", f"${global_current_val:,.2f}")
    with col_s3:
        total_pct = (
            (global_total_pl / global_invested) * 100
            if global_invested > 0
            else 0
        )
        st.metric(
            "Total P&L",
            f"${global_total_pl:,.2f}",
            delta=f"{total_pct:.2f}%",
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
        india_remaining_cap,
        india_profit,
        india_current,
        india_df,
    ),
    (
        "🇺🇸 USA Market",
        "$",
        usa_remaining_cap,
        usa_profit,
        usa_current,
        usa_df,
    ),
    (
        "🇦🇺 CFD Market (Australia)",
        "$",
        cfd_remaining_cap,
        cfd_profit,
        cfd_current,
        cfd_df,
    ),
]

for col, (m_title, curr, rem_c, profit_c, curr_c, m_df) in zip(
    market_cols, markets_data
):
    with col:
        st.markdown(f"### {m_title}")
        sub_col1, sub_col2 = st.columns([1.2, 0.8])

        with sub_col1:
            st.metric(
                "Remaining Cash",
                f"{curr}{rem_c:,.2f}",
                help="Starting Capital minus Active Investments plus Cancelled Returns",
            )
            
            p_color_class = "profit-green" if profit_c >= 0 else "loss-red"
            st.markdown(f"**Net Profit / Loss**<br><span class='{p_color_class}' style='font-size:1.15rem;'>{curr}{profit_c:,.2f}</span>", unsafe_allow_html=True)
            
            st.metric("Total Market Value", f"{curr}{curr_c:,.2f}")

        with sub_col2:
            if not m_df.empty:
                active_m_df = m_df[m_df["Status"] == "Active"]
                if not active_m_df.empty:
                    fig_mini = px.pie(
                        active_m_df, names="Symbol", values="Raw Curr", hole=0.4
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
                    st.caption("No active trades")
            else:
                st.caption("No allocation")

st.markdown("---")

# --- DASHBOARD SECTION: ADD NEW TRADE & FILE IMPORT ---
with st.expander("➕ Add New Trade / Import from File", expanded=df.empty):
    tab_single, tab_excel = st.tabs(["Manual Entry", "📥 Import from File"])

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

            status = st.selectbox("Status", ["Active", "Cancelled"])
            sell_price = 0.0

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
                        "Sell Price": [sell_price],
                        "Status": [status],
                    })
                    raw_df = pd.concat([new_row, raw_df], ignore_index=True)
                    save_data(raw_df)
                    st.success(f"Trade for {ticker} added successfully!")
                    st.rerun()

    with tab_excel:
        st.markdown(
            "Upload file (`.csv` or `.xlsx`) containing your trades."
        )
        uploaded_file = st.file_uploader(
            "Choose a file", type=["csv", "xlsx", "xls"]
        )
        if uploaded_file is not None:
            try:
                if uploaded_file.name.endswith(".csv"):
                    imported_df = pd.read_csv(uploaded_file)
                else:
                    try:
                        imported_df = pd.read_excel(uploaded_file, engine="openpyxl")
                    except Exception:
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

                    processed_rows = []
                    curr_id = start_id
                    for _, row in imported_df.iterrows():
                        t_sym = str(
                            row.get("Ticker", row.get("SYMBOL", ""))
                        ).strip().upper()
                        qty = float(row.get("Quantity", row.get("QTY", 1.0)))
                        b_pr = float(row.get("Buy Price", row.get("AVG PRICE", 0.0)))
                        s_pr = float(row.get("Sell Price", row.get("LTP", 0.0)))

                        processed_rows.append({
                            "ID": curr_id,
                            "Date": str(row.get("Date", datetime.date.today())),
                            "Ticker": t_sym,
                            "Market": str(row.get("Market", "India (INR)")),
                            "Type": str(row.get("Type", "Buy/Long")),
                            "Quantity": qty,
                            "Buy Price": b_pr,
                            "Sell Price": s_pr,
                            "Status": str(row.get("Status", "Active")),
                        })
                        curr_id += 1

                    new_import_df = pd.DataFrame(processed_rows)
                    combined_df = pd.concat([new_import_df, raw_df], ignore_index=True)
                    save_data(combined_df)
                    st.success(
                        f"Successfully imported {len(new_import_df)} trades from file!"
                    )
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading file: {e}")

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
        st.subheader("📋 Active & Cancelled Broker Ledger")
        st.markdown(
            "💡 *Tip: You can change the **Status** column directly in the table"
            " below between **Active** and **Cancelled**. Click **'Save Status"
            " Changes'** when done!*"
        )

        editor_display_df = display_df[[
            "ID",
            "Symbol",
            "Action",
            "Qty",
            "Avg Price",
            "LTP",
            "Status",
            "Investment Value",
            "Current Value",
            "Total P&L",
            "Total P&L %",
            "Raw P&L %",
        ]].copy()

        def color_pnl_pct(val):
            if isinstance(val, (int, float)):
                num = val
            else:
                cleaned = str(val).replace('%', '').replace(',', '').strip()
                try:
                    num = float(cleaned)
                except ValueError:
                    num = 0.0
            color = '#00FF66' if num >= 0 else '#FF3333'
            return f'color: {color}'

        styled_table = editor_display_df.style.map(
            color_pnl_pct, subset=["Total P&L %", "Raw P&L %"]
        ).format({"Raw P&L %": "{:.2f}%"})

        edited_table = st.data_editor(
            styled_table,
            column_config={
                "Status": st.column_config.SelectboxColumn(
                    "Status",
                    help="Select trade status",
                    options=["Active", "Cancelled"],
                    required=True,
                ),
                "ID": st.column_config.NumberColumn("ID", disabled=True),
                "Raw P&L %": None,
            },
            disabled=[
                "ID",
                "Symbol",
                "Action",
                "Qty",
                "Avg Price",
                "LTP",
                "Investment Value",
                "Current Value",
                "Total P&L",
                "Total P&L %",
            ],
            hide_index=True,
            use_container_width=True,
        )

        if st.button("💾 Save Status Changes"):
            raw_df = load_data()
            status_map = dict(zip(editor_display_df["ID"], editor_display_df["Status"]))
            raw_df["Status"] = raw_df["ID"].map(status_map).fillna(raw_df["Status"])
            save_data(raw_df)
            st.success("Trade statuses updated successfully!")
            st.rerun()

    with tab2:
        st.subheader("📊 Individual Market Breakdown Charts")
        chart_col1, chart_col2, chart_col3 = st.columns(3)

        with chart_col1:
            st.markdown("##### 🇮🇳 India Allocation")
            if not india_df.empty:
                active_ind = india_df[india_df["Status"] == "Active"]
                if not active_ind.empty:
                    fig_ind = px.pie(
                        active_ind, names="Symbol", values="Raw Curr", hole=0.3
                    )
                    st.plotly_chart(fig_ind, use_container_width=True)
                else:
                    st.info("No active India trades.")
            else:
                st.info("No India trades.")

        with chart_col2:
            st.markdown("##### 🇺🇸 USA Allocation")
            if not usa_df.empty:
                active_usa = usa_df[usa_df["Status"] == "Active"]
                if not active_usa.empty:
                    fig_usa = px.pie(
                        active_usa, names="Symbol", values="Raw Curr", hole=0.3
                    )
                    st.plotly_chart(fig_usa, use_container_width=True)
                else:
                    st.info("No active USA trades.")
            else:
                st.info("No USA trades.")

        with chart_col3:
            st.markdown("##### 🇦🇺 CFD Allocation")
            if not cfd_df.empty:
                active_cfd = cfd_df[cfd_df["Status"] == "Active"]
                if not active_cfd.empty:
                    fig_cfd = px.pie(
                        active_cfd, names="Symbol", values="Raw Curr", hole=0.3
                    )
                    st.plotly_chart(fig_cfd, use_container_width=True)
                else:
                    st.info("No active CFD trades.")
            else:
                st.info("No CFD trades.")

        st.markdown("---")
        st.subheader("Overall Profit / Loss per Symbol")
        
        active_bar_df = display_df[display_df["Status"] == "Active"]
        fig_bar = px.bar(
            active_bar_df,
            x="Symbol",
            y="Raw P&L",
            color="Raw P&L",
            color_continuous_scale=["red", "green"],
            labels={"Raw P&L": "Profit/Loss ($)"},
            hover_data=["Qty", "Investment Value", "Current Value", "Total P&L %"]
        )
        fig_bar.update_traces(
            hovertemplate="<b>%{x}</b><br>Profit/Loss: $%{y:,.2f}<br>Quantity: %{customdata[0]}<br>Investment: %{customdata[1]}<br>Current Value: %{customdata[2]}<br>Return: %{customdata[3]}<extra></extra>"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        # --- POP-OUT WINDOW / MODAL DIALOG CHART INSPECTOR ---
        st.markdown("---")
        st.subheader("🔍 Pop-Out Chart Modal Inspector")
        st.markdown("Click the button below for any active stock to open its chart in a dedicated pop-out modal window:")

        if not active_bar_df.empty:
            # Define modal dialog function using st.dialog
            @st.dialog("📈 Stock Chart Pop-Out Window", width="large")
            def show_stock_modal(ticker_symbol):
                st.subheader(f"Detailed Price History for: {ticker_symbol}")
                tf = st.selectbox("Timeframe", ["1mo", "3mo", "6mo", "1y", "max"], index=2, key=f"modal_tf_{ticker_symbol}")
                
                with st.spinner("Fetching live chart data..."):
                    try:
                        hist_data = yf.Ticker(ticker_symbol).history(period=tf)
                        if not hist_data.empty:
                            fig_modal = px.line(
                                hist_data, 
                                x=hist_data.index, 
                                y="Close", 
                                title=f"{ticker_symbol} Closing Prices",
                                labels={"x": "Date", "Close": "Price"}
                            )
                            fig_modal.update_layout(margin=dict(t=30, b=10, l=10, r=10), height=400)
                            st.plotly_chart(fig_modal, use_container_width=True)
                        else:
                            st.warning(f"No data available for {ticker_symbol}.")
                    except Exception as ex:
                        st.error(f"Error loading chart: {ex}")

            # Render a grid of buttons for quick pop-out modals
            cols_modal = st.columns(min(4, len(active_bar_df)))
            for i, (_, row_item) in enumerate(active_bar_df.iterrows()):
                col_target = cols_modal[i % len(cols_modal)]
                with col_target:
                    if st.button(f"🔍 Open {row_item['CleanTicker']}", key=f"btn_modal_{row_item['ID']}", use_container_width=True):
                        show_stock_modal(row_item['CleanTicker'])

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
        " File'** section above to get started!"
    )

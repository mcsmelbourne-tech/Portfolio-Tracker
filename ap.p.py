with tab1:
    st.subheader("📋 Active & Closed Broker Ledger")

    def color_pl_pct(val):
      try:
        clean_val = float(
            str(val).replace("%", "").replace(",", "").strip()
        )
        color = "green" if clean_val >= 0 else "red"
        return f"color: {color}; font-weight: bold;"
      except Exception:
        return ""

    cols_to_display = [
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
    ]

    target_df = display_df[cols_to_display]
    # Version-safe styling method check (.map for newer pandas, .applymap for older)
    if hasattr(target_df.style, "map"):
      styled_df = target_df.style.map(color_pl_pct, subset=["Total P&L %"])
    else:
      styled_df = target_df.style.applymap(color_pl_pct, subset=["Total P&L %"])

    st.dataframe(styled_df, use_container_width=True)

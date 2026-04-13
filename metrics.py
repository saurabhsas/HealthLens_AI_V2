def get_kpis(df):
    
    return {
        "Total Members": df["MEMBERID"].nunique(),
        "Total Cost": f"${df['PAID'].sum():,.2f}",
        "Avg Cost": f"${df['PAID'].mean():,.2f}",
        "ED Visits": int(df["EDVISITS"].sum()),
        "IP Visits": int(df["IPVISITS"].sum())
    }
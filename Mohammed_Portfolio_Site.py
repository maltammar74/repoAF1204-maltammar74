# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.19.10",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.19.11"
app = marimo.App()


@app.cell
def _(mo):
    mo.md(r"""
    ---
    ## AF1204 Individual Portfolio  |  Mohammed Al Tammar
    College Diploma  |  City St George's, University of London
    """)
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip
    return micropip, mo, pd


@app.cell
def _(pd):
    data_url = (
        "https://gist.githubusercontent.com/DrAYim/"
        "80393243abdbb4bfe3b45fef58e8d3c8/raw/"
        "ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/"
        "sp500_ZScore_AvgCostofDebt.csv"
    )

    df = pd.read_csv(data_url)
    df = df.dropna(subset=["AvgCost_of_Debt", "Z_Score_lag", "Sector_Key", "Market_Cap", "Name", "Ticker"])
    df = df[df["AvgCost_of_Debt"] < 5].copy()
    df["Debt_Cost_Percent"] = df["AvgCost_of_Debt"] * 100
    df["Market_Cap_B"] = df["Market_Cap"] / 1e9

    sector_table = (
        df.groupby("Sector_Key")
        .agg(
            Avg_Debt_Cost=("Debt_Cost_Percent", "mean"),
            Avg_Z_Score=("Z_Score_lag", "mean"),
            Companies=("Name", "nunique")
        )
        .round(2)
        .reset_index()
        .rename(columns={"Sector_Key": "Sector"})
        .sort_values("Avg_Debt_Cost", ascending=False)
    )

    company_table = (
        df.groupby(["Ticker", "Name", "Sector_Key"], as_index=False)
        .agg(
            Avg_Debt_Cost=("Debt_Cost_Percent", "mean"),
            Avg_Z_Score=("Z_Score_lag", "mean"),
            Avg_Market_Cap_B=("Market_Cap_B", "mean")
        )
        .round(2)
        .sort_values("Avg_Market_Cap_B", ascending=False)
    )

    return company_table, df, sector_table


@app.cell
async def _(micropip):
    await micropip.install("plotly")
    import plotly.express as px
    return (px,)


@app.cell
def _(company_table, df, mo, sector_table):
    sector_options = sorted(df["Sector_Key"].unique().tolist())
    sector_select = mo.ui.multiselect(
        options=sector_options,
        value=sector_options[:4],
        label="Select sectors"
    )

    max_cap = int(df["Market_Cap_B"].max())
    cap_slider = mo.ui.slider(
        start=0,
        stop=max_cap if max_cap > 0 else 200,
        step=10,
        value=20,
        label="Minimum market cap ($ billions)"
    )

    company_options = company_table["Ticker"].drop_duplicates().tolist()
    company_select = mo.ui.dropdown(
        options=company_options,
        value=company_options[0],
        label="Choose a company"
    )

    return cap_slider, company_select, sector_options, sector_select


@app.cell
def _(cap_slider, company_select, company_table, df, sector_select, sector_table):
    filtered_df = df[
        (df["Sector_Key"].isin(sector_select.value)) &
        (df["Market_Cap_B"] >= cap_slider.value)
    ].copy()

    filtered_sector = sector_table[sector_table["Sector"].isin(sector_select.value)].copy()
    selected_company = company_table[company_table["Ticker"] == company_select.value].copy()

    obs_count = len(filtered_df)
    company_count = filtered_df["Name"].nunique()
    avg_cost = round(filtered_df["Debt_Cost_Percent"].mean(), 2) if obs_count else 0

    return avg_cost, company_count, filtered_df, filtered_sector, obs_count, selected_company


@app.cell
def _(filtered_df, filtered_sector, obs_count, px, selected_company):
    scatter_fig = px.scatter(
        filtered_df,
        x="Z_Score_lag",
        y="Debt_Cost_Percent",
        color="Sector_Key",
        size="Market_Cap_B",
        hover_name="Name",
        hover_data=["Ticker"],
        title=f"Credit Risk and Borrowing Cost ({obs_count} observations)",
        labels={
            "Z_Score_lag": "Altman Z-Score (lagged)",
            "Debt_Cost_Percent": "Average Cost of Debt (%)",
            "Sector_Key": "Sector"
        },
        template="presentation",
        width=900,
        height=560
    )
    scatter_fig.add_vline(x=1.81, line_dash="dash", line_color="red")
    scatter_fig.add_vline(x=2.99, line_dash="dash", line_color="green")

    bar_fig = px.bar(
        filtered_sector,
        x="Sector",
        y="Avg_Debt_Cost",
        title="Average Cost of Debt by Sector",
        labels={"Avg_Debt_Cost": "Average Cost of Debt (%)"},
        template="presentation"
    )

    company_fig = px.bar(
        selected_company,
        x="Ticker",
        y=["Avg_Debt_Cost", "Avg_Z_Score", "Avg_Market_Cap_B"],
        barmode="group",
        title="Selected Company Snapshot",
        template="presentation",
        labels={"value": "Value", "variable": "Metric"}
    )

    return bar_fig, company_fig, scatter_fig


@app.cell
def _(avg_cost, bar_fig, cap_slider, company_count, company_fig, company_select, mo, scatter_fig, sector_select):
    tab_overview = mo.md(
        """
### Overview

I am Mohammed Al Tammar, a student at City St George's, University of London. 
This portfolio shows how I used Python, pandas, marimo, and Plotly to work with financial data.

**Main skills shown in this project**
- Loading and cleaning data
- Building simple interactive filters
- Creating charts to explain financial risk
- Presenting results in a clear webpage format
        """
    )

    tab_experience = mo.md(
        """
## Education and Experience

**Education**
- College Diploma, City St George's, University of London (2024-2028)
- High School Diploma, Al Bayan Bilingual School, Kuwait (2009-2024)

**Experience**
- Digital Bank Internship, National Bank of Kuwait (2023)
- Internship, National Investments Company (2025)
- Community Service Volunteer, Tanzania (2023)
- Community Service Volunteer, Nepal (2024)

These experiences helped me improve teamwork, responsibility, and interest in finance and business.
        """
    )

    tab_dashboard = mo.vstack([
        mo.md("## Finance Dashboard"),
        mo.callout(mo.md("Use the filters to compare sectors and study the relationship between credit risk and cost of debt."), kind="info"),
        mo.hstack([sector_select, cap_slider], gap=2),
        mo.md(f"**Companies shown:** {company_count}  \\  **Average cost of debt:** {avg_cost:.2f}%"),
        mo.ui.plotly(scatter_fig),
        mo.ui.plotly(bar_fig),
    ])

    tab_company = mo.vstack([
        mo.md("## Company Snapshot"),
        mo.callout(mo.md("This section gives a simple summary for one selected company."), kind="neutral"),
        company_select,
        mo.ui.plotly(company_fig),
    ])

    tab_reflection = mo.md(
        """
## Reflection

This project helped me connect business interest with data tools. 
I learned that charts and filters can make financial information easier to understand.

I am especially interested in using data in banking, investments, and business decision making. 
In the future, I want to improve my skills in financial analysis and practical data work.
        """
    )

    return tab_company, tab_dashboard, tab_experience, tab_overview, tab_reflection


@app.cell
def _(mo, tab_company, tab_dashboard, tab_experience, tab_overview, tab_reflection):
    app_tabs = mo.ui.tabs({
        "Overview": tab_overview,
        "Experience": tab_experience,
        "Finance Dashboard": tab_dashboard,
        "Company Snapshot": tab_company,
        "Reflection": tab_reflection,
    })

    mo.md(
        f"""
# Mohammed Al Tammar
AF1204 Individual Portfolio | City St George's, University of London

---

{app_tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()

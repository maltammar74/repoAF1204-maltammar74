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
    mo.md(
        r"""
        ---
        ## 🎓 Personal Portfolio Webpage
        This webpage presents my profile, experience, and a simple interactive finance dashboard built with marimo.
        """
    )
    return


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip
    return micropip, mo, pd


@app.cell
def _(pd):
    # Load dataset from a raw gist URL, following the Week 4 lecture style
    csv_url = (
        "https://gist.githubusercontent.com/DrAYim/"
        "80393243abdbb4bfe3b45fef58e8d3c8/raw/"
        "ed5cfd9f210bf80cb59a5f420bf8f2b88a9c2dcd/"
        "sp500_ZScore_AvgCostofDebt.csv"
    )

    df_final = pd.read_csv(csv_url)

    # Basic cleaning
    df_final = df_final.dropna(
        subset=["AvgCost_of_Debt", "Z_Score_lag", "Sector_Key", "Market_Cap", "Name", "Ticker"]
    )

    # Filter extreme outliers
    df_final = df_final[df_final["AvgCost_of_Debt"] < 5]

    # Create useful columns
    df_final = df_final.copy()
    df_final["Debt_Cost_Percent"] = df_final["AvgCost_of_Debt"] * 100
    df_final["Market_Cap_B"] = df_final["Market_Cap"] / 1e9

    return (df_final,)


@app.cell
def _(df_final, mo):
    # UI controls
    all_sectors = sorted(df_final["Sector_Key"].unique().tolist())

    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:3],
        label="Filter by Sector",
    )

    max_cap = int(df_final["Market_Cap_B"].max())

    cap_slider = mo.ui.slider(
        start=0,
        stop=max(50, min(max_cap, 300)),
        step=10,
        value=0,
        label="Minimum Market Cap ($ Billions)",
    )

    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    # Reactive filtering
    filtered_portfolio = df_final[
        (df_final["Sector_Key"].isin(sector_dropdown.value))
        & (df_final["Market_Cap_B"] >= cap_slider.value)
    ].copy()

    company_count = filtered_portfolio["Name"].nunique()
    avg_cost = (
        filtered_portfolio["Debt_Cost_Percent"].mean()
        if not filtered_portfolio.empty
        else 0
    )

    return avg_cost, company_count, filtered_portfolio


@app.cell
async def _(micropip):
    await micropip.install("plotly")
    import plotly.express as px
    return (px,)


@app.cell
def _(filtered_portfolio, mo, pd, px):
    # Main scatter plot
    fig_portfolio = px.scatter(
        filtered_portfolio,
        x="Z_Score_lag",
        y="Debt_Cost_Percent",
        color="Sector_Key",
        size="Market_Cap_B",
        hover_name="Name",
        hover_data=["Ticker"],
        title="Cost of Debt vs. Lagged Z-Score",
        labels={
            "Z_Score_lag": "Altman Z-Score (lagged)",
            "Debt_Cost_Percent": "Average Cost of Debt (%)",
            "Sector_Key": "Sector",
        },
        template="presentation",
        width=900,
        height=600,
    )

    fig_portfolio.add_vline(
        x=1.81,
        line_dash="dash",
        line_color="red",
        annotation_text="Distress Threshold",
        annotation_position="top left",
    )

    fig_portfolio.add_vline(
        x=2.99,
        line_dash="dash",
        line_color="green",
        annotation_text="Safe Threshold",
        annotation_position="top right",
    )

    chart_element = mo.ui.plotly(fig_portfolio)

    # Personal map / interests chart
    travel_data = pd.DataFrame(
        {
            "Place": ["Kuwait", "Tanzania", "Nepal", "London"],
            "Lat": [29.3759, -6.3690, 28.3949, 51.5072],
            "Lon": [47.9774, 34.8888, 84.1240, -0.1276],
            "Category": ["Home", "Volunteer", "Volunteer", "Study"],
        }
    )

    fig_map = px.scatter_geo(
        travel_data,
        lat="Lat",
        lon="Lon",
        hover_name="Place",
        color="Category",
        projection="natural earth",
        title="My Journey: Home, Study, and Volunteer Experience",
    )

    fig_map.update_traces(marker=dict(size=12))

    return chart_element, fig_map


@app.cell
def _(avg_cost, company_count, mo):
    metrics_box = mo.md(
        f"""
        ## Dashboard Summary

        | Metric | Value |
        |---|---:|
        | Unique companies shown | **{company_count}** |
        | Average cost of debt | **{avg_cost:.2f}%** |
        """
    )
    return (metrics_box,)


@app.cell
def _(cap_slider, chart_element, fig_map, metrics_box, mo, sector_dropdown):
    # About tab
    tab_about = mo.md(
        """
        ### Mohammed Al Tammar

        **Student | Aspiring Finance and Data Professional**

        I am a student with an interest in finance, business, and data analysis.
        I enjoy learning how data can support better decisions and improve business understanding.
        This portfolio shows some of the skills I learned in data preparation, visualization, and interactive analysis.

        **Education**
        - **College Diploma**, City, University of London (2024–2028)
        - **High School Diploma**, Al Bayan Bilingual School, Kuwait (2009–2024)

        **Skills**
        - Python basics
        - Data preparation
        - Data visualization
        - Interactive dashboards
        - Interest in business and finance
        """
    )

    # Experience tab
    tab_experience = mo.md(
        """
        ## Experience and Activities

        **Internships**
        - **Digital Bank Internship**, National Bank of Kuwait (2023)
        - **Internship**, National Investments Company (2025)

        **Community Service**
        - **Community Service Volunteer**, Tanzania (2023)
        - **Community Service Volunteer**, Nepal (2024)

        These experiences helped me build teamwork, communication, and responsibility.
        They also increased my interest in practical business learning and real-world problem solving.
        """
    )

    # Finance dashboard tab
    tab_dashboard = mo.vstack(
        [
            mo.md("## Interactive Finance Dashboard"),
            mo.callout(
                mo.md(
                    "Use the filters below to explore the relationship between borrowing cost and financial risk."
                ),
                kind="info",
            ),
            mo.hstack([sector_dropdown, cap_slider], justify="center", gap=2),
            metrics_box,
            chart_element,
        ]
    )

    # Reflection tab
    tab_reflection = mo.vstack(
        [
            mo.md("## Personal Interests and Reflection"),
            mo.md(
                """
                I am interested in finance, business, community service, and learning practical skills.

                My volunteer experiences in Tanzania and Nepal helped me understand teamwork, responsibility, and working with different communities.
                I also enjoy exploring how technology and data can be used in business and finance.

                This project helped me understand how data can be cleaned, filtered, and presented in an interactive webpage.
                """
            ),
            mo.ui.plotly(fig_map),
        ]
    )

    return tab_about, tab_dashboard, tab_experience, tab_reflection


@app.cell
def _(mo, tab_about, tab_dashboard, tab_experience, tab_reflection):
    app_tabs = mo.ui.tabs(
        {
            "📄 About Me": tab_about,
            "💼 Experience": tab_experience,
            "📊 Finance Dashboard": tab_dashboard,
            "🌍 Reflection": tab_reflection,
        }
    )

    mo.md(
        f"""
        # **Mohammed Al Tammar**
        ---
        {app_tabs}
        """
    )
    return


if __name__ == "__main__":
    app.run()
"""AgriCalc: Agriculture Data Analyzer.

A small Streamlit application for cleaning agricultural CSV data,
visualizing treatment responses, and running one-way ANOVA + Tukey HSD.
"""

import re

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

REQUIRED_COLUMNS = ["Treatment", "Seeds_Sown", "Seeds_Germinated", "Yield_g"]
NUMERIC_COLUMNS = ["Seeds_Sown", "Seeds_Germinated", "Yield_g"]


def calculate_germination(seeds_sown, seeds_germinated):
    """Return germination percentage, or NaN for invalid input."""
    try:
        sown = float(seeds_sown)
        germinated = float(seeds_germinated)
    except (TypeError, ValueError):
        return np.nan
    if sown <= 0 or germinated < 0:
        return np.nan
    return germinated / sown * 100


def clean_dataset(dataframe):
    """Validate and prepare an agricultural dataset for analysis."""
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("dataframe must be a pandas DataFrame")

    missing = [column for column in REQUIRED_COLUMNS if column not in dataframe.columns]
    if missing:
        raise ValueError("Missing required column(s): " + ", ".join(missing))

    df = dataframe.copy()
    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df["Treatment"] = df["Treatment"].astype("string").str.strip()
    df = df.dropna(subset=REQUIRED_COLUMNS).copy()
    df = df[df["Treatment"].ne("")]
    df = df[df["Seeds_Sown"] > 0]
    df = df[df["Seeds_Germinated"] >= 0]
    df = df[df["Seeds_Germinated"] <= df["Seeds_Sown"]]

    df["Treatment_Group"] = df["Treatment"].map(
        lambda value: re.split(r"\s*\|\s*", str(value), maxsplit=1)[0].strip()
    )
    df["Germination_%"] = [
        calculate_germination(sown, germinated)
        for sown, germinated in zip(df["Seeds_Sown"], df["Seeds_Germinated"])
    ]
    return df.reset_index(drop=True)


def treatment_summary(dataframe, response="Yield_g"):
    """Return n, mean, SD, and SE for each treatment group."""
    if response not in dataframe.columns:
        raise ValueError(f"Unknown response variable: {response}")
    if "Treatment_Group" not in dataframe.columns:
        raise ValueError("Treatment_Group column is required")

    values = dataframe[["Treatment_Group", response]].copy()
    values[response] = pd.to_numeric(values[response], errors="coerce")
    values = values.dropna()
    summary = (
        values.groupby("Treatment_Group")[response]
        .agg(["count", "mean", "std"])
        .reset_index()
    )
    summary["SE"] = summary["std"].fillna(0) / np.sqrt(summary["count"])
    return summary.rename(
        columns={"count": "n", "mean": "Mean", "std": "SD"}
    )


def run_anova(dataframe, response="Yield_g", alpha=0.05):
    """Run one-way ANOVA and Tukey HSD for treatment groups."""
    if response not in dataframe.columns:
        raise ValueError(f"Unknown response variable: {response}")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")

    groups = []
    names = []
    for name, group in dataframe.groupby("Treatment_Group"):
        values = pd.to_numeric(group[response], errors="coerce").dropna().to_numpy()
        if len(values) >= 2:
            names.append(str(name))
            groups.append(values)

    if len(groups) < 2:
        raise ValueError(
            "At least two treatment groups with two or more observations are required."
        )

    f_stat, p_value = stats.f_oneway(*groups)
    values = np.concatenate(groups)
    labels = np.concatenate(
        [np.repeat(name, len(group_values)) for name, group_values in zip(names, groups)]
    )
    tukey = pairwise_tukeyhsd(values, labels, alpha=alpha)
    table = pd.DataFrame(
        tukey._results_table.data[1:], columns=tukey._results_table.data[0]
    )
    return f_stat, p_value, table.rename(
        columns={
            "group1": "Treatment 1",
            "group2": "Treatment 2",
            "meandiff": "Mean difference",
            "p-adj": "Adjusted p",
            "lower": "Lower CI",
            "upper": "Upper CI",
            "reject": "Significant",
        }
    )


def significance_letters(dataframe, response="Yield_g", alpha=0.05):
    """Create compact letters from Tukey non-significant comparisons."""
    summary = treatment_summary(dataframe, response)
    names = summary["Treatment_Group"].tolist()
    if len(names) == 1:
        return {names[0]: "a"}

    _, _, tukey = run_anova(dataframe, response, alpha)
    means = dict(zip(summary["Treatment_Group"], summary["Mean"]))
    ordered = sorted(names, key=lambda name: means[name], reverse=True)

    nonsignificant = {name: set() for name in names}
    for _, row in tukey.iterrows():
        first = str(row["Treatment 1"])
        second = str(row["Treatment 2"])
        if not bool(row["Significant"]):
            nonsignificant[first].add(second)
            nonsignificant[second].add(first)

    # Greedily build groups in descending mean order. Every member of a
    # letter group must be mutually non-significantly different from the new
    # member according to Tukey HSD.
    letter_groups = []
    assignments = {name: [] for name in ordered}
    for name in ordered:
        for index, members in enumerate(letter_groups):
            if all(member == name or member in nonsignificant[name] for member in members):
                members.append(name)
                assignments[name].append(index)
        if not assignments[name]:
            letter_groups.append([name])
            assignments[name].append(len(letter_groups) - 1)

    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    letters = {}
    for name in ordered:
        labels = []
        for index in assignments[name]:
            labels.append(alphabet[index] if index < 26 else f"L{index + 1}")
        letters[name] = "".join(labels)
    return letters


def build_mean_error_figure(dataframe, response="Yield_g", error="SE", alpha=0.05):
    """Build a horizontal treatment-mean chart with error bars and letters."""
    if error not in {"SE", "SD"}:
        raise ValueError("error must be 'SE' or 'SD'")

    summary = treatment_summary(dataframe, response)
    letters = significance_letters(dataframe, response, alpha)
    summary["Letter"] = summary["Treatment_Group"].map(letters)
    summary = summary.sort_values("Mean")
    errors = summary[error].fillna(0)

    fig = go.Figure(
        go.Bar(
            x=summary["Mean"],
            y=summary["Treatment_Group"],
            orientation="h",
            marker_color="#65e39b",
            error_x=dict(type="data", array=errors, visible=True),
            hovertemplate="<b>%{y}</b><br>Mean: %{x:.2f}<extra></extra>",
        )
    )

    maximum = float((summary["Mean"] + errors).max())
    offset = max(abs(maximum) * 0.015, 0.1)
    for _, row in summary.iterrows():
        error_value = float(row[error])
        fig.add_annotation(
            x=float(row["Mean"]) + error_value + offset,
            y=row["Treatment_Group"],
            text=f"<b>{row['Letter']}</b>",
            showarrow=False,
            font=dict(color="#f4fbf7", size=15),
        )

    fig.update_layout(
        title=f"{response} — mean ± {error} with Tukey letters",
        xaxis_title=response,
        yaxis_title="",
        height=max(430, 75 * len(summary)),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


def main():
    """Run the AgriCalc Streamlit interface."""
    st.set_page_config(page_title="AgriCalc", page_icon="🌱", layout="wide")
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
        html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
        .stApp{background:radial-gradient(circle at 15% 0%,rgba(67,203,132,.09),transparent 28%),#07110e;color:#edf7f2}
        .block-container{max-width:1440px;padding-top:2.2rem}
        h1,h2,h3{font-family:'Space Grotesk',sans-serif!important}
        .hero-title{font-family:'Space Grotesk',sans-serif;font-size:4rem;font-weight:700;color:#f4fbf7}
        .hero-kicker{color:#65e39b;font-size:.78rem;font-weight:700;letter-spacing:.16em;text-transform:uppercase}
        .hero-sub{color:#93aaa2;font-size:1rem;margin:12px 0 22px;max-width:760px}
        .metric-card{background:linear-gradient(145deg,#0e211b,#0a1714);border:1px solid #1d3b31;border-radius:16px;padding:16px 18px;min-height:105px}
        .metric-label{color:#8fa79e;font-size:.76rem;text-transform:uppercase;letter-spacing:.09em}
        .metric-value{color:#f3faf6;font-family:'Space Grotesk';font-size:1.75rem;font-weight:700;margin-top:4px}
        .metric-note{color:#65e39b;font-size:.75rem}
        [data-testid="stSidebar"]{background:#091914;border-right:1px solid #18332a}
        [data-testid="stFileUploaderDropzone"]{border:1px dashed #2a5948!important;background:#0b1b16!important;border-radius:14px!important}
        .stButton>button,.stDownloadButton>button{border-radius:10px;border:1px solid #2b5e4b;background:#11251f;color:#eaf8f1;font-weight:600}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="hero-kicker">Plant science • statistics • visualization</div>'
        '<div class="hero-title">AgriCalc</div>'
        '<div class="hero-sub">A focused Python workspace for agricultural data analysis.</div>',
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.markdown("### 🌱 AgriCalc")
        uploaded = st.file_uploader("Upload CSV dataset", type=["csv"])
        if uploaded is not None:
            try:
                raw = pd.read_csv(uploaded)
                source = uploaded.name
            except Exception as error:
                st.error(f"Could not read the CSV file: {error}")
                st.stop()
        else:
            raw = pd.DataFrame(
                {
                    "Treatment": ["Control", "Treatment A", "Treatment B", "Treatment C"],
                    "Replicate": [1, 1, 1, 1],
                    "Seeds_Sown": [100] * 4,
                    "Seeds_Germinated": [72, 81, 88, 94],
                    "Yield_g": [42, 49, 55, 61],
                }
            )
            source = "Built-in demo"
        chart = st.selectbox(
            "Visualization",
            [
                "Treatment comparison",
                "Germination vs yield",
                "Replicate distribution",
                "Yield distribution",
            ],
        )
        error = st.selectbox("Error bars", ["SE", "SD"])
        alpha = st.selectbox("Significance level (α)", [0.01, 0.05, 0.10], index=1)
        if st.button("↻ Refresh analysis", use_container_width=True):
            st.rerun()

    try:
        df = clean_dataset(raw)
    except (TypeError, ValueError) as error:
        st.error(str(error))
        st.stop()
    if df.empty:
        st.warning("No valid rows remain after cleaning.")
        st.stop()

    st.caption(f"DATASET · {source}")
    columns = st.columns(4)
    metrics = [
        ("Average germination", f"{df['Germination_%'].mean():.1f}%", "Valid observations"),
        ("Average yield", f"{df['Yield_g'].mean():.1f} g", "Mean Yield_g"),
        ("Highest yield", f"{df['Yield_g'].max():.1f} g", "Observed"),
        ("Treatment groups", str(df["Treatment_Group"].nunique()), "After grouping"),
    ]
    for column, (label, value, note) in zip(columns, metrics):
        column.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Overview", "Visualization", "Statistics", "ANOVA & Tukey", "Data"]
    )

    with tab1:
        summary = treatment_summary(df)
        germination = treatment_summary(df, "Germination_%")[["Treatment_Group", "Mean"]]
        germination = germination.rename(columns={"Mean": "Germination %"})
        st.dataframe(
            summary.merge(germination, on="Treatment_Group").round(3),
            use_container_width=True,
            hide_index=True,
        )

    with tab2:
        if chart == "Treatment comparison":
            st.plotly_chart(
                build_mean_error_figure(df, "Yield_g", error, alpha),
                use_container_width=True,
            )
        elif chart == "Germination vs yield":
            figure = px.scatter(
                df,
                x="Germination_%",
                y="Yield_g",
                color="Treatment_Group",
                hover_data=["Treatment"],
                title="Germination vs Yield",
            )
            st.plotly_chart(figure, use_container_width=True)
        elif chart == "Replicate distribution":
            figure = px.box(
                df,
                x="Treatment_Group",
                y="Yield_g",
                points="all",
                title="Yield distribution",
            )
            st.plotly_chart(figure, use_container_width=True)
        else:
            figure = px.histogram(df, x="Yield_g", nbins=12, title="Yield distribution")
            st.plotly_chart(figure, use_container_width=True)
        st.download_button(
            "Download cleaned dataset",
            df.to_csv(index=False).encode("utf-8"),
            "agric_data_cleaned.csv",
            "text/csv",
        )

    with tab3:
        numeric = df.select_dtypes(include=np.number).columns.tolist()
        chosen = st.multiselect(
            "Variables",
            numeric,
            default=[
                variable
                for variable in ["Seeds_Germinated", "Germination_%", "Yield_g"]
                if variable in numeric
            ],
        )
        if chosen:
            st.dataframe(df[chosen].describe().T.round(3), use_container_width=True)
        correlation_columns = [column for column in numeric if column != "Replicate"]
        if len(correlation_columns) >= 2:
            st.plotly_chart(
                px.imshow(
                    df[correlation_columns].corr().round(2),
                    text_auto=True,
                    title="Correlation matrix",
                ),
                use_container_width=True,
            )

    with tab4:
        response = st.selectbox(
            "Response variable", ["Yield_g", "Germination_%", "Seeds_Germinated"]
        )
        try:
            f_stat, p_value, tukey = run_anova(df, response, alpha)
            letters = significance_letters(df, response, alpha)
            metric_columns = st.columns(3)
            metric_columns[0].metric("F statistic", f"{f_stat:.3f}")
            metric_columns[1].metric("ANOVA p-value", f"{p_value:.5f}")
            metric_columns[2].metric("Alpha", f"{alpha:.2f}")
            if p_value < alpha:
                st.success("The overall ANOVA p-value is below the selected alpha level.")
            else:
                st.info("The overall ANOVA p-value is not below the selected alpha level.")

            summary = treatment_summary(df, response)
            summary["Letter"] = summary["Treatment_Group"].map(letters)
            st.dataframe(summary.round(4), use_container_width=True, hide_index=True)
            st.plotly_chart(
                build_mean_error_figure(df, response, error, alpha),
                use_container_width=True,
            )
            st.markdown("#### Tukey HSD pairwise comparisons")
            st.dataframe(tukey.round(4), use_container_width=True, hide_index=True)
        except ValueError as error:
            st.warning(str(error))

    with tab5:
        query = st.text_input("Filter treatment")
        if query:
            view = df[df["Treatment"].str.contains(query, case=False, na=False, regex=False)]
        else:
            view = df
        st.dataframe(view, use_container_width=True, height=500, hide_index=True)


if __name__ == "__main__":
    main()

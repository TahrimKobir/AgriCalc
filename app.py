
import io
import re
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd

st.set_page_config(
    page_title="AgriCalc — Agriculture Data Analyzer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root { --bg:#07110e; --panel:#0d1b17; --line:#1d3730; --text:#edf7f2; --muted:#93aaa2; --accent:#65e39b; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:radial-gradient(circle at 15% 0%,rgba(67,203,132,.09),transparent 28%),radial-gradient(circle at 90% 8%,rgba(83,157,255,.05),transparent 22%),var(--bg); color:var(--text); }
.block-container { max-width:1440px; padding-top:2.2rem; padding-bottom:3rem; }
h1,h2,h3 { font-family:'Space Grotesk',sans-serif !important; letter-spacing:-.02em; }
.hero { padding:8px 0 22px; }
.hero-kicker { color:var(--accent); font-size:.78rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; margin-bottom:8px; }
.hero-title { font-family:'Space Grotesk',sans-serif; font-size:clamp(2.2rem,5vw,4.2rem); line-height:.98; font-weight:700; margin:0; color:#f4fbf7; }
.hero-sub { color:var(--muted); font-size:1rem; margin-top:14px; max-width:760px; }
.metric-card { background:linear-gradient(145deg,#0e211b,#0a1714); border:1px solid #1d3b31; border-radius:16px; padding:16px 18px; min-height:105px; }
.metric-label { color:#8fa79e; font-size:.76rem; text-transform:uppercase; letter-spacing:.09em; }
.metric-value { color:#f3faf6; font-family:'Space Grotesk',sans-serif; font-size:1.75rem; font-weight:700; margin-top:4px; }
.metric-note { color:var(--accent); font-size:.75rem; margin-top:3px; }
[data-testid="stSidebar"] { background:#091914; border-right:1px solid #18332a; }
[data-testid="stSidebar"] * { color:#dcebe5; }
[data-testid="stFileUploaderDropzone"] { border:1px dashed #2a5948 !important; background:#0b1b16 !important; border-radius:14px !important; }
.stButton > button, .stDownloadButton > button { border-radius:10px; border:1px solid #2b5e4b; background:#11251f; color:#eaf8f1; font-weight:600; min-height:42px; }
.stButton > button:hover, .stDownloadButton > button:hover { border-color:var(--accent); color:var(--accent); }
div[data-baseweb="select"] > div { background:#0c1a16; border-color:#25493d; border-radius:10px; }
.stTabs [data-baseweb="tab-list"] { gap:6px; background:#0a1713; padding:6px; border-radius:12px; }
.stTabs [data-baseweb="tab"] { border-radius:9px; }
.stTabs [aria-selected="true"] { background:#173328; color:var(--accent); }
.small { color:var(--muted); font-size:.82rem; }
.badge { display:inline-block; padding:5px 9px; border-radius:999px; background:#123125; color:var(--accent); border:1px solid #285540; font-size:.73rem; font-weight:700; }
.footer { margin-top:40px; color:#647b73; font-size:.75rem; text-align:center; }
</style>
""", unsafe_allow_html=True)

REQUIRED = ["Treatment", "Seeds_Sown", "Seeds_Germinated", "Yield_g"]
DEMO = pd.DataFrame({
    "Treatment":["Control","Hydropriming","Nano-Zn 50 ppm","Nano-Zn 100 ppm"],
    "Replicate":[1,1,1,1],
    "Seeds_Sown":[100,100,100,100],
    "Seeds_Germinated":[72,81,88,94],
    "Yield_g":[42,49,55,61],
})

def treatment_group(value):
    return re.split(r"\s*\|\s*", str(value))[0].strip()

def prepare(df):
    out = df.copy()
    for col in ["Seeds_Sown","Seeds_Germinated","Yield_g"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out = out.dropna(subset=["Treatment","Seeds_Sown","Seeds_Germinated","Yield_g"]).copy()
    out["Treatment_Group"] = out["Treatment"].map(treatment_group)
    out["Germination_%"] = np.where(out["Seeds_Sown"] > 0, out["Seeds_Germinated"]/out["Seeds_Sown"]*100, np.nan)
    return out

def fig_layout(fig, height=430):
    fig.update_layout(
        height=height, template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)", font=dict(family="DM Sans",color="#dfece7"),
        margin=dict(l=12,r=12,t=58,b=25),
        hoverlabel=dict(bgcolor="#10221d",font_color="#eff8f3"),
        legend=dict(bgcolor="rgba(0,0,0,0)",orientation="h",y=1.05,x=0),
    )
    fig.update_xaxes(gridcolor="#1a3029",zeroline=False,linecolor="#28473d")
    fig.update_yaxes(gridcolor="#1a3029",zeroline=False,linecolor="#28473d")
    return fig

def significance_letters(groups, alpha=0.05):
    """
    Compact letter display from Tukey HSD adjusted p-values.
    Treatments sharing a letter are not significantly different at alpha.
    """
    names = list(groups.keys())
    if len(names) < 2:
        return {names[0]:"a"} if names else {}

    values, labels = [], []
    for name, arr in groups.items():
        arr = np.asarray(arr, dtype=float)
        values.extend(arr.tolist())
        labels.extend([name] * len(arr))

    if len(set(labels)) < 2:
        return {names[0]:"a"}

    tukey = pairwise_tukeyhsd(np.asarray(values), np.asarray(labels), alpha=alpha)
    means = {k: float(np.mean(v)) for k,v in groups.items()}
    ordered = sorted(names, key=lambda x: means[x], reverse=True)

    # Build non-significance graph.
    nonsig = {a:set() for a in names}
    for a,b,reject in zip(tukey._multicomp.pairindices[0], tukey._multicomp.pairindices[1], tukey.reject):
        n1 = tukey._multicomp.groupsunique[a]
        n2 = tukey._multicomp.groupsunique[b]
        if not bool(reject):
            nonsig[n1].add(n2)
            nonsig[n2].add(n1)

    # Greedy compact-letter display. This gives a useful standard CLD
    # for the common agricultural case and keeps the chart readable.
    letters = []
    assignment = {n: [] for n in ordered}
    for n in ordered:
        placed = False
        for letter_idx, members in enumerate(letters):
            if all((m == n or m in nonsig[n]) for m in members):
                members.append(n)
                assignment[n].append(letter_idx)
                placed = True
                break
        if not placed:
            letters.append([n])
            assignment[n].append(len(letters)-1)

    # Second pass can add a treatment to a later compatible group,
    # improving compactness when intermediate treatments overlap.
    changed = True
    while changed:
        changed = False
        for n in ordered:
            for idx, members in enumerate(letters):
                if n not in members and all((m == n or m in nonsig[n]) for m in members):
                    if idx not in assignment[n]:
                        members.append(n)
                        assignment[n].append(idx)
                        changed = True

    alphabet = list("abcdefghijklmnopqrstuvwxyz")
    result = {}
    for n in ordered:
        result[n] = "".join(alphabet[i] if i < len(alphabet) else f"L{i+1}" for i in sorted(assignment[n]))
    return result

def run_anova(df, response, alpha=0.05):
    groups = {}
    for name, g in df.groupby("Treatment_Group"):
        vals = pd.to_numeric(g[response], errors="coerce").dropna().values
        if len(vals) >= 2:
            groups[name] = vals

    if len(groups) < 2:
        return None, None, None, groups

    f_stat, p_val = stats.f_oneway(*groups.values())
    tukey = pairwise_tukeyhsd(
        endog=np.concatenate(list(groups.values())),
        groups=np.concatenate([[k]*len(v) for k,v in groups.items()]),
        alpha=alpha,
    )

    tukey_df = pd.DataFrame(
        data=tukey._results_table.data[1:],
        columns=tukey._results_table.data[0]
    )
    tukey_df = tukey_df.rename(columns={
        "group1":"Treatment 1", "group2":"Treatment 2",
        "meandiff":"Mean difference", "p-adj":"Adjusted p",
        "lower":"Lower CI", "upper":"Upper CI", "reject":"Significant"
    })
    tukey_df["Significant"] = tukey_df["Significant"].astype(bool)
    letters = significance_letters(groups, alpha)
    return f_stat, p_val, tukey_df, groups, letters

# Header
st.markdown("""
<div class="hero">
  <div class="hero-kicker">Plant science • statistics • visualization</div>
  <div class="hero-title">AgriCalc</div>
  <div class="hero-sub">A focused workspace for cleaning, exploring, statistically analyzing and visualizing agriculture experiment data.</div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("### 🌱 AgriCalc")
    st.caption("Agriculture Data Analyzer")
    st.divider()
    uploaded = st.file_uploader("Upload CSV dataset", type=["csv"])
    if uploaded is not None:
        raw = pd.read_csv(uploaded)
        source_name = uploaded.name
    else:
        raw = DEMO.copy()
        source_name = "Built-in demo dataset"
    st.divider()
    st.markdown("**Analysis controls**")
    chart_type = st.selectbox(
        "Primary visualization",
        ["Treatment comparison","Germination vs yield","Replicate distribution","Yield distribution"],
    )
    error_bar = st.selectbox("Error bars", ["SE","SD"])
    alpha = st.selectbox("Significance level (α)", [0.01,0.05,0.10], index=1)
    if st.button("↻  Refresh analysis", use_container_width=True):
        st.rerun()
    st.divider()
    st.caption("Expected core columns")
    st.code("Treatment\nSeeds_Sown\nSeeds_Germinated\nYield_g", language="text")
    st.caption("Replicate is optional but recommended.")

missing = [c for c in REQUIRED if c not in raw.columns]
if missing:
    st.error("Missing required column(s): " + ", ".join(missing))
    st.stop()

df = prepare(raw)
if df.empty:
    st.warning("No valid rows remain after cleaning. Check the numeric columns.")
    st.stop()

st.markdown(f'<span class="badge">DATASET · {source_name}</span>', unsafe_allow_html=True)
st.write("")

avg_germ = df["Germination_%"].mean()
avg_yield = df["Yield_g"].mean()
best_row = df.loc[df["Yield_g"].idxmax()]
n_treat = df["Treatment_Group"].nunique()
metrics = [
    ("Average germination",f"{avg_germ:.1f}%","Across valid observations"),
    ("Average yield",f"{avg_yield:.1f} g","Mean Yield_g"),
    ("Highest observed yield",f"{best_row['Yield_g']:.1f} g",str(best_row["Treatment_Group"])),
    ("Treatment groups",f"{n_treat}","After label cleanup"),
]
cols = st.columns(4)
for col,(label,value,note) in zip(cols,metrics):
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>',unsafe_allow_html=True)

st.write("")
tab_overview, tab_viz, tab_stats, tab_anova, tab_quality, tab_data = st.tabs(
    ["Overview","Visualization","Statistics","ANOVA & Tukey","Data quality","Data"]
)

with tab_overview:
    summary = df.groupby("Treatment_Group",as_index=False).agg(
        Observations=("Yield_g","size"),
        Mean_Germination=("Germination_%","mean"),
        Mean_Yield=("Yield_g","mean"),
        SD_Yield=("Yield_g","std")
    ).fillna(0).sort_values("Mean_Yield",ascending=False)
    left,right = st.columns([1.35,1])
    with left:
        st.markdown("### Treatment summary")
        display=summary.copy()
        display["Mean_Germination"]=display["Mean_Germination"].round(1)
        display["Mean_Yield"]=display["Mean_Yield"].round(1)
        display["SD_Yield"]=display["SD_Yield"].round(2)
        display.columns=["Treatment","n","Germination %","Mean yield (g)","SD yield"]
        st.dataframe(display,use_container_width=True,hide_index=True)
    with right:
        top=summary.iloc[0]
        st.markdown("### Quick interpretation")
        st.info(f"{top['Treatment_Group']} has the highest mean yield in this dataset ({top['Mean_Yield']:.1f} g). Use the ANOVA & Tukey tab to determine whether treatment differences are statistically significant.")

with tab_viz:
    st.markdown("### Interactive visualization")
    st.caption("Repeated batches/replicates are aggregated by treatment, so the x-axis stays readable.")
    if chart_type == "Treatment comparison":
        chart_df=df.groupby("Treatment_Group",as_index=False).agg(
            Mean_Yield=("Yield_g","mean"),
            Error=("Yield_g",lambda x: x.std(ddof=1)/np.sqrt(x.count()) if error_bar=="SE" else x.std(ddof=1))
        ).sort_values("Mean_Yield",ascending=True)
        fig=go.Figure()
        fig.add_trace(go.Bar(
            x=chart_df["Mean_Yield"], y=chart_df["Treatment_Group"], orientation="h",
            marker_color="#65e39b",
            error_x=dict(type="data",array=chart_df["Error"].fillna(0),visible=True),
            hovertemplate="<b>%{y}</b><br>Mean: %{x:.2f} g<extra></extra>"
        ))
        fig.update_layout(title=f"Mean yield by treatment ± {error_bar}",xaxis_title="Yield (g)",yaxis_title="")
        fig_layout(fig,470)
        st.plotly_chart(fig,use_container_width=True)
    elif chart_type == "Germination vs yield":
        fig=px.scatter(df,x="Germination_%",y="Yield_g",color="Treatment_Group",hover_data=["Treatment"],title="Germination percentage vs yield",labels={"Germination_%":"Germination (%)","Yield_g":"Yield (g)","Treatment_Group":"Treatment"})
        fig.update_traces(marker=dict(size=10,opacity=.82))
        fig_layout(fig,470)
        st.plotly_chart(fig,use_container_width=True)
    elif chart_type == "Replicate distribution":
        fig=px.box(df,x="Treatment_Group",y="Yield_g",points="all",title="Yield distribution across observations",labels={"Treatment_Group":"Treatment","Yield_g":"Yield (g)"})
        fig.update_traces(marker_color="#65e39b",line_color="#65e39b")
        fig_layout(fig,470); fig.update_xaxes(tickangle=-18)
        st.plotly_chart(fig,use_container_width=True)
    else:
        fig=px.histogram(df,x="Yield_g",nbins=12,title="Yield distribution",labels={"Yield_g":"Yield (g)","count":"Observations"})
        fig.update_traces(marker_color="#65e39b")
        fig_layout(fig,470)
        st.plotly_chart(fig,use_container_width=True)
    st.download_button("Download cleaned dataset",data=df.to_csv(index=False).encode(),file_name="agric_data_cleaned.csv",mime="text/csv")

with tab_stats:
    st.markdown("### Descriptive statistics")
    numeric_cols=df.select_dtypes(include=np.number).columns.tolist()
    chosen=st.multiselect("Variables",numeric_cols,default=[c for c in ["Seeds_Germinated","Germination_%","Yield_g"] if c in numeric_cols])
    if chosen:
        desc=df[chosen].describe().T.rename(columns={"count":"n","mean":"Mean","std":"SD","min":"Min","25%":"Q1","50%":"Median","75%":"Q3","max":"Max"})
        st.dataframe(desc.round(3),use_container_width=True)
    st.markdown("#### Correlation matrix")
    corr_cols=[c for c in numeric_cols if c!="Replicate"]
    if len(corr_cols)>=2:
        corr=df[corr_cols].corr().round(2)
        fig=px.imshow(corr,text_auto=True,aspect="auto",color_continuous_scale=["#10221d","#65e39b"],title="Numeric variable correlation")
        fig_layout(fig,430)
        st.plotly_chart(fig,use_container_width=True)

with tab_anova:
    st.markdown("### ANOVA + Tukey HSD")
    st.caption("One-way ANOVA tests whether treatment means differ overall. Tukey HSD then performs pairwise comparisons while controlling the family-wise error rate.")
    response = st.selectbox("Response variable", ["Yield_g","Germination_%","Seeds_Germinated"])
    result = run_anova(df,response,alpha)
    if len(result)==4:
        f_stat,p_val,tukey_df,groups=result
        letters={}
    else:
        f_stat,p_val,tukey_df,groups,letters=result

    if f_stat is None:
        st.warning("At least two treatment groups with two or more observations each are required.")
    else:
        a,b,c=st.columns(3)
        a.metric("F statistic",f"{f_stat:.3f}")
        b.metric("ANOVA p-value",f"{p_val:.5f}")
        c.metric("α",f"{alpha:.2f}")

        if p_val < alpha:
            st.success(f"ANOVA result: statistically significant treatment effect at α = {alpha:.2f}.")
        else:
            st.info(f"ANOVA result: no statistically significant overall treatment effect at α = {alpha:.2f}.")

        st.markdown("#### Treatment means with significance letters")
        summary=df.groupby("Treatment_Group")[response].agg(["count","mean","std"]).reset_index()
        summary["SE"]=summary["std"]/np.sqrt(summary["count"])
        summary["Letter"]=summary["Treatment_Group"].map(letters).fillna("")
        summary=summary.sort_values("mean",ascending=False)
        table=summary.rename(columns={"Treatment_Group":"Treatment","count":"n","mean":"Mean","std":"SD","SE":"SE"})
        st.dataframe(table[["Treatment","n","Mean","SD","SE","Letter"]].round(4),use_container_width=True,hide_index=True)
        st.caption("Treatments sharing at least one letter are not significantly different according to the Tukey HSD comparison used here.")

        # Publication-style mean ± error chart with letters.
        plot=summary.sort_values("mean",ascending=True)
        fig=go.Figure()
        fig.add_trace(go.Bar(
            x=plot["mean"],y=plot["Treatment_Group"],orientation="h",
            marker_color="#65e39b",
            error_x=dict(type="data",array=(plot["SE"] if error_bar=="SE" else plot["std"]).fillna(0),visible=True),
            hovertemplate="<b>%{y}</b><br>Mean: %{x:.2f}<extra></extra>"
        ))
        maxerr=(plot["SE"] if error_bar=="SE" else plot["std"]).fillna(0)
        maxx=float((plot["mean"]+maxerr).max()) if len(plot) else 1
        for _,row in plot.iterrows():
            err=float(row["SE"] if error_bar=="SE" else row["std"])
            fig.add_annotation(x=float(row["mean"]+err)+maxx*0.015,y=row["Treatment_Group"],text=f"<b>{row['Letter']}</b>",showarrow=False,font=dict(color="#f4fbf7",size=15))
        fig.update_layout(title=f"{response} — mean ± {error_bar} with Tukey letters",xaxis_title=response,yaxis_title="")
        fig_layout(fig,max(430,80*len(plot)))
        st.plotly_chart(fig,use_container_width=True)

        st.markdown("#### Tukey HSD pairwise comparisons")
        st.dataframe(tukey_df.round(4),use_container_width=True,hide_index=True)

with tab_quality:
    st.markdown("### Data quality")
    q1,q2,q3=st.columns(3)
    q1.metric("Rows loaded",f"{len(raw):,}")
    q2.metric("Rows used",f"{len(df):,}")
    q3.metric("Rows excluded",f"{len(raw)-len(df):,}")
    quality=pd.DataFrame({
        "Column":raw.columns,
        "Missing values":[int(raw[c].isna().sum()) for c in raw.columns],
        "Data type":[str(raw[c].dtype) for c in raw.columns],
        "Unique values":[int(raw[c].nunique(dropna=True)) for c in raw.columns],
    })
    st.dataframe(quality,use_container_width=True,hide_index=True)
    invalid={
        "Seeds_Sown ≤ 0":int((df["Seeds_Sown"]<=0).sum()),
        "Seeds_Germinated > Seeds_Sown":int((df["Seeds_Germinated"]>df["Seeds_Sown"]).sum()),
        "Negative yield":int((df["Yield_g"]<0).sum()),
    }
    st.dataframe(pd.DataFrame(list(invalid.items()),columns=["Check","Rows flagged"]),use_container_width=True,hide_index=True)

with tab_data:
    st.markdown("### Dataset explorer")
    search=st.text_input("Filter treatment names",placeholder="e.g. Nano-Zn, Control, N80")
    view=df.copy()
    if search.strip():
        view=view[view["Treatment"].astype(str).str.contains(search.strip(),case=False,na=False)]
    st.caption(f"Showing {len(view):,} of {len(df):,} valid rows")
    st.dataframe(view,use_container_width=True,height=520,hide_index=True)

st.markdown('<div class="footer">AgriCalc · Python · Streamlit · Pandas · NumPy · Plotly · SciPy · Statsmodels · Included datasets are simulated demonstration data, not published experimental results.</div>',unsafe_allow_html=True)

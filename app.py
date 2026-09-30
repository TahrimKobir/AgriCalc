import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- Page setup ----------------
st.set_page_config(
    page_title="AgriCalc | Agriculture Data Analyzer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- Custom CSS ----------------
st.markdown("""
<style>
.stApp {
    background: #f7faf7;
}
[data-testid="stSidebar"] {
    background: #163a2a;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
.hero {
    background: linear-gradient(135deg, #163a2a 0%, #28734b 100%);
    padding: 30px 34px;
    border-radius: 20px;
    color: white;
    margin-bottom: 22px;
}
.hero h1 {
    font-size: 40px;
    margin: 0 0 5px 0;
    font-weight: 800;
}
.hero p {
    margin: 0;
    font-size: 16px;
    opacity: .92;
}
.section-title {
    font-size: 23px;
    font-weight: 750;
    color: #163a2a;
    margin: 25px 0 12px;
}
.metric-card {
    background: white;
    padding: 18px 20px;
    border-radius: 15px;
    border: 1px solid #e0e8e2;
    box-shadow: 0 4px 16px rgba(22,58,42,.06);
}
.metric-label {
    color: #64756a;
    font-size: 13px;
}
.metric-value {
    color: #163a2a;
    font-size: 27px;
    font-weight: 800;
    margin-top: 3px;
}
.info-box {
    background: #edf7f0;
    border-left: 5px solid #28734b;
    padding: 13px 17px;
    border-radius: 9px;
    color: #244a34;
    margin: 14px 0;
}
.footer {
    text-align: center;
    color: #718078;
    font-size: 13px;
    padding: 28px 0 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Header ----------------
st.markdown("""
<div class="hero">
    <h1>🌱 AgriCalc</h1>
    <p>Simple Agriculture Data Analyzer • Python-powered data visualization</p>
</div>
""", unsafe_allow_html=True)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.markdown("## 🌾 AgriCalc")
    st.caption("Agriculture Data Analyzer")
    st.divider()

    st.markdown("### 📂 Upload Dataset")
    uploaded_file = st.file_uploader(
        "Choose a CSV file",
        type=["csv"],
        help="Required columns: Treatment, Seeds_Sown, Seeds_Germinated, Yield_g"
    )

    st.divider()
    st.markdown("### 📊 Chart Settings")
    chart_type = st.selectbox(
        "Choose visualization",
        ["Bar Chart", "Line Chart", "Scatter Plot", "Pie Chart"]
    )

    st.divider()
    st.markdown("### 🧪 Required columns")
    st.code("Treatment\nSeeds_Sown\nSeeds_Germinated\nYield_g")

    st.divider()
    st.caption("Python • Pandas • Matplotlib • Streamlit")

# ---------------- Dataset ----------------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    data_source = uploaded_file.name
else:
    df = pd.DataFrame({
        "Treatment": ["Control", "Treatment A", "Treatment B", "Treatment C"],
        "Seeds_Sown": [100, 100, 100, 100],
        "Seeds_Germinated": [72, 81, 88, 94],
        "Yield_g": [42, 49, 55, 61]
    })
    data_source = "Built-in demo dataset"

required = {"Treatment", "Seeds_Sown", "Seeds_Germinated", "Yield_g"}
missing = required - set(df.columns)

if missing:
    st.error(
        "Missing required columns: " + ", ".join(sorted(missing))
    )
    st.stop()

df["Germination_%"] = (
    df["Seeds_Germinated"] / df["Seeds_Sown"]
) * 100

# ---------------- Metrics ----------------
st.markdown(
    '<div class="section-title">📊 Analysis Overview</div>',
    unsafe_allow_html=True
)

st.markdown(
    f'<div class="info-box">Data source: <b>{data_source}</b> · '
    f'{len(df)} treatment records analyzed automatically using Python.</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

metric_data = [
    ("🌱", "Average Germination", f"{df['Germination_%'].mean():.1f}%"),
    ("🌾", "Average Yield", f"{df['Yield_g'].mean():.1f} g"),
    ("🏆", "Highest Yield", f"{df['Yield_g'].max():.1f} g"),
    ("🔬", "Treatments", str(len(df)))
]

for col, (icon, label, value) in zip([c1, c2, c3, c4], metric_data):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{icon} {label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

best = df.loc[df["Yield_g"].idxmax(), "Treatment"]

st.markdown(
    f'<div class="info-box">🏆 <b>Highest-yielding treatment:</b> {best}</div>',
    unsafe_allow_html=True
)

# ---------------- Dataset table ----------------
st.markdown(
    '<div class="section-title">📋 Dataset</div>',
    unsafe_allow_html=True
)

display_df = df.copy()
display_df["Germination_%"] = display_df["Germination_%"].round(1)

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# ---------------- Visualization ----------------
st.markdown(
    '<div class="section-title">📈 Interactive Visualization</div>',
    unsafe_allow_html=True
)

st.write(f"**Selected chart:** {chart_type}")

fig, ax = plt.subplots(figsize=(10, 5))

if chart_type == "Bar Chart":
    ax.bar(df["Treatment"], df["Yield_g"])
    ax.set_xlabel("Treatment")
    ax.set_ylabel("Yield (g)")
    ax.set_title("Yield Performance by Treatment", fontweight="bold")
    plt.xticks(rotation=15)

elif chart_type == "Line Chart":
    ax.plot(
        df["Treatment"],
        df["Yield_g"],
        marker="o",
        linewidth=2
    )
    ax.set_xlabel("Treatment")
    ax.set_ylabel("Yield (g)")
    ax.set_title("Yield Trend Across Treatments", fontweight="bold")
    plt.xticks(rotation=15)

elif chart_type == "Scatter Plot":
    ax.scatter(
        df["Seeds_Germinated"],
        df["Yield_g"],
        s=90
    )
    ax.set_xlabel("Seeds Germinated")
    ax.set_ylabel("Yield (g)")
    ax.set_title(
        "Relationship Between Germination and Yield",
        fontweight="bold"
    )

elif chart_type == "Pie Chart":
    ax.pie(
        df["Yield_g"],
        labels=df["Treatment"],
        autopct="%1.1f%%",
        startangle=90
    )
    ax.set_title("Yield Distribution by Treatment", fontweight="bold")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()

st.pyplot(fig, use_container_width=True)

# ---------------- Method ----------------
st.markdown(
    '<div class="section-title">⚙️ How AgriCalc Works</div>',
    unsafe_allow_html=True
)

steps = st.columns(4)
items = [
    ("01", "Upload", "Read a CSV dataset with Pandas."),
    ("02", "Calculate", "Calculate germination percentage."),
    ("03", "Analyze", "Generate summary metrics."),
    ("04", "Visualize", "Create multiple chart types.")
]

for col, (num, title, desc) in zip(steps, items):
    with col:
        st.markdown(
            f'<div class="metric-card"><b>{num} · {title}</b><br>'
            f'<span style="color:#64756a;font-size:13px">{desc}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="footer">AgriCalc • Educational portfolio project • '
    'All included sample values are simulated.</div>',
    unsafe_allow_html=True
)

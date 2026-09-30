
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="AgriCalc | Agriculture Data Analyzer",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom styling ----------
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
        padding: 32px 36px;
        border-radius: 22px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(22,58,42,.12);
    }

    .hero h1 {
        font-size: 42px;
        margin: 0 0 6px 0;
        font-weight: 800;
    }

    .hero p {
        margin: 0;
        font-size: 17px;
        opacity: .9;
    }

    .section-title {
        font-size: 24px;
        font-weight: 750;
        color: #163a2a;
        margin: 26px 0 12px 0;
    }

    .metric-card {
        background: white;
        padding: 20px 22px;
        border-radius: 16px;
        border: 1px solid #e1e9e3;
        box-shadow: 0 5px 18px rgba(22,58,42,.06);
    }

    .metric-label {
        color: #64756a;
        font-size: 14px;
        margin-bottom: 5px;
    }

    .metric-value {
        color: #163a2a;
        font-size: 28px;
        font-weight: 800;
    }

    .info-box {
        background: #edf7f0;
        border-left: 5px solid #28734b;
        padding: 14px 18px;
        border-radius: 10px;
        color: #244a34;
        margin: 16px 0;
    }

    div[data-testid="stDataFrame"] {
        border-radius: 14px;
        overflow: hidden;
    }

    .footer {
        text-align: center;
        color: #718078;
        font-size: 13px;
        padding: 30px 0 10px;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown("""
<div class="hero">
    <h1>🌱 AgriCalc</h1>
    <p>Simple Agriculture Data Analyzer • Built with Python</p>
</div>
""", unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🌾 AgriCalc")
    st.caption("Agriculture Data Analyzer")
    st.divider()

    st.markdown("### 📂 Data Input")
    uploaded_file = st.file_uploader(
        "Upload your CSV dataset",
        type=["csv"],
        help="CSV should contain Treatment, Seeds_Sown, Seeds_Germinated and Yield_g."
    )

    st.divider()
    st.markdown("### 🧪 Required columns")
    st.code("Treatment\nSeeds_Sown\nSeeds_Germinated\nYield_g")

    st.divider()
    st.caption("Educational portfolio project")
    st.caption("Python • Pandas • Matplotlib • Streamlit")

# ---------- Data ----------
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    data_source = "Uploaded CSV"
else:
    df = pd.DataFrame({
        "Treatment": ["Control", "Treatment A", "Treatment B", "Treatment C"],
        "Seeds_Sown": [100, 100, 100, 100],
        "Seeds_Germinated": [72, 81, 88, 94],
        "Yield_g": [42, 49, 55, 61]
    })
    data_source = "Demo dataset"

required = {"Treatment", "Seeds_Sown", "Seeds_Germinated", "Yield_g"}
missing = required - set(df.columns)

if missing:
    st.error(f"Missing required columns: {', '.join(sorted(missing))}")
    st.stop()

df["Germination_%"] = (df["Seeds_Germinated"] / df["Seeds_Sown"]) * 100

# ---------- Overview ----------
st.markdown('<div class="section-title">📊 Analysis Overview</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="info-box">Data source: <b>{data_source}</b> · '
    f'{len(df)} treatment records analyzed automatically using Python.</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)

metrics = [
    ("🌱", "Average Germination", f"{df['Germination_%'].mean():.1f}%"),
    ("🌾", "Average Yield", f"{df['Yield_g'].mean():.1f} g"),
    ("🏆", "Highest Yield", f"{df['Yield_g'].max():.1f} g"),
    ("🔬", "Treatments", str(len(df))),
]

for col, (icon, label, value) in zip((c1, c2, c3, c4), metrics):
    with col:
        st.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-label">{icon} {label}</div>'
            f'<div class="metric-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

best_treatment = df.loc[df["Yield_g"].idxmax(), "Treatment"]

st.markdown(
    f'<div class="info-box">🏆 <b>Highest-yielding treatment:</b> {best_treatment}</div>',
    unsafe_allow_html=True
)

# ---------- Dataset ----------
st.markdown('<div class="section-title">📋 Dataset</div>', unsafe_allow_html=True)
display_df = df.copy()
display_df["Germination_%"] = display_df["Germination_%"].round(1)
st.dataframe(display_df, use_container_width=True, hide_index=True)

# ---------- Charts ----------
st.markdown('<div class="section-title">📈 Visual Analysis</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🌱 Germination", "🌾 Yield"])

with tab1:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df["Treatment"], df["Germination_%"])
    ax.set_ylabel("Germination (%)")
    ax.set_xlabel("Treatment")
    ax.set_ylim(0, 100)
    ax.set_title("Seed Germination by Treatment", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

with tab2:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df["Treatment"], df["Yield_g"])
    ax.set_ylabel("Yield (g)")
    ax.set_xlabel("Treatment")
    ax.set_title("Yield Performance by Treatment", fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(fig, use_container_width=True)

# ---------- Method ----------
st.markdown('<div class="section-title">⚙️ How the Tool Works</div>', unsafe_allow_html=True)
steps = st.columns(4)
items = [
    ("01", "Upload", "Read a CSV dataset using Pandas."),
    ("02", "Calculate", "Compute germination percentage."),
    ("03", "Analyze", "Summarize treatment performance."),
    ("04", "Visualize", "Create charts with Matplotlib.")
]
for col, (num, title, desc) in zip(steps, items):
    with col:
        st.markdown(
            f'<div class="metric-card"><b>{num} · {title}</b><br>'
            f'<span style="color:#64756a;font-size:13px">{desc}</span></div>',
            unsafe_allow_html=True
        )

st.markdown(
    '<div class="footer">AgriCalc • Educational portfolio project • '
    'Demo data are simulated for demonstration purposes.</div>',
    unsafe_allow_html=True
)

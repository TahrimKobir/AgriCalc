import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="AgriCalc — Agriculture Data Analyzer",
    page_icon="🌱",
    layout="wide"
)

st.title("🌱 AgriCalc")
st.subheader("Simple Agriculture Data Analyzer")
st.write("A Python-based tool for calculating seed germination and visualizing treatment performance.")

st.sidebar.header("Input Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.DataFrame({
        "Treatment": ["Control", "Treatment A", "Treatment B", "Treatment C"],
        "Seeds_Sown": [100, 100, 100, 100],
        "Seeds_Germinated": [72, 81, 88, 94],
        "Yield_g": [42, 49, 55, 61]
    })

required = {"Treatment", "Seeds_Sown", "Seeds_Germinated", "Yield_g"}

if not required.issubset(df.columns):
    st.error("CSV must contain: Treatment, Seeds_Sown, Seeds_Germinated, Yield_g")
    st.stop()

df["Germination_%"] = (df["Seeds_Germinated"] / df["Seeds_Sown"]) * 100

st.markdown("### 📊 Dataset")
st.dataframe(df, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("Average Germination", f"{df['Germination_%'].mean():.1f}%")
c2.metric("Average Yield", f"{df['Yield_g'].mean():.1f} g")
c3.metric("Best Treatment", str(df.loc[df["Yield_g"].idxmax(), "Treatment"]))

st.markdown("### 🌱 Germination Performance")
fig1, ax1 = plt.subplots()
ax1.bar(df["Treatment"], df["Germination_%"])
ax1.set_ylabel("Germination (%)")
ax1.set_xlabel("Treatment")
ax1.set_ylim(0, 100)
plt.xticks(rotation=20)
st.pyplot(fig1)

st.markdown("### 🌾 Yield Performance")
fig2, ax2 = plt.subplots()
ax2.bar(df["Treatment"], df["Yield_g"])
ax2.set_ylabel("Yield (g)")
ax2.set_xlabel("Treatment")
plt.xticks(rotation=20)
st.pyplot(fig2)

st.markdown("### 🔬 How it works")
st.write("""
1. Python reads the agriculture dataset.
2. The app calculates germination percentage.
3. Summary statistics are generated automatically.
4. Matplotlib creates visualizations.
5. Streamlit provides the interactive web interface.
""")

st.caption("Demo project for educational and portfolio purposes. The included dataset is simulated.")

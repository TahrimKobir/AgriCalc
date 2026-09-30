# 🌱 AgriCalc

A simple Python-based Agriculture Data Analyzer built with **Streamlit, Pandas, and Matplotlib**.

## Features
- Upload your own CSV dataset
- Calculate seed germination percentage
- Display average germination and yield
- Identify the treatment with the highest yield
- Generate simple agriculture charts

## Required CSV columns
- `Treatment`
- `Seeds_Sown`
- `Seeds_Germinated`
- `Yield_g`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment
This project is designed for deployment on Streamlit Community Cloud using a public GitHub repository.

> The included data are simulated demo data and are not presented as real experimental results.

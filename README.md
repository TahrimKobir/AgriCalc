# AgriCalc — Agriculture Data Analyzer

AgriCalc is a small Streamlit application for exploring agriculture experiment datasets.

## Features

- CSV upload
- Automatic treatment-label cleanup for repeated batches/replicates
- Mean yield and germination summaries
- Interactive treatment comparison
- Germination vs. yield scatter plot
- Yield distribution / replicate box plot
- Descriptive statistics
- Correlation matrix
- Basic data-quality checks
- Dataset filtering
- Download cleaned dataset
- Refresh analysis button

## Files

- `app.py` — Streamlit application
- `requirements.txt` — Python dependencies
- `rice_seed_germination.csv`
- `salinity_stress.csv`
- `nitrogen_management.csv`
- `biofertilizer_trial.csv`
- `.gitignore`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy with Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload all project files.
3. Open Streamlit Community Cloud.
4. Select the repository and `app.py`.
5. Deploy.

## Expected core columns

The uploaded CSV should contain:

- `Treatment`
- `Seeds_Sown`
- `Seeds_Germinated`
- `Yield_g`

`Replicate` is optional.

## Important note

The four included CSV files contain simulated demonstration data created for software testing and presentation purposes. They are not real experimental results and should not be presented as published or measured data.

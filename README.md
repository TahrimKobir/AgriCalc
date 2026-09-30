# AgriCalc — Agriculture Data Analyzer

AgriCalc is a Streamlit workspace for cleaning, exploring, visualizing and statistically analyzing agriculture experiment datasets.

## Main features

- CSV upload
- Treatment-wise aggregation of repeated batches/replicates
- Automatic germination percentage calculation
- Interactive treatment comparison
- Mean ± SE or SD error bars
- Germination vs yield scatter plot
- Replicate distribution / box plot
- Descriptive statistics
- Correlation matrix
- One-way ANOVA
- Tukey HSD pairwise comparisons
- Compact significance letters (a, b, c...)
- Publication-style mean ± error chart with significance letters
- Basic data-quality checks
- Treatment search/filter
- Download cleaned dataset
- Refresh analysis button

## Files

- `app.py`
- `requirements.txt`
- `README.md`
- `rice_seed_germination.csv`
- `salinity_stress.csv`
- `nitrogen_management.csv`
- `biofertilizer_trial.csv`
- `.gitignore`

## Required columns

```text
Treatment
Seeds_Sown
Seeds_Germinated
Yield_g
```

`Replicate` is optional but recommended.

## Statistical workflow

1. The app cleans the numeric response columns.
2. Germination percentage is calculated.
3. Observations are grouped by `Treatment_Group`.
4. One-way ANOVA is run for the selected response variable.
5. If multiple groups are available, Tukey HSD performs pairwise comparisons.
6. Compact significance letters summarize which treatment means are not significantly different.
7. Charts can show mean ± SE or mean ± SD.

The significance letters should be interpreted together with the ANOVA and Tukey results; they are not a replacement for the full statistical table.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy

Upload all files to GitHub and deploy `app.py` with Streamlit Community Cloud.

## Important note

The included CSV files contain simulated demonstration data for software testing and presentation. They are not real experimental results and must not be presented as published or measured data.

For real research, the analysis should also consider experimental design, independence, randomization, assumptions, multiple factors, blocking, and the appropriate statistical model.

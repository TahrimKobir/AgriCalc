# AgriCalc — Agriculture Data Analyzer

#### Video Demo: https://youtu.be/yJ-gwAz0Isw?si=Z7-er5T7eNBV3oh5

#### Description:

AgriCalc — Agriculture Data Analyzer is a Python-based application designed to help students and researchers explore agricultural experimental datasets in a simple, interactive workspace. The project focuses on a common agricultural data-analysis workflow in which observations are collected from multiple treatments and replicates, measurements such as germination percentage and yield are summarized, treatment means are compared, and statistical tests are used to investigate whether observed differences are statistically significant.

The application accepts CSV datasets containing four required columns: `Treatment`, `Seeds_Sown`, `Seeds_Germinated`, and `Yield_g`. A `Replicate` column is optional but recommended for experiments containing repeated observations. After a dataset is uploaded, AgriCalc validates the required fields, converts numerical variables into appropriate numeric values, removes unusable observations, standardizes treatment labels, groups repeated treatment labels, and automatically calculates germination percentage.

The application is organized into five main areas: **Overview**, **Visualization**, **Statistics**, **ANOVA & Tukey**, and **Data**.

The **Overview** section provides treatment-level summaries, including sample size, mean germination percentage, mean yield, standard deviation, and standard error. It also displays key summary metrics such as average germination, average yield, highest observed yield, and the number of treatment groups.

The **Visualization** section provides several ways to explore the dataset. Treatment comparison displays treatment means with selectable standard error (SE) or standard deviation (SD) error bars and compact Tukey significance letters. The application also provides a germination-versus-yield scatter plot, a replicate distribution box plot, and a yield distribution histogram. These visualizations allow users to examine treatment differences, relationships between variables, and the distribution of observations.

The **Statistics** section provides descriptive statistics for the numerical variables and a correlation matrix. These tools provide an initial overview of the dataset before inferential statistical analysis.

The main statistical feature is the **ANOVA & Tukey** section. Users can select yield, germination percentage, or number of germinated seeds as the response variable. AgriCalc performs a one-way analysis of variance (ANOVA) using SciPy to test whether there is an overall difference among treatment means. It then performs Tukey's Honestly Significant Difference (HSD) test using Statsmodels for pairwise comparisons. The application also generates compact significance letters from the Tukey comparisons and displays them beside the treatment means, making the pairwise results easier to interpret visually.

The project is intentionally designed as an exploratory agricultural data-analysis tool rather than a replacement for a complete statistical analysis plan. Real experiments may involve factorial treatments, randomized blocks, repeated measurements, nested observations, split-plot designs, or other experimental structures that require statistical models beyond one-way ANOVA. Therefore, results from this application should be interpreted according to the actual experimental design, assumptions, and research objectives.

## Files

- `project.py` — The main Python program. It contains the required `main()` function and the custom top-level functions responsible for germination calculation, dataset cleaning, treatment summaries, ANOVA, Tukey significance letters, and chart generation.
- `test_project.py` — Contains automated pytest tests for the core custom functions in `project.py`.
- `requirements.txt` — Lists the pip-installable Python dependencies required to run the application.
- `rice_seed_germination.csv` — Simulated demonstration dataset for rice seed germination and yield.
- `salinity_stress.csv` — Simulated demonstration dataset representing an agricultural stress experiment.
- `nitrogen_management.csv` — Simulated demonstration dataset representing nitrogen treatment observations.
- `biofertilizer_trial.csv` — Simulated demonstration dataset representing a biofertilizer treatment experiment.
- `agric_demo_anova_tukey.csv` — Simulated demonstration dataset for treatment comparison and ANOVA/Tukey analysis.
- `.gitignore` — Specifies files and directories that should not be committed to the repository.

All included CSV datasets are simulated demonstration data and are not presented as real experimental results.

## Design Choices

I chose **Streamlit** because it allows a Python program to provide an interactive browser-based interface without requiring a separate front-end framework. This keeps the project primarily Python-based while making the application easier to use for researchers and students who may not have extensive programming experience.

**Pandas** is used for data loading, cleaning, transformation, and tabular analysis. **NumPy** supports numerical calculations. **Plotly** provides interactive visualizations. **SciPy** is used for one-way ANOVA, while **Statsmodels** is used for Tukey HSD multiple-comparison analysis. **pytest** is used to test the core functions independently from the user interface.

A major design choice was to separate data processing and statistical calculations into custom functions rather than placing all logic directly inside the Streamlit interface. This makes the program easier to understand, test, and maintain. The visualization functions are also separated from the statistical calculations so that the same analysis results can be presented consistently in the interface.

The treatment comparison chart was designed to show both error bars and compact significance letters. This provides a visual connection between the numerical statistical analysis and the graphical interpretation of treatment differences.

## Testing

The project includes automated tests using `pytest`. The tests cover the core custom functions used for data processing and analysis. Running:

```bash
pytest

# AgriCalc

#### Video Demo: <PASTE-YOUR-YOUTUBE-UNLISTED-URL-HERE>

#### Description:

AgriCalc is a Python-based agriculture data analysis application designed to help students and researchers explore experimental datasets in a simple visual workspace. The project focuses on a common agricultural workflow: a researcher collects observations from several treatments and replicates, calculates measurements such as germination percentage and yield, compares treatment means, and then uses statistical analysis to investigate whether observed differences are meaningful.

The application accepts CSV files containing four required columns: `Treatment`, `Seeds_Sown`, `Seeds_Germinated`, and `Yield_g`. A `Replicate` column is optional but recommended. After a file is uploaded, AgriCalc validates the required fields, converts numeric variables, removes unusable rows, groups repeated treatment labels, and calculates germination percentage automatically.

AgriCalc contains five main areas. The Overview tab summarizes treatment-level sample size, germination percentage, mean yield, standard deviation, and standard error. The Visualization tab provides treatment comparison with selectable SE or SD error bars, a germination-versus-yield scatter plot, a replicate distribution box plot, and a yield histogram. The Statistics tab provides descriptive statistics and a correlation matrix.

The main research feature is the ANOVA & Tukey tab. Users can select yield, germination percentage, or number of germinated seeds as the response variable. The program performs a one-way ANOVA using SciPy to test for an overall treatment effect. It then performs Tukey's Honestly Significant Difference test using Statsmodels for pairwise comparisons. The application also generates compact significance letters and places them beside treatment means. This makes it easier to interpret which treatment groups are different according to the Tukey comparisons. The chart can display mean plus either standard error or standard deviation.

The project is intentionally an exploratory analysis tool rather than a replacement for a complete statistical analysis plan. Real experiments may involve factorial treatments, blocks, repeated measurements, nested observations, or other designs that require models beyond one-way ANOVA. Therefore, real research results should be interpreted according to the actual experimental design and statistical assumptions.

The main program is `project.py`. It contains the required `main` function and the custom top-level functions used for germination calculation, data cleaning, treatment summaries, ANOVA, significance letters, and chart generation. `test_project.py` contains pytest tests for the core custom functions. `requirements.txt` lists the pip-installable dependencies. The CSV files are simulated demonstration datasets and are not real experimental results.

I chose Streamlit because it allows a Python program to provide an interactive browser interface without requiring a separate front-end framework. Pandas handles tabular data, NumPy supports numerical operations, Plotly provides interactive charts, SciPy provides one-way ANOVA, and Statsmodels provides Tukey HSD. This combination keeps the project primarily Python-based while providing a useful research-oriented interface.

To run the project locally, install the dependencies with `pip install -r requirements.txt`, then run `streamlit run project.py`. To execute the automated tests, run `pytest`. The same core functions used by the application are tested independently, which makes the project easier to maintain and demonstrates the testing requirement of the course.

This project was designed to go substantially beyond a simple data display program by combining file validation, data transformation, descriptive analysis, visualization, inferential statistics, multiple-comparison testing, significance-group visualization, and automated unit tests in one application.

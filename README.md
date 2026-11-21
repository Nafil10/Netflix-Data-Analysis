# Netflix Movies and TV Shows — Internship EDA Project

## Project objective
Explore the Netflix titles catalogue to understand content-type composition, additions over time, country and genre representation, and audience rating patterns.

## Technology stack
Python 3.x, Pandas, NumPy, Seaborn, Matplotlib and WordCloud.

## Project structure
```text
Netflix_Internship_Project/
├── data/
│   ├── netflix_titles.csv       # Place the source dataset here
│   └── netflix_cleaned.csv      # Generated after running the script
├── outputs/
│   ├── charts/                  # Generated PNG charts
│   └── *.csv                    # Analysis summary tables
├── src/
│   └── netflix_eda.py
├── requirements.txt
├── PROJECT_REPORT.md
└── README.md
```

## Dataset
Use the public Netflix Movies and TV Shows dataset (`netflix_titles.csv`).
A downloadable copy is available from the TidyTuesday dataset repository:
https://raw.githubusercontent.com/rfordatascience/tidytuesday/main/data/2021/2021-04-20/netflix_titles.csv

Save the file as `data/netflix_titles.csv`. This is a historical dataset snapshot, not a live Netflix catalogue. Cite the dataset source in any submitted report.

## Setup (Windows)
Open Command Prompt in this folder and run:
```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python src/netflix_eda.py
```

## Outputs
The script creates cleaned data, CSV summary tables, and eight visualizations under `outputs/`.
If the dataset is missing, the script displays the expected file location.

## Methodology
1. Load the CSV and inspect its structure and missing values.
2. Remove duplicate rows and fill selected descriptive fields with `Unknown`.
3. Parse `date_added` as datetime; retain genuinely missing dates as `NaT`.
4. Compare Movie and TV Show counts and percentages.
5. Group additions by year and content type.
6. Split and explode multi-valued country and genre fields before counting.
7. Create a WordCloud from title descriptions.
8. Compare rating counts and selected ratings across content types.

## Important interpretation notes
- `date_added` means when a title was added to the dataset's Netflix catalogue, not its original release date.
- A title may list multiple countries and genres. Exploded counts are title-country or title-genre mentions, so they can exceed the number of unique titles.
- `Unknown` is a missing-value label, not an actual director/country/rating.
- This dataset is a historical snapshot; do not describe its counts as Netflix's current catalogue.
- Run the script yourself and use the generated results in your submission. Do not claim results or internship work you have not completed.

"""
Netflix Movies and TV Shows - Exploratory Data Analysis
Run from the project root:
    python src/netflix_eda.py
Input:
    data/netflix_titles.csv
Outputs:
    data/netflix_cleaned.csv
    outputs/*.csv
    outputs/charts/*.png
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

warnings.filterwarnings("ignore", category=FutureWarning)
sns.set_theme(style="whitegrid", context="notebook")

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "netflix_titles.csv"
OUTPUT_DIR = ROOT / "outputs"
CHART_DIR = OUTPUT_DIR / "charts"
OUTPUT_DIR.mkdir(exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(CHART_DIR / filename, dpi=300, bbox_inches="tight")
    plt.close()

def main():
    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATA_FILE}\n"
            "Download netflix_titles.csv and place it inside the data folder."
        )

    # 1. Load and inspect
    df = pd.read_csv(DATA_FILE)
    print("\n--- DATASET PREVIEW ---")
    print(df.head())
    print("\n--- DATASET INFO ---")
    df.info()
    print("\n--- MISSING VALUES BEFORE CLEANING ---")
    print(df.isnull().sum())

    # 2. Clean and prepare
    df = df.drop_duplicates().copy()
    for col in ["director", "cast", "country", "rating", "duration",
                "listed_in", "description"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # Preserve missing dates as NaT; don't invent an addition date.
    df["date_added"] = pd.to_datetime(df["date_added"].astype(str).str.strip(),
                                      errors="coerce")
    df["date_added"] = df["date_added"].where(df["date_added"].notna(), pd.NaT)
    df["year_added"] = df["date_added"].dt.year
    df["month_added"] = df["date_added"].dt.month

    df.to_csv(ROOT / "data" / "netflix_cleaned.csv", index=False)
    print("\n--- MISSING VALUES AFTER CLEANING ---")
    print(df.isnull().sum())

    # 3. Movie vs TV show ratio
    type_counts = df["type"].value_counts()
    type_percent = df["type"].value_counts(normalize=True).mul(100)
    type_summary = pd.DataFrame({
        "content_type": type_counts.index,
        "count": type_counts.values,
        "percentage": type_percent.reindex(type_counts.index).round(2).values
    })
    type_summary.to_csv(OUTPUT_DIR / "content_type_summary.csv", index=False)
    print("\n--- CONTENT TYPE SUMMARY ---")
    print(type_summary)

    plt.figure(figsize=(7, 5))
    sns.barplot(data=type_summary, x="content_type", y="count")
    plt.title("Netflix Catalog: Movies vs TV Shows")
    plt.xlabel("Content type")
    plt.ylabel("Number of titles")
    save_plot("01_content_type_distribution.png")

    # 4. Content additions by year and type
    yearly = (df.dropna(subset=["year_added"])
                .groupby(["year_added", "type"]).size()
                .reset_index(name="titles_added"))
    yearly.to_csv(OUTPUT_DIR / "yearly_additions.csv", index=False)

    plt.figure(figsize=(11, 6))
    sns.lineplot(data=yearly, x="year_added", y="titles_added",
                 hue="type", marker="o")
    plt.title("Netflix Content Additions by Year")
    plt.xlabel("Year added to Netflix")
    plt.ylabel("Number of titles")
    plt.xticks(rotation=45)
    save_plot("02_yearly_additions_line.png")

    plt.figure(figsize=(11, 6))
    sns.barplot(data=yearly, x="year_added", y="titles_added", hue="type")
    plt.title("Yearly Content Additions by Type")
    plt.xlabel("Year added to Netflix")
    plt.ylabel("Number of titles")
    plt.xticks(rotation=45)
    save_plot("03_yearly_additions_bar.png")

    # 5. Countries: split multi-country values and count each title-country pair
    country_rows = df.loc[df["country"].ne("Unknown"), ["show_id", "country"]].copy()
    country_rows["country"] = country_rows["country"].str.split(",")
    country_rows = country_rows.explode("country")
    country_rows["country"] = country_rows["country"].str.strip()
    country_rows = country_rows[country_rows["country"].ne("")]
    top_countries = (country_rows["country"].value_counts()
                     .head(10).rename_axis("country")
                     .reset_index(name="title_count"))
    top_countries.to_csv(OUTPUT_DIR / "top_10_countries.csv", index=False)

    plt.figure(figsize=(11, 6))
    sns.barplot(data=top_countries, x="title_count", y="country")
    plt.title("Top 10 Countries by Netflix Title Count")
    plt.xlabel("Number of title-country entries")
    plt.ylabel("Country")
    save_plot("04_top_10_countries.png")

    # 6. Genres: split and explode to count individual genre mentions
    genre_rows = df.loc[df["listed_in"].ne("Unknown"), ["show_id", "listed_in"]].copy()
    genre_rows["genre"] = genre_rows["listed_in"].str.split(",")
    genre_rows = genre_rows.explode("genre")
    genre_rows["genre"] = genre_rows["genre"].str.strip()
    genre_rows = genre_rows[genre_rows["genre"].ne("")]
    top_genres = (genre_rows["genre"].value_counts()
                  .head(15).rename_axis("genre")
                  .reset_index(name="title_count"))
    top_genres.to_csv(OUTPUT_DIR / "top_genres.csv", index=False)

    plt.figure(figsize=(12, 7))
    sns.barplot(data=top_genres, x="title_count", y="genre")
    plt.title("Most Common Netflix Genres")
    plt.xlabel("Number of title-genre entries")
    plt.ylabel("Genre")
    save_plot("05_top_genres.png")

    # 7. Description word cloud
    description_text = " ".join(
        df.loc[df["description"].ne("Unknown"), "description"].astype(str)
    )
    if description_text.strip():
        stopwords = set(STOPWORDS)
        stopwords.update({"one", "two", "also", "life", "new"})
        cloud = WordCloud(width=1600, height=800, background_color="white",
                          stopwords=stopwords, collocations=False,
                          max_words=200).generate(description_text)
        plt.figure(figsize=(16, 8))
        plt.imshow(cloud, interpolation="bilinear")
        plt.axis("off")
        plt.title("Frequently Used Words in Netflix Descriptions")
        save_plot("06_description_wordcloud.png")

    # 8. Rating distribution, including requested audience categories
    rating_counts = (df["rating"].value_counts()
                     .rename_axis("rating")
                     .reset_index(name="title_count"))
    rating_counts.to_csv(OUTPUT_DIR / "rating_distribution.csv", index=False)

    plt.figure(figsize=(12, 6))
    sns.barplot(data=rating_counts.head(15), x="rating", y="title_count")
    plt.title("Top 15 Netflix Content Ratings")
    plt.xlabel("Rating")
    plt.ylabel("Number of titles")
    plt.xticks(rotation=45)
    save_plot("07_rating_distribution.png")

    focus_ratings = ["TV-MA", "TV-14", "PG-13"]
    focus = df[df["rating"].isin(focus_ratings)]
    rating_by_type = pd.crosstab(focus["rating"], focus["type"])
    rating_by_type.to_csv(OUTPUT_DIR / "selected_ratings_by_type.csv")

    plt.figure(figsize=(8, 5))
    rating_by_type.plot(kind="bar", figsize=(8, 5))
    plt.title("TV-MA, TV-14 and PG-13 by Content Type")
    plt.xlabel("Rating")
    plt.ylabel("Number of titles")
    plt.xticks(rotation=0)
    save_plot("08_selected_ratings_by_type.png")

    # 9. Compact numerical overview (NumPy used for summary statistics)
    valid_years = df["release_year"].dropna().to_numpy()
    metrics = {
        "total_unique_titles": int(df["show_id"].nunique()),
        "rows_after_duplicate_removal": int(len(df)),
        "movies": int((df["type"] == "Movie").sum()),
        "tv_shows": int((df["type"] == "TV Show").sum()),
        "missing_date_added": int(df["date_added"].isna().sum()),
        "average_release_year": float(np.mean(valid_years)) if len(valid_years) else None,
        "median_release_year": float(np.median(valid_years)) if len(valid_years) else None,
    }
    pd.DataFrame([metrics]).to_csv(OUTPUT_DIR / "key_metrics.csv", index=False)

    print("\n--- KEY METRICS ---")
    for key, value in metrics.items():
        print(f"{key}: {value}")
    print(f"\nAnalysis complete. Charts saved in: {CHART_DIR}")

if __name__ == "__main__":
    main()

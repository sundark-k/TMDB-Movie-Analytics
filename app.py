import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from ctypes import cast

st.set_page_config(layout='wide')

import sqlite3 
conn = sqlite3.connect("tmdb_movies.db")

movies = pd.read_csv("movies.csv")
movie_genres = pd.read_csv("movie_genres.csv")

st.title("TMDB Analytics")

with st.sidebar:
    selected = option_menu("Main Menu", ["Home", 'Filters','Dashboard','SQL Queries','Visualization Queries'],
        icons=['house', 'gear', 'graph-up', 'database', 'bar-chart'], menu_icon="cast", default_index=0)

if selected == 'Dashboard':
      c1,c2,c3 = st.columns([0.45,0.1,0.45])

      with c1:

            st.subheader("Movies Genre",divider='violet')
            genres = pd.read_csv("genres.csv")
            movie_genres = pd.read_csv("movie_genres.csv")
            genre_data = pd.merge(  
                movie_genres, genres, on='genre_id'
            )
            genre_count = genre_data.groupby(
                "genre_name"
                 )["movie_id"].nunique()
            fig, ax = plt.subplots(figsize=(8, 6))
            genre_count.sort_values().plot(kind='bar', ax=ax)
            ax.set_xlabel("Genre")
            ax.set_ylabel("Number of Movies")
            st.pyplot(fig)

      with c3:

            st.subheader("Movies Released per Year",divider='rainbow')
            movies["release_date"] = pd.to_datetime(movies["release_date"])
            fig, ax = plt.subplots(figsize=(8, 6))
            movies_per_year = movies.groupby(movies["release_date"].dt.year).size()
            fig, ax = plt.subplots()
            ax.plot(movies_per_year.index, movies_per_year.values)

            ax.set_xlabel("Year")
            ax.set_ylabel("Number of Movies")
            st.pyplot(fig)

if selected == "SQL Queries":

      option = st.selectbox(
      "Select a query",
      ("List all movies in the Action genre released after 2015, showing title and release date.",
      "Find the top 10 highest-grossing movies along with the genre(s) each belongs to",
      "Calculate the average budget and average revenue for each genre, sorted by average revenue descending",   
      "List the top 10 actors who have appeared in the most movies in the dataset.(cast)",
      "Find all directors who have directed more than 3 movies, along with their movie count",
      "List the top 10 most frequently used keywords across all movies",
      "Find movies where the budget was above the overall average budget but the revenue was below the overall average revenue",
      "List all actors who have appeared in a movie directed by a specific director (e.g., Christopher Nolan)",
      "Find the genre with the highest average rating, considering only genres with at least 20 movies",
      "List the top 10 movies with the highest number of keywords tagged to them")
  )
      if option == "List all movies in the Action genre released after 2015, showing title and release date.":
        query = """
        SELECT DISTINCT
        m.title,
        m.release_date
        FROM movies AS m
        JOIN movie_genres AS mg
        ON m.movie_id = mg.movie_id
        JOIN genres AS g
        ON mg.genre_id = g.genre_id
        WHERE g.genre_name = 'Action'
        AND m.release_date >= '2016-01-01'
        ORDER BY m.release_date;
        """
        df = pd.read_sql_query(query, con=conn)
        st.dataframe(df)
        
      elif option == "Find the top 10 highest-grossing movies along with the genre(s) each belongs to":
        query = """
        SELECT m.title, m.revenue, GROUP_CONCAT(g.genre_name) AS genres
        FROM movies AS m
        JOIN movie_genres AS mg ON m.movie_id = mg.movie_id
        JOIN genres AS g ON mg.genre_id = g.genre_id
        GROUP BY m.movie_id
        ORDER BY m.revenue DESC
        LIMIT 10;
        """
        df = pd.read_sql_query(query, con=conn)
        st.dataframe(df)
        
      elif option == "Calculate the average budget and average revenue for each genre, sorted by average revenue descending":
        query = """
            SELECT
              g.genre_name,
                ROUND(AVG(m.budget), 2) AS average_budget,
                  ROUND(AVG(m.revenue), 2) AS average_revenue
                  FROM movies AS m
                  JOIN movie_genres AS mg
                      ON m.movie_id = mg.movie_id
                      JOIN genres AS g
                        ON mg.genre_id = g.genre_id
                        GROUP BY g.genre_name
                        ORDER BY average_revenue DESC;
                        """
        df = pd.read_sql_query(query, con=conn)
        st.dataframe(df)

      elif option == "List the top 10 actors who have appeared in the most movies in the dataset.(cast)":
        query = """
              SELECT
                actor_name,
                COUNT(DISTINCT movie_id) AS movie_count
                FROM cast
                GROUP BY actor_name
                ORDER BY movie_count DESC
                LIMIT 10;
                """
        df = pd.read_sql_query(query, con=conn)
        st.dataframe(df)

      elif option == "Find all directors who have directed more than 3 movies, along with their movie count":
            query = """
              SELECT
                person_name AS director_name,
                  COUNT(DISTINCT movie_id) AS movie_count
                  FROM crew
                  WHERE LOWER(job) = 'director'
                  GROUP BY person_name
                  HAVING COUNT(DISTINCT movie_id) > 3
                  ORDER BY movie_count DESC;
                  """
            df = pd.read_sql_query(query, con=conn)
            st.dataframe(df) 
            
      elif option == "List the top 10 most frequently used keywords across all movies":
            query = """
                SELECT
                  keyword_name,
                    COUNT(DISTINCT movie_id) AS movie_count
                    FROM movie_keywords
                    GROUP BY keyword_name
                    ORDER BY movie_count DESC
                    LIMIT 10;
                    """
            df = pd.read_sql_query(query, con=conn)
            st.dataframe(df)  

      elif option == "Find movies where the budget was above the overall average budget but the revenue was below the overall average revenue":
            query = """
            SELECT m.title, m.budget, m.revenue
            FROM movies AS m
            WHERE m.budget > (SELECT AVG(budget) FROM movies)
            AND m.revenue < (SELECT AVG(revenue) FROM movies);
            """
            df = pd.read_sql_query(query, con=conn)
            st.dataframe(df)

      elif option == "List all actors who have appeared in a movie directed by a specific director (e.g., Christopher Nolan)":
            query = """
            SELECT DISTINCT c.actor_name
            FROM cast AS c
            JOIN crew AS cr ON c.movie_id = cr.movie_id
            WHERE cr.person_name = 'Christopher Nolan' AND LOWER(cr.job) = 'director';
"""
            df = pd.read_sql_query(query, con=conn)
            st.dataframe(df)       

      elif option == "Find the genre with the highest average rating, considering only genres with at least 20 movies":
            query = """
            SELECT g.genre_name, ROUND(AVG(m.vote_average), 2) AS avg_rating, COUNT(m.movie_id) AS movie_count
            FROM movies AS m
            JOIN movie_genres AS mg ON m.movie_id = mg.movie_id
            JOIN genres AS g ON mg.genre_id = g.genre_id
            GROUP BY g.genre_name
            HAVING movie_count >= 20
            ORDER BY avg_rating DESC
            LIMIT 1;
            """
            df = pd.read_sql_query(query, con=conn)
            st.dataframe(df)

      elif option == "List the top 10 movies with the highest number of keywords tagged to them":
            query = """
            SELECT m.title, COUNT(mk.keyword_id) AS keyword_count
            FROM movies AS m
            JOIN movie_keywords AS mk ON m.movie_id = mk.movie_id
            GROUP BY m.movie_id
            ORDER BY keyword_count DESC
            LIMIT 10;
            """
            df = pd.read_sql_query(query, con=conn)
            st.dataframe(df) 

genre_names = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western"
}

movie_genres["genre"] = movie_genres["genre_id"].map(genre_names)

movies.columns = movies.columns.str.strip()
movie_genres.columns = movie_genres.columns.str.strip()

# CONNECT BOTH FILES
data = pd.merge(
        movies,
        movie_genres,
        on="movie_id",
        how="left"
    )

# PREPARE DATA
data["release_date"] = pd.to_datetime(data["release_date"], errors="coerce")
data["year"] = data["release_date"].dt.year

number_columns = [
    "budget", "revenue", "runtime",
    "popularity", "vote_average", "vote_count"
]

for col in number_columns:
    data[col] = pd.to_numeric(data[col], errors="coerce")

# REMOVE DUPLICATES FOR MOVIE ANALYSIS
movie_data = data.drop_duplicates(subset="movie_id").copy()

# SIDEBAR FILTERS

# FILTERS PAGE

selected_year = "All"
selected_genre = "All"
selected_language = "All"
rating = (0.0, 10.0)

if selected == "Filters":

    st.subheader("Filters")

    years = sorted(movie_data["year"].dropna().astype(int).unique())

    selected_year = st.selectbox(
        "Select Year",
        ["All"] + years
    )

    genre_list = sorted(data["genre"].dropna().unique())

    selected_genre = st.selectbox(
        "Select Genre",
        ["All"] + genre_list
    )

    languages = sorted(movie_data["original_language"].dropna().unique())

    selected_language = st.selectbox(
        "Select Language",
        ["All"] + languages
    )

    rating = st.slider(
        "Select Rating",
        0.0, 10.0, (0.0, 10.0)
    )

# APPLY FILTERS

filtered = movie_data.copy()

if selected_year != "All":
    filtered = filtered[filtered["year"] == selected_year]

if selected_genre != "All":
    genre_movies = data[
        data["genre"] == selected_genre
    ]["movie_id"].unique()

    filtered = filtered[
        filtered["movie_id"].isin(genre_movies)
    ]

if selected_language != "All":
    filtered = filtered[
        filtered["original_language"] == selected_language
    ]

filtered = filtered[
    filtered["vote_average"].between(rating[0], rating[1])
]

# SHOW FILTERED MOVIES

if selected == "Filters":

    st.divider()

    st.subheader("Filtered Movie Results")

    st.metric("Movies Found", len(filtered))

    if len(filtered) > 0:

        st.dataframe(
            filtered[
                ["title", "release_date", "original_language",
                 "vote_average", "budget", "revenue"]
            ],
            use_container_width=True
        )

# HOME PAGE DESIGN

if selected == "Home":

    st.subheader("Project Overview")

    st.write(
        "Explore movie trends, ratings and performance "
        "through TMDB Movie Analytics."
    )

    st.divider()

    st.subheader("TMDB Dataset at a Glance")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Movies",
        f"{len(movie_data):,}"
    )

    col2.metric(
        "Average Rating",
        round(movie_data["vote_average"].mean(), 2)
    )

    col3.metric(
        "Movie Genres",
        data["genre"].nunique()
    )

    col4.metric(
        "Languages",
        movie_data["original_language"].nunique()
    )

    st.divider()

    st.subheader("Explore Your Project")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Movie Filters")
        st.write("Filter movies by year, genre, language and rating.")

        st.markdown("### Movie Dashboard")
        st.write("Explore movie statistics and trends.")

    with col2:
        st.markdown("### SQL Analysis")
        st.write("Explore SQL questions and their results.")

        st.markdown("### Data Visualizations")
        st.write("Explore 10 different movie visualizations.")


# DASHBOARD SUMMARY

if selected == "Dashboard":

    st.subheader("Movie Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Movies", len(filtered))

    col2.metric(
        "Average Rating",
        round(filtered["vote_average"].mean(), 2)
    )

    col3.metric(
        "Total Revenue",
        f"${filtered['revenue'].sum():,.0f}"
    )

    st.divider()


if selected == "Visualization Queries":
    st.subheader("Visualization Queries")

  # 1. BUDGET DISTRIBUTION
    st.subheader("1. Movie Budget Distribution")

    fig, ax = plt.subplots()

    budget = filtered[filtered["budget"] > 0]["budget"].dropna()

    ax.hist(budget, bins=20, edgecolor="black")
    ax.set_xlabel("Budget")
    ax.set_ylabel("Number of Movies")
    ax.set_title("Budget Distribution")

    st.pyplot(fig)
    plt.close(fig)

    # 2. RUNTIME DISTRIBUTION
    st.subheader("2. Runtime Distribution")

    fig, ax = plt.subplots()

    runtime = filtered["runtime"].dropna()

    ax.boxplot(runtime)
    ax.set_ylabel("Runtime in Minutes")
    ax.set_title("Movie Runtime Box Plot")

    st.pyplot(fig)
    plt.close(fig)

    # 3. VOTE AVERAGE DISTRIBUTION
    st.subheader("3. Vote Average Distribution")

    fig, ax = plt.subplots()

    ax.hist(
        filtered["vote_average"].dropna(),
        bins=20,
        edgecolor="black"
    )

    ax.set_xlabel("Vote Average")
    ax.set_ylabel("Number of Movies")
    ax.set_title("Rating Distribution")

    st.pyplot(fig)
    plt.close(fig)

    # 4. MOVIE COUNT PER GENRE
    st.subheader("4. Movie Count per Genre")

    genre_data = data[
        data["movie_id"].isin(filtered["movie_id"])
    ]

    genre_count = genre_data.groupby("genre")["movie_id"].nunique()

    fig, ax = plt.subplots()

    genre_count.plot(kind="bar", ax=ax)

    ax.set_xlabel("Genre")
    ax.set_ylabel("Number of Movies")
    ax.set_title("Movie Count by Genre")
    plt.xticks(rotation=45)

    st.pyplot(fig)
    plt.close(fig)

    # 5. BUDGET VS REVENUE
    st.subheader("5. Budget vs Revenue")

    budget_data = filtered[
        (filtered["budget"] > 0) &
        (filtered["revenue"] > 0)
    ].dropna(subset=["budget", "revenue"])

    fig, ax = plt.subplots()

    ax.scatter(
        budget_data["budget"],
        budget_data["revenue"]
    )

    if len(budget_data) > 1:
        x = budget_data["budget"]
        y = budget_data["revenue"]

        slope, intercept = np.polyfit(x, y, 1)

        ax.plot(x, slope * x + intercept)

    ax.set_xlabel("Budget")
    ax.set_ylabel("Revenue")
    ax.set_title("Budget vs Revenue")

    st.pyplot(fig)
    plt.close(fig)

    # 6. POPULARITY VS VOTE COUNT
    st.subheader("6. Popularity vs Vote Count")

    fig, ax = plt.subplots()

    ax.scatter(
        filtered["popularity"],
        filtered["vote_count"]
    )

    ax.set_xlabel("Popularity")
    ax.set_ylabel("Vote Count")
    ax.set_title("Popularity vs Vote Count")

    st.pyplot(fig)
    plt.close(fig)

    # 7. AVERAGE RATING BY GENRE
    st.subheader("7. Average Rating by Genre")

    genre_rating = genre_data.groupby("genre")[
        "vote_average"
    ].mean()

    fig, ax = plt.subplots()

    genre_rating.plot(kind="bar", ax=ax)

    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Rating")
    ax.set_title("Average Rating by Genre")
    plt.xticks(rotation=45)

    st.pyplot(fig)
    plt.close(fig)

    # 8. MOVIES RELEASED PER YEAR
    st.subheader("8. Movies Released Per Year")

    year_count = filtered.groupby("year")["movie_id"].nunique()

    fig, ax = plt.subplots()

    year_count.plot(kind="bar", ax=ax)

    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Movies")
    ax.set_title("Movies Released Per Year")

    st.pyplot(fig)
    plt.close(fig)

    # 9. CORRELATION HEATMAP
    st.subheader("9. Correlation Heatmap")

    correlation = filtered[
        ["budget", "revenue", "runtime",
        "popularity", "vote_average", "vote_count"]
    ].corr()

    fig, ax = plt.subplots(figsize=(9, 6))

    image = ax.imshow(correlation, cmap="coolwarm")

    ax.set_xticks(range(len(correlation.columns)))
    ax.set_yticks(range(len(correlation.columns)))

    ax.set_xticklabels(correlation.columns, rotation=45)
    ax.set_yticklabels(correlation.columns)

    for i in range(len(correlation.columns)):
        for j in range(len(correlation.columns)):
            ax.text(
                j, i,
                round(correlation.iloc[i, j], 2),
                ha="center",
                va="center"
            )

    ax.set_title("Movie Data Correlation")
    fig.colorbar(image)

    st.pyplot(fig)
    plt.close(fig)

    # 10. PAIRPLOT
    st.subheader("10. Budget vs Popularity")

    fig, ax = plt.subplots()

    ax.scatter(
        filtered["budget"],
        filtered["popularity"]
    )

    ax.set_xlabel("Budget")
    ax.set_ylabel("Popularity")
    ax.set_title("Budget vs Popularity")

    st.pyplot(fig)
    plt.close(fig)